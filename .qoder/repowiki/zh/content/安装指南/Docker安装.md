# Docker安装

<cite>
**本文档中引用的文件**  
- [Dockerfile](file://Dockerfile)
- [Dockerfile.pro](file://Dockerfile.pro)
- [docker-compose.yml](file://docker-compose.yml)
- [.env.example](file://.env.example)
- [docker/nocobase/Dockerfile](file://docker/nocobase/Dockerfile)
- [docker/nocobase/Dockerfile-full](file://docker/nocobase/Dockerfile-full)
- [docker/nocobase/docker-entrypoint.sh](file://docker/nocobase/docker-entrypoint.sh)
- [docker/nocobase/nocobase.conf](file://docker/nocobase/nocobase.conf)
- [docker/app-mysql/docker-compose.yml](file://docker/app-mysql/docker-compose.yml)
- [docker/app-postgres/docker-compose.yml](file://docker/app-postgres/docker-compose.yml)
- [docker/app-mariadb/docker-compose.yml](file://docker/app-mariadb/docker-compose.yml)
- [docker/app-sqlite/docker-compose.yml](file://docker/app-sqlite/docker-compose.yml)
</cite>

## 目录
1. [简介](#简介)
2. [项目结构](#项目结构)
3. [核心组件](#核心组件)
4. [架构概述](#架构概述)
5. [详细组件分析](#详细组件分析)
6. [依赖分析](#依赖分析)
7. [性能考虑](#性能考虑)
8. [故障排除指南](#故障排除指南)
9. [结论](#结论)

## 简介
本文档提供了NocoBase的完整Docker部署指南，涵盖使用`docker-compose.yml`文件部署NocoBase的详细步骤。文档详细解释了各个服务的配置说明（nocobase、数据库等）、Dockerfile中的构建指令、docker-entrypoint.sh中的初始化脚本、环境变量配置（包括数据库连接、端口映射和存储卷设置）、Docker网络配置、容器间通信和安全最佳实践。同时提供常见问题的解决方案，如容器启动失败、数据库初始化问题和网络连接错误，并包含生产环境部署的最佳实践和性能优化建议。

## 项目结构
NocoBase的Docker相关文件组织在`docker/`目录下，包含多个预配置的`docker-compose.yml`文件用于不同的数据库后端，以及nocobase服务的Docker构建文件。

```mermaid
graph TD
A[docker/] --> B[app-mysql/]
A --> C[app-postgres/]
A --> D[app-mariadb/]
A --> E[app-sqlite/]
A --> F[nocobase/]
B --> G[docker-compose.yml]
C --> H[docker-compose.yml]
D --> I[docker-compose.yml]
E --> J[docker-compose.yml]
F --> K[Dockerfile]
F --> L[Dockerfile-full]
F --> M[docker-entrypoint.sh]
F --> N[nocobase.conf]
```

**图示来源**
- [docker/app-mysql/docker-compose.yml](file://docker/app-mysql/docker-compose.yml)
- [docker/app-postgres/docker-compose.yml](file://docker/app-postgres/docker-compose.yml)
- [docker/app-mariadb/docker-compose.yml](file://docker/app-mariadb/docker-compose.yml)
- [docker/app-sqlite/docker-compose.yml](file://docker/app-sqlite/docker-compose.yml)
- [docker/nocobase/Dockerfile](file://docker/nocobase/Dockerfile)

**章节来源**
- [docker/](file://docker/)

## 核心组件
NocoBase的Docker部署包含两个主要组件：应用服务（nocobase）和数据库服务。应用服务基于Node.js构建，通过Nginx提供静态文件服务，而数据库服务支持多种数据库后端，包括MySQL、PostgreSQL、MariaDB和SQLite。

**章节来源**
- [docker/nocobase/Dockerfile](file://docker/nocobase/Dockerfile#L1-L49)
- [docker/app-mysql/docker-compose.yml](file://docker/app-mysql/docker-compose.yml#L1-L38)

## 架构概述
NocoBase的Docker部署采用多容器架构，其中应用容器和数据库容器通过自定义Docker网络进行通信。应用容器暴露80端口，通过端口映射将外部请求的13000端口转发到容器内部的80端口。

```mermaid
graph LR
Client[客户端] --> |HTTP请求| Proxy[Nginx代理]
Proxy --> |API请求| App[NocoBase应用]
App --> |数据库操作| DB[(数据库)]
App --> |文件存储| Storage[(存储卷)]
subgraph Docker网络
App
DB
Storage
end
```

**图示来源**
- [docker/app-mysql/docker-compose.yml](file://docker/app-mysql/docker-compose.yml#L1-L38)
- [docker/nocobase/nocobase.conf](file://docker/nocobase/nocobase.conf#L1-L91)

## 详细组件分析

### NocoBase应用服务分析
NocoBase应用服务是部署的核心组件，负责处理所有业务逻辑和API请求。服务通过Dockerfile构建，并在启动时执行初始化脚本。

#### Dockerfile构建指令
NocoBase的Dockerfile采用多阶段构建策略，第一阶段使用Node.js基础镜像创建应用包，第二阶段将包复制到精简的运行时镜像中。

```mermaid
graph TD
A[构建阶段] --> B[安装依赖]
B --> C[创建NocoBase应用]
C --> D[打包应用]
D --> E[运行阶段]
E --> F[安装运行时依赖]
F --> G[复制应用包]
G --> H[配置Nginx]
H --> I[启动服务]
```

**图示来源**
- [docker/nocobase/Dockerfile](file://docker/nocobase/Dockerfile#L1-L49)

**章节来源**
- [docker/nocobase/Dockerfile](file://docker/nocobase/Dockerfile#L1-L49)

#### docker-entrypoint.sh初始化脚本
初始化脚本负责在容器启动时执行必要的设置步骤，包括解压附加组件、创建应用目录、生成Nginx配置和启动服务。

```mermaid
graph TD
A[启动脚本] --> B[设置环境变量]
B --> C{检查LibreOffice}
C --> |存在| D[解压LibreOffice]
C --> |不存在| E[跳过]
D --> F{检查Oracle客户端}
E --> F
F --> |存在| G[解压并配置]
F --> |不存在| H[跳过]
G --> I{应用目录存在?}
H --> I
I --> |否| J[创建目录并解压应用]
I --> |是| K[跳过]
J --> L[生成Nginx配置]
K --> L
L --> M[启动Nginx]
M --> N[运行启动脚本]
N --> O[启动应用]
```

**图示来源**
- [docker/nocobase/docker-entrypoint.sh](file://docker/nocobase/docker-entrypoint.sh#L1-L56)

**章节来源**
- [docker/nocobase/docker-entrypoint.sh](file://docker/nocobase/docker-entrypoint.sh#L1-L56)

### 数据库服务配置
NocoBase支持多种数据库后端，每种数据库都有对应的docker-compose配置文件。

#### MySQL数据库配置
MySQL数据库服务配置包括环境变量设置、数据卷挂载和网络配置。

```mermaid
classDiagram
class MySQLConfig {
+image : mysql : latest
+environment : Map[string,string]
+volumes : List[string]
+networks : List[string]
+restart : always
}
MySQLConfig : MYSQL_DATABASE : nocobase
MySQLConfig : MYSQL_USER : nocobase
MySQLConfig : MYSQL_PASSWORD : nocobase
MySQLConfig : MYSQL_ROOT_PASSWORD : nocobase
```

**图示来源**
- [docker/app-mysql/docker-compose.yml](file://docker/app-mysql/docker-compose.yml#L1-L38)

**章节来源**
- [docker/app-mysql/docker-compose.yml](file://docker/app-mysql/docker-compose.yml#L1-L38)

#### PostgreSQL数据库配置
PostgreSQL数据库服务配置与MySQL类似，但包含特定的WAL级别设置以支持逻辑复制。

```mermaid
flowchart TD
A[PostgreSQL服务] --> B[设置环境变量]
B --> C[配置WAL级别]
C --> D[挂载数据卷]
D --> E[连接到网络]
E --> F[设置重启策略]
C --> |command| G[postgres -c wal_level=logical]
```

**图示来源**
- [docker/app-postgres/docker-compose.yml](file://docker/app-postgres/docker-compose.yml#L1-L37)

**章节来源**
- [docker/app-postgres/docker-compose.yml](file://docker/app-postgres/docker-compose.yml#L1-L37)

#### MariaDB数据库配置
MariaDB数据库服务配置与MySQL几乎相同，使用MariaDB镜像替代MySQL镜像。

```mermaid
graph LR
A[MariaDB服务] --> B[使用mariadb:latest镜像]
B --> C[设置数据库环境变量]
C --> D[挂载数据卷到/var/lib/mysql]
D --> E[连接到nocobase网络]
E --> F[设置始终重启]
```

**图示来源**
- [docker/app-mariadb/docker-compose.yml](file://docker/app-mariadb/docker-compose.yml#L1-L39)

**章节来源**
- [docker/app-mariadb/docker-compose.yml](file://docker/app-mariadb/docker-compose.yml#L1-L39)

#### SQLite数据库配置
SQLite数据库服务配置最为简单，因为SQLite是文件型数据库，不需要独立的数据库服务。

```mermaid
graph TD
A[SQLite配置] --> B[无需数据库服务]
B --> C[应用直接访问存储卷中的数据库文件]
C --> D[通过存储卷持久化数据]
```

**图示来源**
- [docker/app-sqlite/docker-compose.yml](file://docker/app-sqlite/docker-compose.yml#L1-L15)

**章节来源**
- [docker/app-sqlite/docker-compose.yml](file://docker/app-sqlite/docker-compose.yml#L1-L15)

### Nginx配置分析
NocoBase使用Nginx作为反向代理服务器，处理静态文件服务和API请求转发。

```mermaid
graph TD
A[Nginx配置] --> B[日志格式定义]
B --> C[服务器块配置]
C --> D[监听80端口]
D --> E[设置根目录]
E --> F[配置访问日志]
F --> G[启用Gzip压缩]
G --> H[静态文件缓存策略]
H --> I[API请求代理]
I --> J[WebSocket连接代理]
```

**图示来源**
- [docker/nocobase/nocobase.conf](file://docker/nocobase/nocobase.conf#L1-L91)

**章节来源**
- [docker/nocobase/nocobase.conf](file://docker/nocobase/nocobase.conf#L1-L91)

## 依赖分析
NocoBase的Docker部署依赖于多个外部组件和服务，包括数据库服务、存储卷和网络配置。

```mermaid
graph TD
A[NocoBase应用] --> B[数据库服务]
A --> C[存储卷]
A --> D[Nginx]
B --> E[MySQL/MariaDB]
B --> F[PostgreSQL]
B --> G[SQLite]
C --> H[上传文件]
C --> I[日志文件]
C --> J[配置文件]
D --> K[静态文件服务]
D --> L[API代理]
```

**图示来源**
- [docker/app-mysql/docker-compose.yml](file://docker/app-mysql/docker-compose.yml#L1-L38)
- [docker/app-postgres/docker-compose.yml](file://docker/app-postgres/docker-compose.yml#L1-L37)
- [docker/nocobase/nocobase.conf](file://docker/nocobase/nocobase.conf#L1-L91)

**章节来源**
- [docker/app-mysql/docker-compose.yml](file://docker/app-mysql/docker-compose.yml#L1-L38)
- [docker/app-postgres/docker-compose.yml](file://docker/app-postgres/docker-compose.yml#L1-L37)
- [docker/nocobase/nocobase.conf](file://docker/nocobase/nocobase.conf#L1-L91)

## 性能考虑
在生产环境中部署NocoBase时，需要考虑多个性能优化因素，包括数据库连接池配置、静态文件缓存和资源限制。

### 数据库连接池配置
通过环境变量可以配置数据库连接池的大小和行为，以优化数据库性能。

```mermaid
graph TD
A[数据库连接池] --> B[最大连接数]
A --> C[最小连接数]
A --> D[空闲超时]
A --> E[获取超时]
A --> F[驱逐间隔]
A --> G[最大使用次数]
B --> |DB_POOL_MAX| H[默认值: 5]
C --> |DB_POOL_MIN| I[默认值: 0]
D --> |DB_POOL_IDLE| J[默认值: 10000ms]
E --> |DB_POOL_ACQUIRE| K[默认值: 60000ms]
F --> |DB_POOL_EVICT| L[默认值: 1000ms]
G --> |DB_POOL_MAX_USES| M[默认值: 0 (无限)]
```

**章节来源**
- [.env.example](file://.env.example#L60-L67)

### 静态文件缓存策略
Nginx配置了针对不同文件类型的缓存策略，以提高静态文件的访问性能。

```mermaid
flowchart TD
A[静态文件请求] --> B{文件类型}
B --> |HTML| C[不缓存]
B --> |JS/CSS| D[缓存365天]
B --> |上传文件| E[不记录访问日志]
C --> F[设置Cache-Control: no-store]
D --> G[设置Cache-Control: public]
E --> H[设置access_log off]
```

**章节来源**
- [docker/nocobase/nocobase.conf](file://docker/nocobase/nocobase.conf#L26-L37)

## 故障排除指南
本节提供常见问题的解决方案，帮助用户解决部署过程中可能遇到的问题。

### 容器启动失败
当容器无法启动时，可能的原因包括端口冲突、存储卷权限问题或环境变量配置错误。

```mermaid
graph TD
A[容器启动失败] --> B{检查日志}
B --> C[端口被占用]
C --> |是| D[更改端口映射]
C --> |否| E[检查存储卷]
E --> F[权限问题]
F --> |是| G[修复目录权限]
F --> |否| H[检查环境变量]
H --> I[配置错误]
I --> |是| J[修正环境变量]
I --> |否| K[检查Docker资源]
```

**章节来源**
- [docker/app-mysql/docker-compose.yml](file://docker/app-mysql/docker-compose.yml#L24)
- [docker/nocobase/docker-entrypoint.sh](file://docker/nocobase/docker-entrypoint.sh#L35)

### 数据库初始化问题
数据库初始化问题通常与连接配置、用户权限或数据卷挂载有关。

```mermaid
flowchart TD
A[数据库初始化问题] --> B{检查数据库服务}
B --> C[服务是否运行]
C --> |否| D[启动数据库服务]
C --> |是| E[检查连接参数]
E --> F[主机名是否正确]
F --> |否| G[修正DB_HOST]
F --> |是| H[检查认证信息]
H --> I[用户名/密码是否正确]
I --> |否| J[修正认证信息]
I --> |是| K[检查数据卷]
K --> L[数据是否持久化]
L --> |否| M[检查卷挂载]
```

**章节来源**
- [docker/app-mysql/docker-compose.yml](file://docker/app-mysql/docker-compose.yml#L16-L19)
- [docker/app-postgres/docker-compose.yml](file://docker/app-postgres/docker-compose.yml#L14-L17)

### 网络连接错误
网络连接错误通常是由于Docker网络配置不当或服务依赖关系错误导致的。

```mermaid
graph TD
A[网络连接错误] --> B{检查Docker网络}
B --> C[网络是否存在]
C --> |否| D[创建网络]
C --> |是| E[服务是否在同一网络]
E --> |否| F[添加到同一网络]
E --> |是| G[检查服务依赖]
G --> H[依赖服务是否启动]
H --> |否| I[添加depends_on]
H --> |是| J[检查防火墙]
```

**章节来源**
- [docker/app-mysql/docker-compose.yml](file://docker/app-mysql/docker-compose.yml#L2-L4)
- [docker/app-postgres/docker-compose.yml](file://docker/app-postgres/docker-compose.yml#L2-L4)

## 结论
NocoBase提供了完善的Docker部署方案，通过预配置的`docker-compose.yml`文件可以轻松部署到各种环境中。文档详细介绍了各个组件的配置方法、环境变量设置、网络配置和常见问题的解决方案。在生产环境中部署时，建议根据实际需求调整数据库连接池配置、存储卷设置和资源限制，以获得最佳性能。同时，遵循安全最佳实践，如使用强密码、定期备份数据和监控系统日志，可以确保系统的稳定和安全运行。