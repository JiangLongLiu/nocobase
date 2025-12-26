# .qoder 的 repoWiki 在新分支开发中的 Git 技巧和操作流程

## 问题场景

在开发新功能时，我们通常会：

1. 从 `main` 分支创建新的功能分支
2. 在新分支上开发时，需要使用 Qoder AI 的辅助（依赖 `.qoder` 目录）
3. 但新分支是从 main 分叉而来，而 main 不跟踪 `.qoder` 目录
4. 如何让新分支能使用 `.qoder`，同时又不污染 Git 历史？

## 核心原理

**.qoder 目录是本地缓存，与 Git 分支无关**

关键认知：
- `.qoder/` 只是工作目录中的一个普通目录
- 通过 `.gitignore` 忽略后，Git 不会跟踪它
- 切换分支时，Git 不会删除未跟踪的文件
- 因此 `.qoder/` 可以在所有分支之间"共享使用"

---

## 方案一：一次恢复，所有分支共享（推荐）

这是最简单、最高效的方式。

### 适用场景

- 长期本地开发
- 不需要频繁删除 `.qoder`
- 多个功能分支会同时开发

### 操作步骤

#### 第一步：在任意分支恢复 .qoder（只需执行一次）

推荐在 `main` 分支执行：

```bash
# 1. 切换到 main 分支
git checkout main
git pull origin main

# 2. 从快照分支恢复 .qoder 目录
# 注意：cache/qoder-YYYYMMDD 需要替换为你实际的快照分支名
git checkout cache/qoder-20251226 -- .qoder

# 3. 确保不被 Git 跟踪（保险起见）
git rm -r --cached .qoder 2>/dev/null || true

# 4. 验证状态
git status
# 应该看到工作目录干净，没有 .qoder 的变更
```

**重要说明**：
- 这个操作只需要执行**一次**
- `.qoder/` 会一直留在你的工作目录中
- 所有分支都能使用它

#### 第二步：创建新功能分支（自动带有 .qoder）

以后创建任何新分支：

```bash
# 1. 从 main 创建新分支
git checkout main
git pull origin main
git checkout -b feature/my-new-feature

# 2. 无需任何额外操作！
# .qoder 已经在工作目录中，可以直接使用
```

#### 验证

```bash
# 查看 .qoder 是否存在
ls -la .qoder/

# 查看 Git 状态（应该不显示 .qoder）
git status

# 开发时 Qoder AI 可以正常使用知识库
```

### 工作流程图

```
main 分支 (有 .qoder 在工作目录)
    ↓
创建 feature/xxx 分支
    ↓
.qoder 自动跟随（不被跟踪）
    ↓
开发 + 提交代码（不包含 .qoder）
    ↓
合并回 main（.qoder 仍在工作目录）
```

---

## 方案二：每个分支临时恢复（按需使用）

适合需要严格控制 `.qoder` 存在的场景。

### 适用场景

- 磁盘空间紧张
- 只在特定分支使用 Qoder AI
- 需要频繁切换不同版本的 .qoder

### 操作步骤

#### 在功能分支上临时恢复 .qoder

```bash
# 1. 创建并切换到新分支
git checkout main
git checkout -b feature/some-feature

# 2. 临时恢复 .qoder
git checkout cache/qoder-20251226 -- .qoder

# 3. 确保不被跟踪
git rm -r --cached .qoder 2>/dev/null || true

# 4. 验证
git status  # 应该干净，没有 .qoder
ls .qoder/  # 目录存在
```

#### 开发完成后清理（可选）

```bash
# 如果不再需要 .qoder，可以删除
rm -rf .qoder

# Windows PowerShell
Remove-Item -Recurse -Force .qoder
```

### 工作流程图

```
创建 feature/xxx 分支（无 .qoder）
    ↓
临时恢复 .qoder
    ↓
开发 + 使用 AI 辅助
    ↓
提交代码（不包含 .qoder）
    ↓
可选：删除 .qoder 释放空间
```

---

## 方案三：手动拷贝（备用方案）

如果 Git 命令不熟悉，也可以用最简单的文件拷贝。

### 操作步骤

#### 第一步：从快照分支导出 .qoder

```bash
# 1. 切换到快照分支
git checkout cache/qoder-20251226

# 2. 压缩备份
# Windows PowerShell
Compress-Archive -Path .qoder -DestinationPath E:\backup\qoder-backup.zip

# Linux/macOS
tar -czf ~/backup/qoder-backup.tar.gz .qoder

# 3. 回到开发分支
git checkout main
```

#### 第二步：在新分支解压使用

```bash
# 1. 创建新分支
git checkout -b feature/new-feature

# 2. 解压 .qoder
# Windows PowerShell
Expand-Archive -Path E:\backup\qoder-backup.zip -DestinationPath .

# Linux/macOS
tar -xzf ~/backup/qoder-backup.tar.gz

# 3. 验证
ls .qoder/
git status  # 应该不显示 .qoder
```

---

## 常见问题与解答

### Q1：为什么切换分支后 .qoder 还在？

**A**：这是正常现象，也是我们想要的效果。

- `.qoder` 被 `.gitignore` 忽略，Git 不管它
- 切换分支时，Git 只会修改被跟踪的文件
- 未跟踪的文件（如 .qoder）会保留在工作目录中

### Q2：会不会不小心把 .qoder 提交上去？

**A**：几乎不可能，因为有多重保护：

1. `.gitignore` 中已经忽略 `.qoder/`
2. `git add .` 不会添加它
3. `git status` 不会显示它
4. 除非使用 `git add -f .qoder` 强制添加

### Q3：如果 .qoder 真的进入了 Git 索引怎么办？

**A**：执行清理命令：

```bash
git rm -r --cached .qoder
git commit -m "chore: remove qoder from git tracking"
```

### Q4：不同分支能用不同版本的 .qoder 吗？

**A**：可以，但需要手动管理：

```bash
# 在分支 A 使用版本 1
git checkout feature/branch-a
git checkout cache/qoder-20251201 -- .qoder

# 在分支 B 使用版本 2
git checkout feature/branch-b
git checkout cache/qoder-20251226 -- .qoder
```

但这样比较麻烦，通常不需要区分版本。

### Q5：.qoder 目录很大，会影响 Git 性能吗？

**A**：不会。

- `.qoder` 不被 Git 跟踪，Git 完全忽略它
- 不会影响 `git status`、`git commit` 等命令的速度
- 只占用本地磁盘空间

### Q6：多人协作时，其他人也需要 .qoder 吗？

**A**：看情况：

- **需要 AI 辅助**：从快照分支恢复一份
- **不需要 AI**：可以不恢复，不影响正常开发
- 每个人的 `.qoder` 是独立的本地缓存

---

## 最佳实践建议

### 1. 建议使用方案一（共享模式）

对大多数开发者来说，方案一最简单高效：
- ✅ 只需恢复一次
- ✅ 所有分支自动可用
- ✅ 不需要记忆额外操作
- ✅ 性能最好

### 2. 定期更新 .qoder 快照

```bash
# 当知识库有重大更新时，创建新快照
git checkout -b cache/qoder-20260115
git add -f .qoder
git commit -m "chore: snapshot qoder cache 2026-01-15"
git push origin cache/qoder-20260115
git checkout main
```

### 3. 在 .gitignore 中确认规则

确保项目根目录的 `.gitignore` 包含：

```gitignore
# Qoder AI 缓存和索引
.qoder/
```

### 4. 团队协作约定

在团队中明确：
- `.qoder` 是可选的本地工具
- 不强制所有人使用
- 需要的人从快照分支恢复
- 绝不提交到功能分支或 main

### 5. 与三段式方案配合

本文档是对"三段式方案"的补充：

- **三段式方案**：管理 .qoder 的备份和恢复
- **本文档**：解决新分支开发中的使用问题

配合使用可以完美解决所有场景。

---

## 完整操作示例

### 场景：第一次设置（推荐流程）

```bash
# 1. 确保 main 分支干净
git checkout main
git pull origin main

# 2. 确认 .gitignore 配置
echo ".qoder/" >> .gitignore
git add .gitignore
git commit -m "chore: ignore qoder cache directory"

# 3. 恢复 .qoder 到工作目录（一次性）
git checkout cache/qoder-20251226 -- .qoder
git rm -r --cached .qoder 2>/dev/null || true

# 4. 验证状态
git status  # 应该干净
ls .qoder/  # 应该存在
```

### 场景：日常开发新功能

```bash
# 1. 创建新分支
git checkout main
git pull origin main
git checkout -b feature/user-authentication

# 2. 开发（.qoder 自动可用，无需额外操作）
# 编写代码...
# 使用 Qoder AI 辅助...

# 3. 提交代码
git add src/
git commit -m "feat: implement user authentication"
git push origin feature/user-authentication

# 4. 验证提交不包含 .qoder
git log --stat  # 应该只看到 src/ 下的文件
```

### 场景：切换到其他分支

```bash
# 直接切换即可
git checkout main
git checkout feature/another-feature

# .qoder 仍然在工作目录中可用
ls .qoder/  # 存在
git status  # 干净
```

---

## 技术原理说明

### Git 对未跟踪文件的处理

Git 在切换分支时的行为：

1. **被跟踪的文件**：
   - 根据目标分支的内容进行更新
   - 可能新增、删除、修改文件

2. **未跟踪的文件**：
   - 完全保留，不做任何修改
   - `.qoder/` 属于这一类

3. **冲突处理**：
   - 如果未跟踪的文件与目标分支有冲突，Git 会阻止切换
   - 但 `.qoder/` 在所有分支都被忽略，不会冲突

### .gitignore 的作用范围

```gitignore
.qoder/
```

这条规则的效果：

- ✅ `git status` 不显示 `.qoder/` 的变化
- ✅ `git add .` 不会添加 `.qoder/`
- ✅ `git commit -a` 不会提交 `.qoder/`
- ❌ `git add -f .qoder` 可以强制添加（快照分支使用）

### git checkout -- 的用途

```bash
git checkout <branch> -- <path>
```

这个命令的作用：
- 从指定分支检出某个路径的文件
- 不切换当前分支
- 适合"借用"其他分支的文件

我们用它来从快照分支获取 `.qoder/`：

```bash
git checkout cache/qoder-20251226 -- .qoder
```

---

## 故障排查

### 问题 1：git status 显示 .qoder 有变化

**可能原因**：
- `.gitignore` 没有配置
- `.qoder` 被添加到了 Git 索引

**解决方案**：

```bash
# 1. 检查 .gitignore
cat .gitignore | grep qoder

# 2. 如果没有，添加规则
echo ".qoder/" >> .gitignore

# 3. 从索引中移除
git rm -r --cached .qoder

# 4. 提交 .gitignore 变更
git add .gitignore
git commit -m "chore: ignore qoder cache directory"
```

---

### 问题 2：切换分支时 .qoder 消失了

**可能原因**：
- `.qoder` 在某个分支被删除了
- 或者从未恢复过

**解决方案**：

```bash
# 重新从快照分支恢复
git checkout cache/qoder-20251226 -- .qoder
git rm -r --cached .qoder 2>/dev/null || true
```

---

### 问题 3：找不到快照分支

**症状**：执行 `git checkout cache/qoder-xxx -- .qoder` 报错

**解决方案**：

```bash
# 1. 查看所有快照分支
git branch -a | grep cache/qoder

# 2. 如果没有，需要先创建快照
git checkout -b cache/qoder-$(date +%Y%m%d)
git add -f .qoder
git commit -m "chore: snapshot qoder cache"
git push origin cache/qoder-$(date +%Y%m%d)

# 3. 如果快照在远程，先拉取
git fetch origin
git branch -a | grep cache/qoder
```

---

### 问题 4：.qoder 内容过期了

**解决方案**：更新到最新快照

```bash
# 1. 查看所有快照，找最新的
git branch -a | grep cache/qoder | sort

# 2. 从最新快照恢复
git checkout cache/qoder-20260115 -- .qoder
```

---

## 与其他 Git 工作流的配合

### 与 main 分支策略配合

```
main (干净，不跟踪 .qoder)
    ├─ .qoder/ (工作目录中存在，但 Git 忽略)
    └─ feature/* (所有分支共享同一个 .qoder/)
```

### 与 rebase 工作流配合

```bash
# 正常 rebase，.qoder 不受影响
git checkout feature/xxx
git rebase main

# .qoder 仍然在工作目录中
ls .qoder/
```

### 与 stash 工作流配合

```bash
# stash 不会包含未跟踪的文件
git stash

# .qoder 仍然在工作目录中
ls .qoder/
```

---

## 总结

### 核心要点

1. **一次恢复，全局可用**：从快照分支恢复 `.qoder` 到工作目录一次即可
2. **Git 不跟踪**：通过 `.gitignore` 确保 Git 忽略 `.qoder/`
3. **分支共享**：切换分支时 `.qoder/` 保持不变，所有分支可用
4. **不污染历史**：`.qoder/` 永远不会进入 Git 提交历史

### 推荐工作流

```
阶段 A：初始化（一次性）
    ↓
从快照分支恢复 .qoder
    ↓
阶段 B：日常开发
    ↓
创建功能分支（自动带 .qoder）
    ↓
开发 + 提交（不含 .qoder）
    ↓
切换分支（.qoder 保持可用）
    ↓
阶段 C：定期维护
    ↓
更新 .qoder 快照（按需）
```

### 记忆口诀

- **恢复一次，全局可用**
- **Git 不管，分支共享**
- **提交代码，忽略缓存**

---

## 参考文档

- [.qoder目录的版本控制三段式方案](./qoder的repoWiki的三段式方案.md) - 完整的 .qoder 管理策略
- [使用源码开发模式](./使用源码开发模式.md) - Git 工作流最佳实践

---

**最后更新**: 2025-12-26
