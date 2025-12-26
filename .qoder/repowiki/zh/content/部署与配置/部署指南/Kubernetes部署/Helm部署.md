# Helm部署

<cite>
**本文档中引用的文件**  
- [docker-compose.yml](file://docker-compose.yml)
- [.env.example](file://.env.example)
- [docker/nocobase/Dockerfile](file://docker/nocobase/Dockerfile)
- [docker/nocobase/docker-entrypoint.sh](file://docker/nocobase/docker-entrypoint.sh)
- [docker/nocobase/nocobase.conf](file://docker/nocobase/nocobase.conf)
- [package.json](file://package.json)
- [packages/core/server/src/environment.ts](file://packages/core/server/src/environment.ts)
- [packages/plugins/@nocobase/plugin-environment-variables/src/server/plugin.ts](file://packages/plugins/@nocobase/plugin-environment-variables/src/server/plugin.ts)
- [packages/plugins/@nocobase/plugin-environment-variables/src/server/collections/environmentVariables.ts](file://packages/plugins/@nocobase/plugin-environment-variables/src/server/collections/environmentVariables.ts)
- [packages/core/database/src/helpers.ts](file://packages/core/database/src/helpers.ts)
</cite>

## 目录
1. [简介](#简介)
2. [Chart结构](#chart结构)
3. [values.yaml配置选项](#valuesyaml配置选项)
4. [Helm安装、升级和回滚](#helm安装升级和回滚)
5. [数据库连接配置](#数据库连接配置)
6. [缓存服务配置](#缓存服务配置)
7. [存储卷配置](#存储卷配置)
8. [不同环境的Helm配置](#不同环境的helm配置)
9. [Helm Hook使用方法](#helm-hook使用方法)
10. [自定义Helm模板开发](#自定义helm模板开发)

## 简介

NocoBase是一个可扩展的AI驱动的无代码平台，支持通过Docker和Docker Compose进行部署。虽然项目中没有现成的Helm Chart，但可以根据现有的Docker部署配置创建Helm Chart来部署NocoBase。本指南将详细介绍如何使用Helm部署NocoBase，包括Chart的结构、values.yaml配置选项和自定义参数。

**Section sources**
- [README.md](file://README.md#L1-L96)

## Chart结构

NocoBase的Helm Chart结构应包括以下主要文件和目录：

- `Chart.yaml`: 包含Chart的基本信息，如名称、版本和描述。
- `values.yaml`: 包含默认的配置值。
- `templates/`: 包含Kubernetes资源的模板文件，如Deployment、Service、ConfigMap等。
- `templates/_helpers.tpl`: 包含可重用的模板助手。
- `templates/tests/`: 包含Helm测试的模板文件。

基于NocoBase的Docker部署配置，Chart的结构可以设计为支持多数据库、缓存服务和存储卷的配置。

**Section sources**
- [docker-compose.yml](file://docker-compose.yml#L1-L80)
- [package.json](file://package.json#L1-L102)

## values.yaml配置选项

values.yaml文件应包含以下主要配置选项：

- `image.repository`: NocoBase Docker镜像的仓库。
- `image.tag`: NocoBase Docker镜像的标签。
- `image.pullPolicy`: 镜像拉取策略。
- `service.type`: 服务类型（ClusterIP、NodePort、LoadBalancer）。
- `service.port`: 服务端口。
- `ingress.enabled`: 是否启用Ingress。
- `ingress.hosts`: Ingress主机列表。
- `ingress.tls`: Ingress TLS配置。
- `resources`: 资源请求和限制。
- `nodeSelector`: 节点选择器。
- `tolerations`: 容忍度。
- `affinity`: 亲和性。

这些配置选项可以根据不同的部署需求进行自定义。

**Section sources**
- [.env.example](file://.env.example#L1-L98)
- [docker-compose.yml](file://docker-compose.yml#L1-L80)

## Helm安装、升级和回滚

### Helm安装

使用以下命令安装NocoBase Helm Chart：

```bash
helm install nocobase ./nocobase-chart --values values.yaml
```

### Helm升级

使用以下命令升级NocoBase Helm Chart：

```bash
helm upgrade nocobase ./nocobase-chart --values values.yaml
```

### Helm回滚

使用以下命令回滚到之前的版本：

```bash
helm rollback nocobase <revision>
```

其中`<revision>`是想要回滚到的版本号。

**Section sources**
- [package.json](file://package.json#L1-L102)
- [docker-compose.yml](file://docker-compose.yml#L1-L80)

## 数据库连接配置

NocoBase支持多种数据库，包括PostgreSQL、MySQL、MariaDB和Kingbase。在Helm Chart中，可以通过values.yaml文件配置数据库连接参数：

- `database.dialect`: 数据库类型（postgres、mysql、mariadb、kingbase）。
- `database.host`: 数据库主机。
- `database.port`: 数据库端口。
- `database.database`: 数据库名称。
- `database.user`: 数据库用户。
- `database.password`: 数据库密码。
- `database.ssl`: SSL配置。

这些参数可以通过环境变量传递给NocoBase应用。

**Section sources**
- [.env.example](file://.env.example#L46-L73)
- [packages/core/database/src/helpers.ts](file://packages/core/database/src/helpers.ts#L46-L86)

## 缓存服务配置

NocoBase支持内存缓存和Redis缓存。在Helm Chart中，可以通过values.yaml文件配置缓存服务：

- `cache.defaultStore`: 默认缓存存储（memory、redis）。
- `cache.memory.max`: 内存缓存的最大项数。
- `cache.redis.url`: Redis URL。

这些参数可以通过环境变量传递给NocoBase应用。

**Section sources**
- [.env.example](file://.env.example#L74-L79)
- [packages/core/server/src/environment.ts](file://packages/core/server/src/environment.ts#L1-L47)

## 存储卷配置

NocoBase需要持久化存储来保存上传的文件和日志。在Helm Chart中，可以通过values.yaml文件配置存储卷：

- `persistence.enabled`: 是否启用持久化存储。
- `persistence.storageClass`: 存储类。
- `persistence.accessModes`: 访问模式。
- `persistence.size`: 存储大小。
- `persistence.mountPath`: 挂载路径。

这些配置可以确保NocoBase的数据在Pod重启后不会丢失。

**Section sources**
- [docker-compose.yml](file://docker-compose.yml#L1-L80)
- [storage](file://storage)

## 不同环境的Helm配置

### 开发环境

在开发环境中，可以使用以下配置：

- `image.pullPolicy`: Always
- `resources`: 较低的资源请求和限制
- `persistence.enabled`: false

### 测试环境

在测试环境中，可以使用以下配置：

- `image.pullPolicy`: IfNotPresent
- `resources`: 中等的资源请求和限制
- `persistence.enabled`: true

### 生产环境

在生产环境中，可以使用以下配置：

- `image.pullPolicy`: IfNotPresent
- `resources`: 较高的资源请求和限制
- `persistence.enabled`: true
- `replicaCount`: 2或更多
- `ingress.enabled`: true

这些配置可以根据实际需求进行调整。

**Section sources**
- [.env.example](file://.env.example#L1-L98)
- [docker-compose.yml](file://docker-compose.yml#L1-L80)

## Helm Hook使用方法

Helm Hook可以用于执行预安装和后升级任务。例如，可以在安装前创建数据库，或在升级后迁移数据库。

### 预安装Hook

创建一个名为`pre-install-job.yaml`的文件，内容如下：

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: "{{ .Release.Name }}-pre-install"
  annotations:
    "helm.sh/hook": pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      containers:
      - name: pre-install
        image: postgres:13
        command: ['sh', '-c', 'psql -h postgres -U postgres -c "CREATE DATABASE nocobase;"']
      restartPolicy: Never
```

### 后升级Hook

创建一个名为`post-upgrade-job.yaml`的文件，内容如下：

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: "{{ .Release.Name }}-post-upgrade"
  annotations:
    "helm.sh/hook": post-upgrade
    "helm.sh/hook-weight": "5"
    "helm.sh/hook-delete-policy": hook-succeeded
spec:
  template:
    spec:
      containers:
      - name: post-upgrade
        image: node:16
        command: ['sh', '-c', 'cd /app && yarn migrate']
        volumeMounts:
        - name: app-volume
          mountPath: /app
      volumes:
      - name: app-volume
        persistentVolumeClaim:
          claimName: "{{ .Release.Name }}-pvc"
      restartPolicy: Never
```

这些Hook可以确保在安装和升级过程中执行必要的任务。

**Section sources**
- [docker-compose.yml](file://docker-compose.yml#L1-L80)
- [package.json](file://package.json#L1-L102)

## 自定义Helm模板开发

### 创建自定义模板

在`templates/`目录中创建自定义模板文件，例如`custom-configmap.yaml`：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-custom-config
data:
  config.json: |-
    {
      "database": {
        "dialect": "{{ .Values.database.dialect }}",
        "host": "{{ .Values.database.host }}",
        "port": {{ .Values.database.port }},
        "database": "{{ .Values.database.database }}",
        "username": "{{ .Values.database.user }}",
        "password": "{{ .Values.database.password }}"
      }
    }
```

### 使用自定义模板

在`deployment.yaml`中引用自定义ConfigMap：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deployment
spec:
  template:
    spec:
      containers:
      - name: nocobase
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        env:
        - name: DB_DIALECT
          valueFrom:
            configMapKeyRef:
              name: {{ .Release.Name }}-custom-config
              key: database.dialect
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: {{ .Release.Name }}-custom-config
              key: database.host
        # 其他环境变量...
```

通过这种方式，可以创建灵活的Helm Chart来满足特定的部署需求。

**Section sources**
- [docker-compose.yml](file://docker-compose.yml#L1-L80)
- [.env.example](file://.env.example#L1-L98)
- [packages/plugins/@nocobase/plugin-environment-variables/src/server/plugin.ts](file://packages/plugins/@nocobase/plugin-environment-variables/src/server/plugin.ts#L1-L219)
- [packages/plugins/@nocobase/plugin-environment-variables/src/server/collections/environmentVariables.ts](file://packages/plugins/@nocobase/plugin-environment-variables/src/server/collections/environmentVariables.ts#L1-L35)