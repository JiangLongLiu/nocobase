# API暴露

<cite>
**本文档中引用的文件**   
- [resourcer.ts](file://packages/core/resourcer/src/resourcer.ts)
- [resource.ts](file://packages/core/resourcer/src/resource.ts)
- [action.ts](file://packages/core/resourcer/src/action.ts)
- [middleware.ts](file://packages/core/resourcer/src/middleware.ts)
- [utils.ts](file://packages/core/resourcer/src/utils.ts)
- [simple.ts](file://examples/app/resource-actions/simple.ts)
- [global-action.ts](file://examples/app/resource-actions/global-action.ts)
- [action-with-default-options.ts](file://examples/app/resource-actions/action-with-default-options.ts)
- [action-merge-params.ts](file://examples/app/resource-actions/action-merge-params.ts)
</cite>

## 目录
1. [简介](#简介)
2. [核心组件](#核心组件)
3. [资源与操作概念](#资源与操作概念)
4. [API路由生成规则](#api路由生成规则)
5. [请求处理流程](#请求处理流程)
6. [自定义API行为](#自定义api行为)
7. [API版本控制与安全性](#api版本控制与安全性)

## 简介
NocoBase的Resourcer模块是一个强大的数据访问API暴露机制，它将数据模型自动转换为RESTful API端点。该模块通过资源（Resource）和操作（Action）的概念，实现了灵活的API定义和处理机制。Resourcer模块基于Koa框架构建，利用中间件机制实现了请求的解析、路由匹配和响应处理。

## 核心组件

Resourcer模块由几个核心组件构成：ResourceManager、Resource、Action和Middleware。这些组件协同工作，将数据模型转换为可用的API端点。

**本文档中引用的文件**   
- [resourcer.ts](file://packages/core/resourcer/src/resourcer.ts)
- [resource.ts](file://packages/core/resourcer/src/resource.ts)
- [action.ts](file://packages/core/resourcer/src/action.ts)
- [middleware.ts](file://packages/core/resourcer/src/middleware.ts)

## 资源与操作概念

### 资源（Resource）
资源是Resourcer模块中的核心概念之一，代表一个数据实体或数据集合。每个资源都有一个唯一的名称，并可以定义其类型（如'single'、'hasOne'、'hasMany'等）。资源可以包含多个操作，并可以配置中间件来处理特定的业务逻辑。

```mermaid
classDiagram
class Resource {
+string name
+ResourceType type
+Map<ActionName, Action> actions
+Array<Middleware> middlewares
+ResourceOptions options
+except : Array<ActionName>
+resourcer : ResourceManager
+getName() string
+getExcept() Array<ActionName>
+addAction(name, handler) void
+getAction(action) Action
}
class ResourceManager {
+ResourceManagerOptions options
+Map<string, Resource> resources
+Map<ActionName, any> actionHandlers
+Map<string, any> middlewareHandlers
+Toposort<any> middlewares
+define(options) Resource
+isDefined(name) boolean
+registerActionHandler(name, handler) void
+getResource(name) Resource
+getAction(name, action) Action
+middleware(options) HandlerType
+execute(options, context, next) Promise<any>
}
ResourceManager --> Resource : "包含"
```

**图源**
- [resource.ts](file://packages/core/resourcer/src/resource.ts#L61-L126)
- [resourcer.ts](file://packages/core/resourcer/src/resourcer.ts#L161-L429)

### 操作（Action）
操作是资源上可执行的具体行为，如'list'（查看列表）、'create'（新增数据）、'get'（查看数据详情）、'update'（更新数据）和'delete'（删除数据）。每个操作可以定义默认参数、中间件和处理函数。

```mermaid
classDiagram
class Action {
+ActionName name
+Resource resource
+ActionOptions options
+ActionParams params
+Array<Middleware> middlewares
+handler : any
+context : ActionContext
+actionName : string
+resourceName : string
+sourceId : any
+clone() Action
+setContext(context) void
+mergeParams(params, strategies) void
+setResource(resource) Action
+getResource() Resource
+getOptions() ActionOptions
+setName(name) Action
+getName() ActionName
+getMiddlewareHandlers() Array<HandlerType>
+getHandler() HandlerType
+getHandlers() Array<HandlerType>
+execute(context, next) Promise<any>
}
class ActionOptions {
+any values
+string[] fields
+string[] appends
+string[] except
+string[] whitelist
+string[] blacklist
+FilterOptions filter
+string[] sort
+number page
+number pageSize
+number maxPageSize
+MiddlewareType middleware
+MiddlewareType middlewares
+HandlerType handler
}
class ActionParams {
+any filterByTk
+string[] fields
+string[] appends
+string[] except
+string[] whitelist
+string[] blacklist
+FilterOptions filter
+string[] sort
+number page
+number pageSize
+any values
+string resourceName
+string resourceIndex
+string associatedName
+string associatedIndex
+any associated
+string actionName
}
Action --> ActionOptions : "包含"
Action --> ActionParams : "包含"
Resource --> Action : "包含"
```

**图源**
- [action.ts](file://packages/core/resourcer/src/action.ts#L212-L409)

## API路由生成规则

Resourcer模块通过解析请求路径和方法来生成API路由。路由规则基于资源名称、操作名称和请求方法的组合。

### 路由匹配逻辑
路由匹配逻辑在`utils.ts`文件中的`parseRequest`函数中实现。该函数根据请求路径、方法和配置选项来解析出资源名称、操作名称和相关参数。

```mermaid
flowchart TD
Start([开始解析请求]) --> CheckResourcerPath["检查是否为/resourcer/:rest(.*)格式"]
CheckResourcerPath --> |是| ParseRestPath["解析rest参数"]
CheckResourcerPath --> |否| CheckPrefix["检查前缀"]
ParseRestPath --> ExtractResourceAction["提取资源和操作名称"]
ExtractResourceAction --> ReturnParams["返回解析参数"]
CheckPrefix --> BuildRegexp["构建正则表达式"]
BuildRegexp --> MatchPath["匹配请求路径"]
MatchPath --> |匹配成功| ExtractParams["提取路径参数"]
MatchPath --> |匹配失败| ReturnFalse["返回false"]
ExtractParams --> DetermineAction["根据请求方法确定操作"]
DetermineAction --> ReturnParams
ReturnParams --> End([结束])
ReturnFalse --> End
```

**图源**
- [utils.ts](file://packages/core/resourcer/src/utils.ts#L55-L213)

### 默认路由映射
Resourcer模块定义了不同资源类型（如'single'、'hasOne'、'hasMany'等）的默认路由映射规则。这些规则决定了特定路径和HTTP方法组合对应的操作。

```mermaid
erDiagram
RESOURCE_TYPE {
string type PK
string description
}
ROUTE_PATTERN {
string pattern PK
string description
}
HTTP_METHOD {
string method PK
string description
}
ACTION {
string action PK
string description
}
RESOURCE_TYPE ||--o{ ROUTE_PATTERN : "has"
ROUTE_PATTERN ||--o{ METHOD_ACTION_MAPPING : "has"
HTTP_METHOD ||--o{ METHOD_ACTION_MAPPING : "has"
METHOD_ACTION_MAPPING }|--|| ACTION : "maps to"
class METHOD_ACTION_MAPPING {
string resourceType
string routePattern
string httpMethod
string action
}
```

**图源**
- [utils.ts](file://packages/core/resourcer/src/utils.ts#L91-L168)

## 请求处理流程

Resourcer模块的请求处理流程是一个典型的中间件管道，从请求进入开始，经过多个处理阶段，最终返回响应。

### 处理流程概述
请求处理流程始于`resourcer.middleware`方法，该方法创建了一个Koa中间件，负责解析请求、查找对应的资源和操作，并执行相应的处理函数。

```mermaid
sequenceDiagram
participant Client as "客户端"
participant Middleware as "Resourcer中间件"
participant ResourceManager as "ResourceManager"
participant Resource as "Resource"
participant Action as "Action"
participant Handler as "处理函数"
Client->>Middleware : 发送HTTP请求
Middleware->>Middleware : 解析请求路径和参数
Middleware->>ResourceManager : 根据资源名称获取Resource
ResourceManager-->>Middleware : 返回Resource实例
Middleware->>Resource : 根据操作名称获取Action
Resource-->>Middleware : 返回Action实例
Middleware->>Action : 设置上下文和参数
Action->>Action : 合并参数默认参数、请求参数等
Action->>Handler : 执行处理函数
Handler-->>Action : 返回处理结果
Action-->>Middleware : 返回响应
Middleware-->>Client : 发送HTTP响应
```

**图源**
- [resourcer.ts](file://packages/core/resourcer/src/resourcer.ts#L311-L391)

### 参数合并机制
Resourcer模块实现了复杂的参数合并机制，允许从多个来源（如全局配置、资源配置、中间件、请求参数等）合并操作参数。

```mermaid
flowchart TD
Start([开始参数合并]) --> DefaultOptions["获取操作默认参数"]
DefaultOptions --> MiddlewareParams["获取中间件设置的参数"]
MiddlewareParams --> ACLParams["获取ACL权限参数"]
ACLParams --> RequestParams["获取请求参数查询字符串、请求体"]
RequestParams --> MergeStrategy["应用合并策略"]
MergeStrategy --> FilterMerge["过滤条件：andMerge"]
MergeStrategy --> FieldsMerge["字段：intersect"]
MergeStrategy --> AppendsMerge["附加字段：union"]
MergeStrategy --> ExceptMerge["排除字段：union"]
MergeStrategy --> SortMerge["排序：overwrite"]
FilterMerge --> FinalParams["生成最终参数"]
FieldsMerge --> FinalParams
AppendsMerge --> FinalParams
ExceptMerge --> FinalParams
SortMerge --> FinalParams
FinalParams --> End([结束参数合并])
```

**图源**
- [action.ts](file://packages/core/resourcer/src/action.ts#L289-L307)
- [action-merge-params.ts](file://examples/app/resource-actions/action-merge-params.ts)

## 自定义API行为

Resourcer模块提供了多种方式来自定义API行为，包括注册全局操作、定义资源特定操作和使用中间件。

### 全局操作注册
通过`registerActionHandlers`方法，可以注册全局可用的操作，这些操作可以在任何资源中使用。

```mermaid
classDiagram
class ResourceManager {
+registerActionHandlers(handlers) void
+registerActionHandler(name, handler) void
+getRegisteredHandler(name) HandlerType
+getRegisteredHandlers() Map<ActionName, any>
}
class ExampleGlobalAction {
+async import(ctx, next) void
+async export(ctx, next) void
}
ResourceManager --> ExampleGlobalAction : "注册"
```

**图源**
- [resourcer.ts](file://packages/core/resourcer/src/resourcer.ts#L252-L267)
- [global-action.ts](file://examples/app/resource-actions/global-action.ts)

### 资源特定操作
可以在定义资源时指定特定的操作，这些操作可以覆盖全局操作的默认行为。

```mermaid
classDiagram
class Resource {
+actions : Map<ActionName, Action>
+addAction(name, handler) void
+getAction(action) Action
}
class ActionWithDefaultOptions {
+filter : FilterOptions
+fields : string[]
+handler : HandlerType
}
Resource --> ActionWithDefaultOptions : "包含"
```

**图源**
- [resource.ts](file://packages/core/resourcer/src/resource.ts#L100-L112)
- [action-with-default-options.ts](file://examples/app/resource-actions/action-with-default-options.ts)

### 中间件机制
Resourcer模块支持中间件机制，允许在请求处理过程中插入自定义逻辑。

```mermaid
classDiagram
class Middleware {
+MiddlewareOptions options
+Array<HandlerType> middlewares
+getHandler() HandlerType
+use(middleware) void
+disuse(middleware) void
+canAccess(name) boolean
+toInstanceArray(middlewares) Array<Middleware>
}
class ResourceManager {
+middlewares : Toposort<any>
+use(middlewares, options) void
+getMiddlewares() Array<HandlerType>
}
ResourceManager --> Middleware : "使用"
```

**图源**
- [middleware.ts](file://packages/core/resourcer/src/middleware.ts#L33-L94)
- [resourcer.ts](file://packages/core/resourcer/src/resourcer.ts#L304-L310)

## API版本控制与安全性

### API版本控制
虽然Resourcer模块本身不直接提供版本控制功能，但可以通过前缀配置实现简单的版本控制。

```mermaid
flowchart TD
Start([API请求]) --> CheckPrefix["检查API前缀"]
CheckPrefix --> |/api/v1/*| V1Handler["调用v1版本处理逻辑"]
CheckPrefix --> |/api/v2/*| V2Handler["调用v2版本处理逻辑"]
CheckPrefix --> |其他| DefaultHandler["调用默认处理逻辑"]
V1Handler --> End
V2Handler --> End
DefaultHandler --> End
```

**图源**
- [resourcer.ts](file://packages/core/resourcer/src/resourcer.ts#L79-L83)

### 安全性考虑
Resourcer模块通过与ACL（访问控制列表）模块集成来实现安全性控制。权限检查通常在中间件阶段完成。

```mermaid
sequenceDiagram
participant Client as "客户端"
participant Resourcer as "Resourcer中间件"
participant ACL as "ACL中间件"
participant Resource as "Resource"
participant Action as "Action"
Client->>Resourcer : 发送请求
Resourcer->>ACL : 调用ACL中间件
ACL->>ACL : 检查用户权限
ACL->>ACL : 根据权限设置参数
ACL-->>Resourcer : 返回继续
Resourcer->>Resource : 查找资源
Resource->>Action : 查找操作
Action->>Action : 执行权限检查
Action-->>Client : 返回响应
```

**图源**
- [action-merge-params.ts](file://examples/app/resource-actions/action-merge-params.ts#L44-L61)