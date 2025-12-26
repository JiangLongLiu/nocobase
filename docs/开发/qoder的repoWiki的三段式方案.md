# .qoder 目录的版本控制三段式方案

## 背景说明

`.qoder/repowiki` 目录是 Qoder AI 为了加速语义检索而创建的项目知识库本地镜像和索引，包含：

- `.qoder/repowiki/zh/content/**/*.md` - 同步的文档和知识内容
- `.qoder/repowiki/zh/meta/repowiki-metadata.json` - 索引、摘要、结构信息

### 核心问题

1. **成本考虑**：生成 `.qoder` 目录需要消耗大量 AI 资源（花钱），不希望重复生成
2. **版本管理**：`.qoder` 本质是缓存/索引，频繁更新会污染 Git 历史
3. **同步需求**：偶尔需要将 `.qoder` 备份到远程，以防本地丢失

### 解决方案

采用**三段式方案**：
- **阶段 A**：日常开发时忽略 `.qoder`，保持分支干净
- **阶段 B**：需要备份时创建专用快照分支
- **阶段 C**：需要恢复时从快照分支获取

---

## 阶段 A：日常开发 - 忽略 .qoder 目录

**目标**：保持 main 和功能分支干净，`.qoder` 仅作为本地缓存

### 步骤 1：在 .gitignore 中添加忽略规则

编辑项目根目录的 `.gitignore` 文件，在末尾添加：

```gitignore
# Qoder AI 缓存和索引
.qoder/
```

### 步骤 2：从 Git 索引中移除 .qoder（保留本地文件）

在项目根目录执行：

```bash
git rm -r --cached .qoder
git commit -m "chore: ignore qoder cache directory"
git push origin main
```

**效果**：
- ✅ 本地磁盘上的 `.qoder` 目录及文件保持不变
- ✅ Git 不再跟踪 `.qoder` 的后续变化
- ✅ `.qoder` 像 `node_modules/` 一样成为本地缓存
- ✅ `git status` 不再显示 `.qoder` 的变更

**注意**：
- 历史提交中已经存在的 `.qoder` 快照不会丢失
- 从此次提交开始，后续开发不再跟踪 `.qoder`

---

## 阶段 B：定期备份 - 创建 .qoder 快照

**时机**：当你觉得当前 `.qoder` 状态良好，想要备份到远程以防丢失时

### 步骤 1：创建专用快照分支

```bash
# 确保 main 是最新的
git checkout main
git pull origin main

# 创建快照分支（命名格式：cache/qoder-YYYYMMDD）
git checkout -b cache/qoder-20251226
```

### 步骤 2：强制添加 .qoder 目录并提交

即使 `.gitignore` 中有 `.qoder/`，使用 `-f` 参数强制添加：

```bash
git add -f .qoder
git commit -m "chore: snapshot qoder cache 2025-12-26"
git push origin cache/qoder-20251226
```

### 步骤 3：返回正常开发分支

```bash
git checkout main
```

**效果**：
- ✅ 快照提交仅存在于 `cache/qoder-YYYYMMDD` 分支
- ✅ main 分支仍然不跟踪 `.qoder`
- ✅ 远程仓库有完整的 `.qoder` 备份
- ✅ 日常开发不受影响

### 分支命名规范

```
cache/qoder-YYYYMMDD
```

示例：
- `cache/qoder-20251226` - 2025年12月26日的快照
- `cache/qoder-20260101` - 2026年1月1日的快照

---

## 阶段 C：恢复缓存 - 从快照获取 .qoder

**场景**：
- 更换电脑
- 误删 `.qoder` 目录
- 需要回退到某个历史版本的知识库

### 方法 1：切换分支 + 手动拷贝（推荐）

#### 步骤 1：切换到快照分支

```bash
git checkout cache/qoder-20251226
```

此时工作区会包含完整的 `.qoder` 目录。

#### 步骤 2：备份 .qoder 目录

```bash
# Windows
xcopy .qoder E:\backup\qoder-20251226 /E /I /H

# Linux/macOS
cp -r .qoder ~/backup/qoder-20251226/
```

或者压缩保存：

```bash
# Windows PowerShell
Compress-Archive -Path .qoder -DestinationPath qoder-backup.zip

# Linux/macOS
tar -czf qoder-backup.tar.gz .qoder
```

#### 步骤 3：回到开发分支

```bash
git checkout main
```

#### 步骤 4：恢复 .qoder 目录

将之前备份的 `.qoder` 目录复制回项目根目录即可。

因为 `.gitignore` 中有 `.qoder/`，所以它只存在于磁盘，不会被 Git 跟踪。

---

### 方法 2：直接从快照分支检出（进阶）

在 main 分支上直接从快照分支拉取 `.qoder`：

```bash
# 在 main 分支执行
git checkout cache/qoder-20251226 -- .qoder
```

这会将 `.qoder` 目录的内容拉到当前工作区，并写入 Git 索引。

为了保持"不跟踪 `.qoder`"的状态，再执行：

```bash
git rm -r --cached .qoder
```

**效果**：
- ✅ 磁盘上有 `.qoder` 目录
- ✅ Git 不跟踪它

---

## 完整工作流示例

### 场景：日常开发流程

```bash
# 1. 在 main 分支正常开发
git checkout main
git pull origin main

# 2. 创建功能分支
git checkout -b feature/new-plugin

# 3. 开发过程中 .qoder 可能会更新
# 但 git status 不会显示 .qoder 的变化

# 4. 提交功能代码
git add packages/plugins/@myorg/new-plugin
git commit -m "feat: add new plugin"
git push origin feature/new-plugin
```

---

### 场景：备份 .qoder 到远程

```bash
# 1. 确保在 main 分支
git checkout main
git pull origin main

# 2. 创建快照分支
git checkout -b cache/qoder-20251226

# 3. 强制添加并提交
git add -f .qoder
git commit -m "chore: snapshot qoder cache 2025-12-26"
git push origin cache/qoder-20251226

# 4. 回到 main 继续开发
git checkout main
```

---

### 场景：从快照恢复 .qoder

```bash
# 方法 1：切换分支拷贝
git checkout cache/qoder-20251226
cp -r .qoder ~/backup/
git checkout main
cp -r ~/backup/.qoder ./

# 方法 2：直接检出
git checkout main
git checkout cache/qoder-20251226 -- .qoder
git rm -r --cached .qoder
```

---

## 最佳实践建议

### 1. 备份频率

建议在以下情况创建快照：

- ✅ 项目知识库有重大更新后
- ✅ 完成重要文档编写后
- ✅ 准备更换开发环境前
- ✅ 每月固定备份一次（如每月1日）

### 2. 快照分支管理

```bash
# 查看所有快照分支
git branch -a | grep cache/qoder

# 删除过期的快照分支（本地）
git branch -D cache/qoder-20251201

# 删除过期的快照分支（远程）
git push origin --delete cache/qoder-20251201
```

### 3. 快照分支命名约定

```
cache/qoder-YYYYMMDD          # 标准快照
cache/qoder-YYYYMMDD-desc     # 带描述的快照
```

示例：
- `cache/qoder-20251226` - 标准日期快照
- `cache/qoder-20251226-major-update` - 重大更新快照
- `cache/qoder-20251231-year-end` - 年末快照

### 4. 与其他分支策略的配合

本方案与现有的 Git 工作流完全兼容：

```
origin/main (官方远程)
    ↓
main (本地) ← 干净，不跟踪 .qoder
    ↓
    ├─ feature/* ← 功能开发分支，不跟踪 .qoder
    └─ cache/qoder-* ← 快照分支，专门跟踪 .qoder
```

---

## 故障排查

### 问题 1：执行 `git rm --cached .qoder` 后仍然看到变更

**原因**：`.gitignore` 没有正确配置或缓存未清理

**解决方案**：

```bash
# 1. 确认 .gitignore 中有 .qoder/
cat .gitignore | grep qoder

# 2. 清理 Git 缓存
git rm -r --cached .qoder
git add .gitignore
git commit -m "chore: properly ignore .qoder directory"
```

---

### 问题 2：快照分支太多，占用空间

**解决方案**：定期清理旧快照

```bash
# 保留最近 3 个月的快照，删除更早的
git branch -a | grep cache/qoder | grep -v "202412\|202501\|202502" | xargs -I {} git branch -D {}
```

---

### 问题 3：切换快照分支时出现冲突

**原因**：工作区有未提交的更改

**解决方案**：

```bash
# 暂存当前更改
git stash

# 切换分支
git checkout cache/qoder-20251226

# 恢复更改
git stash pop
```

---

## 技术原理说明

### 为什么 .qoder 会频繁更新？

1. **元数据时间戳**：每次重建索引会更新时间戳
2. **内部 ID 变化**：索引文件可能包含非幂等的 ID 生成
3. **统计信息更新**：文档数量、结构等统计信息会变化

### 为什么用独立分支而不是标签？

1. **灵活性**：分支可以继续提交、修改
2. **完整性**：包含完整的 `.qoder` 目录树
3. **可恢复性**：可以直接 checkout 查看内容
4. **隔离性**：不影响 main 分支历史

### Git 忽略规则的优先级

```
.gitignore 中的规则 < git add -f 强制添加
```

所以在快照分支中使用 `git add -f` 可以突破 `.gitignore` 的限制。

---

## 附录：快速命令参考

### 日常开发

```bash
# .qoder 会被自动忽略，正常开发即可
git status              # 不会显示 .qoder 的变化
git add .               # 不会添加 .qoder
git commit -m "..."     # 不会提交 .qoder
```

### 创建快照

```bash
git checkout -b cache/qoder-$(date +%Y%m%d)
git add -f .qoder
git commit -m "chore: snapshot qoder cache $(date +%Y-%m-%d)"
git push origin cache/qoder-$(date +%Y%m%d)
git checkout main
```

### 恢复快照

```bash
# 方法 1
git checkout cache/qoder-20251226
cp -r .qoder ~/backup/
git checkout main
cp -r ~/backup/.qoder ./

# 方法 2
git checkout cache/qoder-20251226 -- .qoder
git rm -r --cached .qoder
```

---

## 总结

通过这套三段式方案：

✅ **日常开发干净**：`.qoder` 不污染 Git 历史  
✅ **成本节约**：备份到远程，避免重复生成  
✅ **随时恢复**：快照分支提供完整备份  
✅ **符合规范**：与现有 Git 工作流完美配合  

**核心原则**：
- main 分支保持干净
- 功能分支专注功能开发
- 快照分支专门管理 `.qoder`
- 本地保留 `.qoder`，按需备份

---

**最后更新**: 2025-12-26
