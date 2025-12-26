# Vitest 配置

<cite>
**本文档中引用的文件**  
- [vitest.config.mts](file://vitest.config.mts)
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs)
- [packages/core/test/setup/client.ts](file://packages/core/test/setup/client.ts)
- [packages/core/test/setup/server.ts](file://packages/core/test/setup/server.ts)
- [package.json](file://package.json)
- [tsconfig.json](file://tsconfig.json)
</cite>

## 目录
1. [简介](#简介)
2. [项目结构与测试组织](#项目结构与测试组织)
3. [核心配置详解](#核心配置详解)
4. [测试环境配置](#测试环境配置)
5. [模块模拟与别名处理](#模块模拟与别名处理)
6. [覆盖率报告配置](#覆盖率报告配置)
7. [测试匹配模式](#测试匹配模式)
8. [TypeScript 与 ES 模块支持](#typescript-与-es-模块支持)
9. [不同测试类型的配置示例](#不同测试类型的配置示例)
10. [测试钩子与全局设置](#测试钩子与全局设置)
11. [性能优化配置](#性能优化配置)
12. [常见问题与调试技巧](#常见问题与调试技巧)

## 简介
本文档详细介绍了 NocoBase 项目中 Vitest 测试框架的配置方案。通过分析 `vitest.config.mts` 文件及其相关实现，深入解析了测试配置的各个关键部分，包括测试环境设置、模块别名处理、覆盖率报告、测试匹配模式等。文档还提供了针对不同类型测试的配置示例，以及性能优化和问题排查的实用建议。

**Section sources**
- [vitest.config.mts](file://vitest.config.mts#L1-L4)
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L1-L271)

## 项目结构与测试组织
NocoBase 项目采用 Lerna 管理的多包结构，测试文件主要分布在各个包的 `src/__tests__` 目录下。项目通过 Vitest 进行单元测试和集成测试，配置文件位于项目根目录。

```mermaid
graph TD
A[项目根目录] --> B[vitest.config.mts]
A --> C[packages/]
C --> D[core/]
C --> E[plugins/]
D --> F[test/]
F --> G[vitest.mjs]
F --> H[setup/]
H --> I[client.ts]
H --> J[server.ts]
```

**Diagram sources**
- [vitest.config.mts](file://vitest.config.mts#L1-L4)
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L1-L271)

**Section sources**
- [vitest.config.mts](file://vitest.config.mts#L1-L4)
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L1-L271)

## 核心配置详解
Vitest 配置通过 `@nocobase/test/vitest.mjs` 文件中的 `defineConfig` 函数实现。该函数根据环境变量 `TEST_ENV` 的值，合并通用配置与特定环境配置。

```mermaid
classDiagram
class defineConfig {
+defineCommonConfig() Config
+defineServerConfig() Config
+defineClientConfig() Config
+getFilterInclude(isServer, isCoverage) Object
+getReportsDirectory(isServer) String
}
defineConfig --> defineCommonConfig : "调用"
defineConfig --> defineServerConfig : "调用"
defineConfig --> defineClientConfig : "调用"
```

**Diagram sources**
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L229-L270)

**Section sources**
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L229-L270)

## 测试环境配置
测试环境配置分为服务端和客户端两种模式，通过 `TEST_ENV` 环境变量进行区分。服务端测试使用 Node.js 环境，客户端测试使用 jsdom 环境。

```mermaid
stateDiagram-v2
[*] --> 初始化
初始化 --> 服务端测试 : TEST_ENV=server-side
初始化 --> 客户端测试 : TEST_ENV 未设置
服务端测试 --> 执行测试 : 使用 server.ts 设置
客户端测试 --> 执行测试 : 使用 client.ts 设置
```

**Diagram sources**
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L230-L232)
- [packages/core/test/setup/server.ts](file://packages/core/test/setup/server.ts#L1-L6)
- [packages/core/test/setup/client.ts](file://packages/core/test/setup/client.ts#L1-L68)

**Section sources**
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L115-L151)
- [packages/core/test/setup/server.ts](file://packages/core/test/setup/server.ts#L1-L6)
- [packages/core/test/setup/client.ts](file://packages/core/test/setup/client.ts#L1-L68)

## 模块模拟与别名处理
配置通过 `tsConfigPathsToAlias` 函数将 TypeScript 的路径映射转换为 Vite 的别名配置，支持模块的路径别名解析。

```mermaid
flowchart TD
A[读取 tsconfig.paths.json] --> B[解析 paths 配置]
B --> C[转换为 Vite 别名格式]
C --> D[添加特殊别名映射]
D --> E[返回别名数组]
```

**Diagram sources**
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L18-L50)

**Section sources**
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L18-L50)

## 覆盖率报告配置
覆盖率配置使用 Istanbul 作为提供者，包含详细的包含和排除规则，确保只对源代码进行覆盖率分析。

```mermaid
erDiagram
COVERAGE_CONFIG {
string provider PK
array include
array exclude
string reportsDirectory
}
COVERAGE_CONFIG ||--o{ INCLUDE_RULE : "包含"
COVERAGE_CONFIG ||--o{ EXCLUDE_RULE : "排除"
```

**Diagram sources**
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L86-L103)

**Section sources**
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L86-L103)

## 测试匹配模式
测试匹配模式通过 `include` 和 `exclude` 配置项定义，精确控制哪些文件被纳入测试范围。

```mermaid
flowchart TD
A[测试匹配模式] --> B[包含模式]
A --> C[排除模式]
B --> D["packages/**/src/**/__tests__/**/*.test.{ts,tsx}"]
C --> E["**/node_modules/**"]
C --> F["**/dist/**"]
C --> G["**/lib/**"]
C --> H["**/e2e/**"]
```

**Diagram sources**
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L64-L85)

**Section sources**
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L64-L85)

## TypeScript 与 ES 模块支持
项目通过 `tsconfig.json` 配置 TypeScript 编译选项，支持 ES 模块和现代 JavaScript 特性。

```mermaid
classDiagram
class tsconfig {
+compilerOptions
+ts-node
+include
+exclude
}
tsconfig --> compilerOptions : "包含"
compilerOptions --> esModuleInterop : "true"
compilerOptions --> moduleResolution : "node"
compilerOptions --> target : "esnext"
compilerOptions --> module : "esnext"
```

**Diagram sources**
- [tsconfig.json](file://tsconfig.json#L1-L37)

**Section sources**
- [tsconfig.json](file://tsconfig.json#L1-L37)

## 不同测试类型的配置示例
项目提供了针对不同测试类型（单元测试、集成测试）的配置示例，通过不同的脚本命令调用。

```mermaid
sequenceDiagram
participant 用户
participant package_json
participant vitest_config
用户->>package_json : 执行 yarn test : server
package_json->>vitest_config : 设置 TEST_ENV=server-side
vitest_config->>vitest_config : 合并服务端配置
vitest_config-->>用户 : 执行服务端测试
用户->>package_json : 执行 yarn test : client
package_json->>vitest_config : 不设置 TEST_ENV
vitest_config->>vitest_config : 合并客户端配置
vitest_config-->>用户 : 执行客户端测试
```

**Diagram sources**
- [package.json](file://package.json#L28-L31)
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L230-L232)

**Section sources**
- [package.json](file://package.json#L28-L31)
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L230-L232)

## 测试钩子与全局设置
通过 setupFiles 配置项引入测试钩子文件，进行全局测试环境的初始化设置。

```mermaid
flowchart TD
A[测试开始] --> B[执行 setupFiles]
B --> C[client.ts 或 server.ts]
C --> D[设置环境变量]
C --> E[模拟全局对象]
C --> F[配置测试库]
D --> G[执行测试用例]
E --> G
F --> G
```

**Diagram sources**
- [packages/core/test/setup/client.ts](file://packages/core/test/setup/client.ts#L1-L68)
- [packages/core/test/setup/server.ts](file://packages/core/test/setup/server.ts#L1-L6)

**Section sources**
- [packages/core/test/setup/client.ts](file://packages/core/test/setup/client.ts#L1-L68)
- [packages/core/test/setup/server.ts](file://packages/core/test/setup/server.ts#L1-L6)

## 性能优化配置
配置中包含多项性能优化设置，如超时时间、并行执行和缓存配置。

```mermaid
graph TB
A[性能优化] --> B[超时设置]
A --> C[并行执行]
A --> D[缓存配置]
B --> E[testTimeout: 300000]
B --> F[hookTimeout: 300000]
C --> G[默认并行]
D --> H[覆盖率报告目录]
```

**Diagram sources**
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L61-L62)
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L264-L267)

**Section sources**
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L61-L62)
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L264-L267)

## 常见问题与调试技巧
针对常见的测试配置问题，提供以下调试技巧：

```mermaid
flowchart TD
A[常见问题] --> B[环境变量未设置]
A --> C[路径别名解析失败]
A --> D[全局对象未模拟]
B --> E[检查 TEST_ENV 变量]
C --> F[检查 tsconfig.paths.json]
D --> G[检查 setupFiles 配置]
```

**Diagram sources**
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L230-L232)
- [packages/core/test/setup/client.ts](file://packages/core/test/setup/client.ts#L1-L68)

**Section sources**
- [packages/core/test/vitest.mjs](file://packages/core/test/vitest.mjs#L230-L232)
- [packages/core/test/setup/client.ts](file://packages/core/test/setup/client.ts#L1-L68)