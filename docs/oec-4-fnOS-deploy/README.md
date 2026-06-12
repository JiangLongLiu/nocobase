# NocoBase on oec-4-fnOS 部署

## 概述

将 NocoBase 部署到 oec-4-fnOS 主机 (192.168.123.54)，使用 Docker Compose 编排 PostgreSQL + NocoBase，并配置资源限制以适配有限的硬件资源（4核/3.8GB）。

**访问地址**: http://192.168.123.54:18080/

## 文档索引

| 文档 | 说明 |
|------|------|
| [部署计划](docs/deployment-plan.md) | 部署架构、端口分配、资源限制策略 |
| [操作手册](docs/operation-manual.md) | 日常运维操作、备份恢复、故障排查 |
| [进度记录](progress.md) | 部署过程进度跟踪和问题记录 |

## 目录结构

```
docs/oec-4-fnOS-deploy/
├── README.md                    # 本文档
├── password.csv                 # 主机凭证
├── progress.md                  # 进度记录
├── config/
│   ├── docker-compose.yml       # 容器编排（已脱敏）
│   └── .env                     # 敏感配置（不提交 Git）
├── scripts/
│   ├── 01-check-ports.py        # 端口可用性检测
│   ├── 02-upload-and-deploy.py  # 上传配置并部署
│   ├── 03-verify.py             # 部署验证
│   └── _quick_redeploy.py       # 快速重部署
└── docs/
    ├── deployment-plan.md       # 部署计划
    └── operation-manual.md      # 操作手册
```

## 快速开始

### 首次部署

1. 确认端口可用：`python scripts/01-check-ports.py`
2. 上传并部署：`python scripts/02-upload-and-deploy.py`
3. 验证部署：`python scripts/03-verify.py`

### 更新配置

1. 编辑 `config/docker-compose.yml`
2. 执行：`python scripts/_quick_redeploy.py`

## 部署信息

| 项目 | 值 |
|------|-----|
| 主机 | oec-4-fnOS (192.168.123.54) |
| NocoBase 端口 | 18080 |
| PostgreSQL 端口 | 15432 |
| 部署路径 | /vol1/docker/mycontainers/nocobase |
| NocoBase CPU 限制 | 1 核 |
| NocoBase 内存限制 | 512MB |
| 分支 | oec-4-fnOS-deploy |
