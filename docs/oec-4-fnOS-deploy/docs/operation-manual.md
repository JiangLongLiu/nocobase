# NocoBase on oec-4-fnOS 操作手册

## 环境信息

| 项目 | 值 |
|------|-----|
| 主机 | oec-4-fnOS (192.168.123.54) |
| 架构 | x86_64 |
| CPU/内存 | 4核 / 3.8GB |
| 部署路径 | /vol1/docker/mycontainers/nocobase |
| NocoBase 端口 | **18080** (映射到容器 80) |
| PostgreSQL 端口 | **15432** (映射到容器 5432) |

## 访问地址

- **Web 界面**: http://192.168.123.54:18080/
- **API**: http://192.168.123.54:18080/api/

## 默认登录凭据

| 项目 | 值 |
|------|-----|
| 用户名 | admin |
| 密码 | 见 .env 文件中 INIT_ROOT_PASSWORD |
| 邮箱 | admin@nocobase.com |

## 资源限制

由于 oec-4 主机资源有限（4核/3.8GB），NocoBase 容器配置了以下资源限制：

| 容器 | CPU | 内存 | Node.js 堆 |
|------|-----|------|------------|
| nocobase-app | 1 核 | 512MB | 384MB |
| nocobase-postgres | 0.5 核 | 128MB | - |

## 常用操作

### 查看容器状态

```bash
ssh root@192.168.123.54
cd /vol1/docker/mycontainers/nocobase
docker compose ps
```

### 查看容器日志

```bash
# 最近 50 行
docker compose logs --tail=50 nocobase

# 实时跟踪
docker compose logs -f nocobase
```

### 重启容器

```bash
cd /vol1/docker/mycontainers/nocobase
docker compose restart
```

### 停止容器

```bash
docker compose down
```

### 启动容器

```bash
docker compose up -d
```

### 更新 NocoBase 镜像

```bash
cd /vol1/docker/mycontainers/nocobase
docker compose pull
docker compose up -d
```

## 从本机修改配置

1. 在本机编辑 `docs/oec-4-fnOS-deploy/config/` 下的文件
2. 使用脚本上传：
   ```bash
   python docs/oec-4-fnOS-deploy/scripts/02-upload-and-deploy.py
   ```
3. 或手动上传：
   ```bash
   python docs/oec-4-fnOS-deploy/scripts/_quick_redeploy.py
   ```

## 数据备份

数据卷路径（在宿主机上）：
- **PostgreSQL 数据**: /vol1/docker/mycontainers/nocobase/storage/db/postgres
- **NocoBase 存储**: /vol1/docker/mycontainers/nocobase/storage

备份命令：
```bash
# 备份数据库
docker compose exec postgres pg_dump -U nocobase nocobase > backup_$(date +%Y%m%d).sql

# 备份整个 storage 目录
tar czf nocobase_storage_$(date +%Y%m%d).tar.gz storage/
```

## 故障排查

### 容器反复重启

检查日志：`docker compose logs --tail=100 nocobase`

常见原因：
- 内存不足（OOM）：查看 `docker stats`，确认内存使用是否接近限制
- 数据库连接失败：检查 postgres 容器是否 healthy

### 系统负载过高

```bash
# 查看系统负载
uptime

# 查看各容器资源占用
docker stats --no-stream

# 如果 NocoBase 内存接近上限，可以进一步降低 NODE_OPTIONS
# 编辑 docker-compose.yml 中的 NODE_OPTIONS: "--max-old-space-size=256"
```

### 端口被占用

使用端口检测脚本检查：
```bash
python docs/oec-4-fnOS-deploy/scripts/01-check-ports.py
```
