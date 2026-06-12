# NocoBase on oec-4-fnOS 部署计划

## 目标

将 NocoBase 容器化部署到 oec-4-fnOS 主机（RK3566 ARM64 平台），配置 PostgreSQL 数据库和资源限制，确保在有限资源（4核/3.8GB）下稳定运行。

## 主机信息

| 项目 | 值 |
|------|-----|
| IP | 192.168.123.54 |
| SSH 端口 | 22 |
| 用户 | root |
| 凭证 | password.csv |
| CPU | 4 核 |
| 内存 | 3.8GB |
| 磁盘 | /vol1 (207GB, 可用 175GB) |
| 部署路径 | /vol1/docker/mycontainers/nocobase |

## 部署架构

```
本机 (Windows)
├── docs/oec-4-fnOS-deploy/
│   ├── config/          <-- docker-compose.yml + .env
│   ├── scripts/         <-- 自动化脚本
│   └── docs/            <-- 文档
│
└── SSH/SCP ─────────> oec-4-fnOS (192.168.123.54)
                        /vol1/docker/mycontainers/nocobase/
                        ├── docker-compose.yml
                        ├── .env
                        └── storage/           <-- 数据卷
                            ├── db/postgres/   <-- PostgreSQL 数据
                            └── ...            <-- NocoBase 存储
```

## 端口分配

| 服务 | 宿主机端口 | 容器端口 | 状态 |
|------|-----------|---------|------|
| NocoBase Web | 18080 | 80 (nginx) | 可用 |
| PostgreSQL | 15432 | 5432 | 可用 |

## 资源限制策略

| 容器 | CPU 上限 | 内存上限 | 说明 |
|------|---------|---------|------|
| nocobase-app | 1.0 核 | 512MB | NODE_OPTIONS --max-old-space-size=384 |
| nocobase-postgres | 0.5 核 | 128MB | PostgreSQL 轻量使用 |

## 遇到的问题及解决

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| APP_PORT=80 冲突 | nginx 和 Node.js 都监听 80 | 移除 APP_PORT 环境变量 |
| curl 不可用 | 容器镜像无 curl/wget | 改用 node 做健康检查 |
| 系统崩溃/OOM | 4核/3.8GB 负载过高 | 添加 CPU/内存限制 + NODE_OPTIONS |
| 健康检查失败 | 端点错误/工具缺失 | 使用 CMD-SHELL + node HTTP 检查 |
