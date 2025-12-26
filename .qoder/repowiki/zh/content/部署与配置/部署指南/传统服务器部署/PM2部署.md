# PM2部署

<cite>
**本文档中引用的文件**  
- [package.json](file://package.json)
- [packages/core/cli/src/commands/pm2.js](file://packages/core/cli/src/commands/pm2.js)
- [packages/core/cli/src/commands/start.js](file://packages/core/cli/src/commands/start.js)
- [packages/core/server/src/environment.ts](file://packages/core/server/src/environment.ts)
- [packages/plugins/@nocobase/plugin-environment-variables/src/server/plugin.ts](file://packages/plugins/@nocobase/plugin-environment-variables/src/server/plugin.ts)
- [packages/core/logger/src/system-logger.ts](file://packages/core/logger/src/system-logger.ts)
- [.env.example](file://.env.example)
- [docker/nocobase/nocobase.conf](file://docker/nocobase/nocobase.conf)
- [packages/core/cli/nocobase.conf.tpl](file://packages/core/cli/nocobase.conf.tpl)
</cite>

## 目录
1. [简介](#简介)
2. [PM2配置文件配置](#pm2配置文件配置)
3. [进程管理命令](#进程管理命令)
4. [集群模式配置](#集群模式配置)
5. [日志管理](#日志管理)
6. [环境变量配置](#环境变量配置)
7. [PM2监控面板](#pm2监控面板)
8. [生产环境部署建议](#生产环境部署建议)

## 简介

NocoBase是一个低代码开发平台，支持使用PM2进程管理器进行应用部署和管理。本指南详细说明了如何使用PM2部署和管理NocoBase应用，包括PM2配置文件的编写方法、进程管理命令、集群模式配置、日志管理功能、环境变量配置以及PM2监控面板的使用。

NocoBase通过内置的PM2支持，提供了强大的进程管理功能，包括应用的启动、停止、重启和监控。通过PM2的集群模式，可以实现多核CPU的负载均衡，提高应用的性能和可靠性。同时，NocoBase提供了完善的日志管理和环境变量配置功能，确保生产环境的安全性和可维护性。

**Section sources**
- [package.json](file://package.json#L19-L21)
- [packages/core/cli/src/commands/pm2.js](file://packages/core/cli/src/commands/pm2.js#L1-L38)

## PM2配置文件配置

在NocoBase中，PM2配置是通过命令行参数和环境变量来实现的，而不是传统的ecosystem.config.js文件。NocoBase的PM2配置主要通过以下方式实现：

1. **命令行参数**：通过`start`命令的参数来配置PM2
2. **环境变量**：通过`.env`文件中的环境变量来配置PM2和应用

在`package.json`文件中，可以看到PM2相关的脚本配置：

```json
"scripts": {
  "pm2": "nocobase pm2",
  "pm2-restart": "nocobase pm2-restart",
  "pm2-stop": "nocobase pm2-stop"
}
```

这些脚本直接调用了NocoBase的PM2命令，实现了对PM2的封装和集成。

**Section sources**
- [package.json](file://package.json#L19-L21)
- [packages/core/cli/src/commands/pm2.js](file://packages/core/cli/src/commands/pm2.js#L1-L38)

## 进程管理命令

NocoBase提供了丰富的进程管理命令，用于启动、停止、重启和监控应用。这些命令通过PM2实现，确保了应用的稳定运行。

### 启动应用

启动NocoBase应用有多种方式：

1. **开发模式启动**：
```bash
yarn dev
```

2. **生产模式启动**：
```bash
yarn start
```

3. **PM2模式启动**：
```bash
yarn pm2
```

在`packages/core/cli/src/commands/start.js`文件中，可以看到启动命令的实现逻辑。当指定`--daemon`参数时，会使用PM2来启动应用：

```javascript
if (opts.daemon) {
  await run('pm2', [
    'start',
    ...instancesArgs,
    `${APP_PACKAGE_ROOT}/lib/index.js`,
    '--',
    ...process.argv.slice(2),
  ]);
  process.exit();
}
```

### 停止应用

停止NocoBase应用可以使用以下命令：

```bash
yarn pm2-stop
```

这个命令会停止所有通过PM2管理的应用实例。

### 重启应用

重启NocoBase应用可以使用以下命令：

```bash
yarn pm2-restart
```

这个命令会重启所有通过PM2管理的应用实例。

### 监控应用

PM2提供了实时监控功能，可以查看应用的运行状态、CPU和内存使用情况等。使用以下命令可以查看应用状态：

```bash
yarn pm2 list
```

或者使用监控命令：

```bash
yarn pm2 monit
```

**Section sources**
- [packages/core/cli/src/commands/pm2.js](file://packages/core/cli/src/commands/pm2.js#L1-L38)
- [packages/core/cli/src/commands/start.js](file://packages/core/cli/src/commands/start.js#L126-L138)

## 集群模式配置

NocoBase支持通过PM2的集群模式实现多核CPU的负载均衡。集群模式可以通过以下方式配置：

1. **环境变量配置**：在`.env`文件中设置`CLUSTER_MODE`变量
2. **命令行参数**：在启动命令中使用`--instances`参数

在`.env.example`文件中，可以看到集群模式的配置说明：

```env
# Start application in cluster mode when the value is set (same as pm2 -i <cluster_mode>).
# Cluster mode will only work properly when plugins related to distributed architecture are enabled.
# Otherwise, the application's functionality may encounter unexpected issues.
# The cluster mode will not work in development mode either.
CLUSTER_MODE=
```

当设置`CLUSTER_MODE`变量时，NocoBase会以集群模式启动，实现多实例负载均衡。在`packages/core/cli/src/commands/start.js`文件中，可以看到集群模式的实现逻辑：

```javascript
const instances = opts.instances || process.env.CLUSTER_MODE;
const instancesArgs = instances ? ['-i', instances] : [];
```

这表明可以通过命令行参数`--instances`或环境变量`CLUSTER_MODE`来指定实例数量。

**Section sources**
- [.env.example](file://.env.example#L32-L36)
- [packages/core/cli/src/commands/start.js](file://packages/core/cli/src/commands/start.js#L113-L115)

## 日志管理

NocoBase提供了完善的日志管理功能，包括日志轮转和错误日志分析。日志管理主要通过以下方式实现：

### 日志配置

在`.env.example`文件中，可以看到日志相关的配置选项：

```env
# console | file | dailyRotateFile
LOGGER_TRANSPORT=
LOGGER_BASE_PATH=storage/logs
# error | warn | info | debug | trace
LOGGER_LEVEL=
# If LOGGER_TRANSPORT is dailyRotateFile and using days, add 'd' as the suffix.
LOGGER_MAX_FILES=
# add 'k', 'm', 'g' as the suffix.
LOGGER_MAX_SIZE=
# console | json | logfmt | delimiter
LOGGER_FORMAT=
```

这些配置选项允许用户自定义日志的输出方式、存储路径、日志级别、文件轮转策略等。

### 日志轮转

NocoBase使用`winston-daily-rotate-file`实现日志轮转功能。在`packages/core/logger/package.json`文件中，可以看到依赖了`winston-daily-rotate-file`包：

```json
"dependencies": {
  "winston-daily-rotate-file": "^5.0.0"
}
```

通过配置`LOGGER_MAX_FILES`和`LOGGER_MAX_SIZE`环境变量，可以控制日志文件的轮转策略。

### 错误日志分析

NocoBase的日志系统基于Winston实现，提供了详细的错误日志记录功能。在`packages/core/logger/src/system-logger.ts`文件中，可以看到日志系统的实现：

```javascript
export const createSystemLogger = (options: SystemLoggerOptions): SystemLogger => {
  const transport = new SystemLoggerTransport(options);
  transport.once('unpipe', () => {
    transport.close();
  });
  const logger = winston.createLogger({
    levels,
    transports: [transport],
  }) as any;
};
```

**Section sources**
- [.env.example](file://.env.example#L20-L31)
- [packages/core/logger/package.json](file://packages/core/logger/package.json#L18)
- [packages/core/logger/src/system-logger.ts](file://packages/core/logger/src/system-logger.ts#L119-L130)

## 环境变量配置

NocoBase提供了强大的环境变量配置功能，确保生产环境的安全性。环境变量配置主要通过以下方式实现：

### 环境变量管理插件

NocoBase提供了`@nocobase/plugin-environment-variables`插件，用于管理环境变量。该插件允许用户在运行时动态设置和更新环境变量。

在`packages/plugins/@nocobase/plugin-environment-variables/src/server/plugin.ts`文件中，可以看到环境变量插件的实现：

```javascript
export class PluginEnvironmentVariablesServer extends Plugin {
  async load() {
    this.registerACL();
    this.onEnvironmentSaved();
    await this.loadVariables();
  }
  
  registerACL() {
    this.app.acl.allow('environmentVariables', 'list', 'loggedIn');
    this.app.acl.registerSnippet({
      name: `pm.${this.name}`,
      actions: ['environmentVariables:*', 'app:refresh'],
    });
  }
}
```

### 环境变量存储

环境变量可以存储在数据库中，实现持久化管理。在`packages/plugins/@nocobase/plugin-environment-variables/src/server/collections/environmentVariables.ts`文件中，定义了环境变量的数据结构：

```javascript
export default defineCollection({
  name: 'environmentVariables',
  autoGenId: false,
  fields: [
    {
      type: 'string',
      name: 'name',
      primaryKey: true,
    },
    {
      type: 'string',
      name: 'type',
    },
    {
      type: 'text',
      name: 'value',
    },
  ],
});
```

### 敏感信息加密

对于敏感信息，如密码、密钥等，NocoBase提供了加密存储功能。在环境变量插件中，可以将变量类型设置为`secret`，系统会自动对值进行加密存储。

**Section sources**
- [packages/plugins/@nocobase/plugin-environment-variables/src/server/plugin.ts](file://packages/plugins/@nocobase/plugin-environment-variables/src/server/plugin.ts#L12-L43)
- [packages/plugins/@nocobase/plugin-environment-variables/src/server/collections/environmentVariables.ts](file://packages/plugins/@nocobase/plugin-environment-variables/src/server/collections/environmentVariables.ts#L13-L35)
- [packages/core/server/src/environment.ts](file://packages/core/server/src/environment.ts#L13-L47)

## PM2监控面板

NocoBase虽然没有直接集成PM2的监控面板，但提供了类似的监控功能。通过PM2的内置命令，可以实现应用性能的实时监控。

### 实时监控

使用PM2的`monit`命令可以实时监控应用的性能：

```bash
yarn pm2 monit
```

这将打开一个交互式界面，显示应用的CPU、内存使用情况，以及HTTP请求的实时统计。

### 性能指标

NocoBase集成了OpenTelemetry，提供了详细的性能指标收集功能。在`packages/core/telemetry/src/telemetry.ts`文件中，可以看到性能监控的实现：

```javascript
export class Telemetry {
  trace: Trace;
  metric: Metric;
  
  init() {
    registerInstrumentations({
      instrumentations: this.instrumentations,
    });
    
    const resource = Resource.default().merge(
      new Resource({
        [SemanticResourceAttributes.SERVICE_NAME]: this.serviceName,
        [SemanticResourceAttributes.SERVICE_VERSION]: this.version,
      }),
    );
    
    this.trace.init(resource);
    this.metric.init(resource);
  }
}
```

### 日志监控

通过配置日志级别和格式，可以实现对应用运行状态的全面监控。建议在生产环境中将`LOGGER_LEVEL`设置为`info`或`warn`，以平衡日志详细程度和性能影响。

**Section sources**
- [packages/core/telemetry/src/telemetry.ts](file://packages/core/telemetry/src/telemetry.ts#L23-L71)
- [packages/core/telemetry/src/metric.ts](file://packages/core/telemetry/src/metric.ts#L29-L86)

## 生产环境部署建议

在生产环境中部署NocoBase时，建议遵循以下最佳实践：

### 使用Docker部署

NocoBase提供了Docker部署方案，通过`docker-compose.yml`文件可以快速部署完整的应用环境。在`docker-compose.yml`文件中，定义了NocoBase应用、数据库、缓存等服务的配置。

### Nginx反向代理

建议使用Nginx作为反向代理服务器，提高应用的安全性和性能。在`docker/nocobase/nocobase.conf`文件中，提供了Nginx的配置示例：

```nginx
server {
    listen 80;
    server_name _;
    root /app/nocobase/node_modules/@nocobase/app/dist/client;
    
    location ^~ /api/ {
        proxy_pass http://127.0.0.1:13000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 安全配置

1. 将`APP_ENV`设置为`production`
2. 使用HTTPS加密通信
3. 配置适当的日志级别，避免敏感信息泄露
4. 定期备份数据库和配置文件

### 性能优化

1. 启用集群模式，充分利用多核CPU
2. 配置适当的缓存策略
3. 优化数据库查询
4. 使用CDN加速静态资源加载

**Section sources**
- [docker-compose.yml](file://docker-compose.yml#L1-L80)
- [docker/nocobase/nocobase.conf](file://docker/nocobase/nocobase.conf#L1-L90)
- [.env.example](file://.env.example#L11-L13)