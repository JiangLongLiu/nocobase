# 部署进度跟踪

## 项目信息
- **目标主机**: oec-4-fnOS (192.168.123.54)
- **部署路径**: /vol1/docker/mycontainers/nocobase
- **分支**: oec-4-fnOS-deploy
- **启动时间**: 2026-06-12

## 任务进度

| # | 任务 | 状态 | 备注 |
|---|------|------|------|
| 1 | 创建 Git 分支 | DONE | 从 main 创建 oec-4-fnOS-deploy |
| 2 | 创建目录结构 | DONE | config/ scripts/ docs/ |
| 3 | 远程端口检测 | DONE | Web=18080, PG=15432 |
| 4 | 编写部署配置 | DONE | docker-compose.yml + .env 脱敏 |
| 5 | 编写自动化脚本 | DONE | 4 个 Python 脚本 |
| 6 | 上传并启动容器 | DONE | 含资源限制优化 |
| 7 | 部署验证 | DONE | 容器 healthy, API 返回 200 |
| 8 | 编写文档 | DONE | 操作手册 + 部署计划 + README |
| 9 | 提交分支 | PENDING | - |

## 问题记录

### 问题 1: APP_PORT=80 与 nginx 冲突
- **现象**: `Port 80 already in use`
- **原因**: NocoBase 容器内 nginx 监听 80，设置 APP_PORT=80 导致 Node.js 也尝试监听 80
- **解决**: 移除 APP_PORT 环境变量，让容器使用默认内部端口

### 问题 2: 容器内无 curl/wget
- **现象**: 健康检查 `curl -f http://localhost/api/app:getLang` 失败
- **原因**: nocobase/nocobase 镜像基于 node:22-bookworm-slim，未安装 curl
- **解决**: 改用 `CMD-SHELL` + `node -e` 执行 HTTP 请求做健康检查

### 问题 3: 系统崩溃 - CPU/内存耗尽
- **现象**: 系统负载 7.81（4核），内存仅剩 84MB，Swap 几乎满
- **原因**: NocoBase 初始化占 89% CPU，加上其他容器共 18 个同时运行
- **解决**: 
  - NocoBase 限制 1 核 CPU + 512MB 内存
  - PostgreSQL 限制 0.5 核 CPU + 128MB 内存
  - 设置 NODE_OPTIONS: --max-old-space-size=384
  - 部署后系统负载降至 3.79，Swap 恢复至 201MB 空闲

## 最终部署状态

| 容器 | 状态 | CPU | 内存 |
|------|------|-----|------|
| nocobase-app | healthy | 43% | 348MB/512MB |
| nocobase-postgres | healthy | 25% | 20MB/128MB |

- **Web 界面**: http://192.168.123.54:18080/ (可用)
- **API**: http://192.168.123.54:18080/api/app:getLang (200 OK)
