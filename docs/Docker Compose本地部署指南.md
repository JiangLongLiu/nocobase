# NocoBase Docker Compose 本地部署指南

本文档详细介绍如何使用 Docker Compose 在本地部署 NocoBase 应用。

## 前置要求

### 系统要求
- **操作系统**: Windows 10/11, macOS, Linux
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **可用内存**: 至少 4GB RAM
- **可用磁盘**: 至少 10GB 空闲空间

### 安装 Docker 和 Docker Compose

#### Windows
1. 下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. 安装完成后，Docker Compose 已自动包含

#### macOS
1. 下载并安装 [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
2. 安装完成后，Docker Compose 已自动包含

#### Linux
```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 验证安装
```bash
docker --version
docker-compose --version
```

---

## 部署方式一：使用官方镜像（推荐）

这种方式使用 NocoBase 官方预构建的 Docker 镜像，适合快速部署和生产环境使用。

### 1. 创建部署目录

```bash
mkdir nocobase-app
cd nocobase-app
```

### 2. 创建 docker-compose.yml 文件

根据你选择的数据库创建对应的配置文件：

#### 使用 PostgreSQL（推荐）

创建 `docker-compose.yml` 文件：

```yaml
version: "3"

networks:
  nocobase:
    driver: bridge

services:
  app:
    image: nocobase/nocobase:latest
    container_name: nocobase-app
    networks:
      - nocobase
    environment:
      # 应用密钥（必须修改为你自己的随机字符串）
      - APP_KEY=your-secret-key-change-me-$(openssl rand -hex 16)
      - ENCRYPTION_FIELD_KEY=your-encryption-key-change-me-$(openssl rand -hex 16)
      
      # 数据库配置
      - DB_DIALECT=postgres
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_DATABASE=nocobase
      - DB_USER=nocobase
      - DB_PASSWORD=nocobase
      
      # 初始化配置
      - INIT_LANG=zh-CN
      - INIT_ROOT_EMAIL=admin@nocobase.com
      - INIT_ROOT_PASSWORD=admin123
      - INIT_ROOT_NICKNAME=超级管理员
      
    volumes:
      - ./storage:/app/nocobase/storage
    ports:
      - "13000:80"
    depends_on:
      - postgres
    init: true
    restart: unless-stopped

  postgres:
    image: postgres:16
    container_name: nocobase-postgres
    restart: unless-stopped
    command: postgres -c wal_level=logical
    environment:
      POSTGRES_USER: nocobase
      POSTGRES_DB: nocobase
      POSTGRES_PASSWORD: nocobase
    volumes:
      - ./storage/db/postgres:/var/lib/postgresql/data
    networks:
      - nocobase
```

#### 使用 MySQL

创建 `docker-compose.yml` 文件：

```yaml
version: "3"

networks:
  nocobase:
    driver: bridge

services:
  app:
    image: nocobase/nocobase:latest
    container_name: nocobase-app
    networks:
      - nocobase
    environment:
      - APP_KEY=your-secret-key-change-me
      - ENCRYPTION_FIELD_KEY=your-encryption-key-change-me
      - DB_DIALECT=mysql
      - DB_HOST=mysql
      - DB_PORT=3306
      - DB_DATABASE=nocobase
      - DB_USER=nocobase
      - DB_PASSWORD=nocobase
      - INIT_LANG=zh-CN
      - INIT_ROOT_EMAIL=admin@nocobase.com
      - INIT_ROOT_PASSWORD=admin123
    volumes:
      - ./storage:/app/nocobase/storage
    ports:
      - "13000:80"
    depends_on:
      - mysql
    init: true
    restart: unless-stopped

  mysql:
    image: mysql:8
    container_name: nocobase-mysql
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: nocobase
      MYSQL_USER: nocobase
      MYSQL_PASSWORD: nocobase
      MYSQL_ROOT_PASSWORD: nocobase
    volumes:
      - ./storage/db/mysql:/var/lib/mysql
    networks:
      - nocobase
```

### 3. 启动服务

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f app
```

### 4. 访问应用

在浏览器中打开：`http://localhost:13000`

默认登录信息：
- 邮箱：`admin@nocobase.com`
- 密码：`admin123`

**⚠️ 重要：首次登录后请立即修改默认密码！**

---

# 部署方式二：使用源码开发模式

这种方式适合开发人员进行二次开发和调试。

### 为什么选择源码开发模式？

相比官方镜像部署，源码开发模式有以下优势：

#### 1. 更适合二次开发和调试
- 可以直接在本地用 IDE（VS Code / WebStorm）打开整个源码仓库
- 支持代码跳转、重构、全局搜索
- 完整的 TypeScript 类型提示
- 可以设置断点进行前端和后端调试
- 使用 `yarn dev` 支持热更新，修改代码后几乎实时看到效果

#### 2. 与官方开发流程完全对齐
项目内置了完整的开发脚本（`package.json`）：
- `yarn dev` - 本地开发模式
- `yarn dev-server` - 仅启动后端
- `yarn build` + `yarn start` - 构建和生产模式
- `yarn test:*` - 运行测试

使用源码模式，就是在官方推荐的开发环境下工作，后续跟进升级、调试插件、编写测试都会更顺畅。

#### 3. 插件开发和深度定制
如果需要以下功能，源码模式几乎是必选：
- 开发自定义插件（服务端/客户端）
- 修改内置插件行为
- 改动核心逻辑（权限、数据建模、工作流等）
- 本地快速试验新特性、调试 SDK、编写脚本

镜像模式更偏向"黑盒运行"，源码模式则是"完全掌握代码"，适合真正做产品和二次开发。

#### 4. 更细粒度的环境控制
- 完全控制 Node.js 版本（项目要求 Node ≥ 18）
- 精确控制依赖版本：`package.json` + `yarn.lock`
- 可以直接在源码中添加日志、修改依赖版本来排查问题
- 在纯 Docker 镜像模式下这些操作会比较困难

#### 5. 与 Git 流程无缝集成
- 本地就是标准的 Git 仓库，支持分支管理、提交、回滚
- 可以进行 Code Review
- 干净地管理自己的改动、插件源码、配置等

#### 6. 更好的开发体验
- `yarn dev` 启动时前端支持热更新、快速增量构建（Vite/Webpack）
- 适合频繁修改 UI、调试交互的场景
- 不需要每次都打包镜像、重启容器

---

**简单总结**：
- **只是使用 NocoBase**：推荐方式一（官方镜像）
- **需要二次开发/深度定制**：推荐方式二（源码模式）

### 1. 克隆项目（如果还没有）

```bash
git clone https://github.com/nocobase/nocobase.git
cd nocobase
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env
```

编辑 `.env` 文件，修改关键配置：

```bash
# 应用配置
APP_ENV=development
APP_PORT=13000
APP_KEY=your-secret-key  # 修改为你自己的密钥

# 数据库配置（选择一种）
DB_DIALECT=postgres       # postgres | mysql | mariadb
DB_HOST=localhost
DB_PORT=5432              # PostgreSQL: 5432, MySQL: 3306
DB_DATABASE=nocobase
DB_USER=nocobase
DB_PASSWORD=nocobase

# 初始化配置
INIT_LANG=zh-CN
INIT_ROOT_EMAIL=admin@nocobase.com
INIT_ROOT_PASSWORD=admin123
INIT_ROOT_NICKNAME=超级管理员
```

### 3. 启动数据库服务

项目根目录提供了完整的 `docker-compose.yml`，包含多种数据库：

```bash
# 启动 PostgreSQL
docker-compose up -d postgres

# 或启动 MySQL
docker-compose up -d mysql

# 查看数据库服务状态
docker-compose ps
```

### 4. 安装依赖并启动应用

```bash
# 安装依赖（首次运行或更新代码后）
yarn install

# 启动开发服务器
yarn dev

# 或启动生产模式
yarn build
yarn start
```

### 5. 访问应用

在浏览器中打开：`http://localhost:13000`

---

## 常用管理命令

### Docker Compose 命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f [service_name]

# 进入容器内部
docker-compose exec app sh

# 删除所有服务和数据卷（危险操作！）
docker-compose down -v
```

### NocoBase 应用命令

在容器内执行（使用 `docker-compose exec app sh` 进入容器）：

```bash
# 查看帮助
yarn nocobase -h

# 安装 NocoBase
yarn nocobase install

# 升级 NocoBase
yarn nocobase upgrade

# 启动应用
yarn start

# 重启应用
yarn restart
```

---

## 数据持久化

### 数据卷说明

所有重要数据都存储在本地 `storage` 目录中：

```
./storage/
├── db/              # 数据库数据文件
│   ├── postgres/    # PostgreSQL 数据
│   ├── mysql/       # MySQL 数据
│   └── kingbase/    # Kingbase 数据
├── logs/            # 应用日志
├── uploads/         # 上传的文件
└── backups/         # 备份文件
```

### 备份数据

```bash
# 备份整个 storage 目录
tar -czf nocobase-backup-$(date +%Y%m%d).tar.gz storage/

# 仅备份数据库
docker-compose exec postgres pg_dump -U nocobase nocobase > backup.sql

# 或 MySQL
docker-compose exec mysql mysqldump -u nocobase -pnocobase nocobase > backup.sql
```

### 恢复数据

```bash
# 恢复 PostgreSQL
docker-compose exec -T postgres psql -U nocobase nocobase < backup.sql

# 恢复 MySQL
docker-compose exec -T mysql mysql -u nocobase -pnocobase nocobase < backup.sql
```

---

## 端口配置

默认端口分配（在 `.env` 中配置）：

| 服务 | 默认端口 | 环境变量 | 说明 |
|------|---------|----------|------|
| NocoBase 应用 | 13000 | APP_PORT | Web 访问端口 |
| PostgreSQL | 10103 | DB_POSTGRES_PORT | PostgreSQL 数据库端口 |
| MySQL | 10102 | DB_MYSQL_PORT | MySQL 数据库端口 |
| Adminer | 10101 | ADMINER_PORT | 数据库管理工具 |
| Verdaccio | 10104 | VERDACCIO_PORT | NPM 私有源 |

如果端口冲突，可以修改 `.env` 文件中的对应端口号。

---

## 常见问题排查

### 1. 端口被占用

**错误信息**: `Bind for 0.0.0.0:13000 failed: port is already allocated`

**解决方案**:
```bash
# Windows
netstat -ano | findstr :13000

# Linux/macOS
lsof -i :13000

# 修改 .env 中的 APP_PORT 或停止占用端口的程序
```

### 2. 容器启动失败

**解决方案**:
```bash
# 查看详细日志
docker-compose logs app

# 重新构建并启动
docker-compose down
docker-compose up -d --force-recreate
```

### 3. 数据库连接失败

**检查项**:
1. 确保数据库容器正在运行：`docker-compose ps`
2. 检查 `.env` 中的数据库配置是否正确
3. 查看数据库日志：`docker-compose logs postgres`

### 4. 权限问题（Linux）

**错误信息**: `Permission denied`

**解决方案**:
```bash
# 修改 storage 目录权限
sudo chown -R $(id -u):$(id -g) storage/
```

### 5. 内存不足

**解决方案**:
```bash
# 增加 Docker 可用内存（Docker Desktop 设置）
# 或清理 Docker 缓存
docker system prune -a
```

### 6. 无法访问应用

**检查清单**:
- [ ] 容器是否正在运行：`docker-compose ps`
- [ ] 端口映射是否正确：查看 `docker-compose.yml`
- [ ] 防火墙是否阻止端口访问
- [ ] 查看应用日志：`docker-compose logs -f app`

---

## 升级 NocoBase

### 使用官方镜像

```bash
# 停止服务
docker-compose down

# 拉取最新镜像
docker-compose pull

# 启动服务
docker-compose up -d

# 执行升级
docker-compose exec app yarn nocobase upgrade
```

### 使用源码

```bash
# 拉取最新代码
git pull

# 安装依赖
yarn install

# 构建
yarn build

# 执行升级
yarn nocobase upgrade

# 重启服务
yarn restart
```

---

## 安全建议

### 1. 修改默认密钥

在 `.env` 或 `docker-compose.yml` 中：
```bash
APP_KEY=$(openssl rand -hex 32)
ENCRYPTION_FIELD_KEY=$(openssl rand -hex 32)
```

### 2. 修改默认密码

首次登录后立即修改：
- 管理员密码
- 数据库密码（如果暴露端口）

### 3. 生产环境配置

```bash
# .env 文件
APP_ENV=production

# 不要暴露数据库端口
# 在 docker-compose.yml 中删除 ports 配置
```

### 4. 使用反向代理

推荐使用 Nginx 作为反向代理：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:13000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 性能优化

### 1. 数据库优化

**PostgreSQL**:
```yaml
# docker-compose.yml
postgres:
  command: postgres -c wal_level=logical -c max_connections=200 -c shared_buffers=256MB
```

**MySQL**:
```yaml
# docker-compose.yml
mysql:
  command: --max-connections=200 --innodb-buffer-pool-size=256M
```

### 2. 应用缓存配置

在 `.env` 中启用 Redis 缓存：
```bash
CACHE_DEFAULT_STORE=redis
CACHE_REDIS_URL=redis://redis:6379
```

添加 Redis 服务到 `docker-compose.yml`：
```yaml
redis:
  image: redis:7-alpine
  container_name: nocobase-redis
  restart: unless-stopped
  networks:
    - nocobase
```

---

## 监控和日志

### 查看日志

```bash
# 实时查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f app

# 查看最近 100 行日志
docker-compose logs --tail=100 app
```

### 日志配置

在 `.env` 中配置日志：
```bash
# 日志传输方式: console | file | dailyRotateFile
LOGGER_TRANSPORT=dailyRotateFile

# 日志级别: error | warn | info | debug | trace
LOGGER_LEVEL=info

# 日志保存路径
LOGGER_BASE_PATH=storage/logs

# 日志保留天数
LOGGER_MAX_FILES=7d

# 单个日志文件大小
LOGGER_MAX_SIZE=20m
```

---

## 多环境部署

### 开发环境
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 生产环境
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 附录：完整配置示例

### 生产环境 docker-compose.yml

```yaml
version: "3"

networks:
  nocobase:
    driver: bridge

services:
  app:
    image: nocobase/nocobase:latest
    container_name: nocobase-app
    networks:
      - nocobase
    environment:
      - APP_ENV=production
      - APP_KEY=${APP_KEY}
      - ENCRYPTION_FIELD_KEY=${ENCRYPTION_FIELD_KEY}
      - DB_DIALECT=postgres
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_DATABASE=nocobase
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - CACHE_DEFAULT_STORE=redis
      - CACHE_REDIS_URL=redis://redis:6379
      - LOGGER_TRANSPORT=dailyRotateFile
      - LOGGER_LEVEL=info
    volumes:
      - ./storage:/app/nocobase/storage
    ports:
      - "13000:80"
    depends_on:
      - postgres
      - redis
    init: true
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G

  postgres:
    image: postgres:16
    container_name: nocobase-postgres
    restart: unless-stopped
    command: |
      postgres
      -c wal_level=logical
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_DB: nocobase
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - ./storage/db/postgres:/var/lib/postgresql/data
    networks:
      - nocobase
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

  redis:
    image: redis:7-alpine
    container_name: nocobase-redis
    restart: unless-stopped
    networks:
      - nocobase
    command: redis-server --appendonly yes
    volumes:
      - ./storage/redis:/data
```

### 对应的 .env 文件

```bash
# 应用密钥（使用 openssl rand -hex 32 生成）
APP_KEY=your-generated-secret-key-here
ENCRYPTION_FIELD_KEY=your-generated-encryption-key-here

# 数据库配置
DB_USER=nocobase
DB_PASSWORD=your-strong-password-here
```

---

## 技术支持

- 官方文档：https://docs.nocobase.com
- GitHub Issues：https://github.com/nocobase/nocobase/issues
- 社区论坛：https://forum.nocobase.com

---

**最后更新**: 2025-12-26
