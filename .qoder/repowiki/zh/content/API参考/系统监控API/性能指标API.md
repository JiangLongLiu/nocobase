# 性能指标API

<cite>
**本文档中引用的文件**  
- [telemetry.ts](file://packages/core/app/src/config/telemetry.ts)
- [telemetry.ts](file://packages/core/telemetry/src/telemetry.ts)
- [trace.ts](file://packages/core/telemetry/src/trace.ts)
- [metric.ts](file://packages/core/telemetry/src/metric.ts)
- [helper.ts](file://packages/core/server/src/helper.ts)
- [index.js](file://benchmark/nocobase-server/index.js)
</cite>

## 目录
1. [简介](#简介)
2. [性能指标收集](#性能指标收集)
3. [分布式追踪](#分布式追踪)
4. [指标聚合与采样](#指标聚合与采样)
5. [监控系统集成](#监控系统集成)
6. [性能基线与异常分析](#性能基线与异常分析)
7. [配置与环境变量](#配置与环境变量)
8. [性能测试工具](#性能测试工具)

## 简介
NocoBase 提供了一套完整的性能监控和追踪系统，基于 OpenTelemetry 标准实现。该系统能够收集 CPU 使用率、内存占用、请求延迟、数据库查询性能等关键性能指标，并支持分布式追踪功能，帮助开发者分析性能瓶颈。系统通过可配置的指标收集器和追踪处理器，将数据导出到各种监控工具，如 Grafana 和 Jaeger。

**Section sources**
- [telemetry.ts](file://packages/core/app/src/config/telemetry.ts)
- [telemetry.ts](file://packages/core/telemetry/src/telemetry.ts)

## 性能指标收集
NocoBase 的性能指标收集系统基于 OpenTelemetry SDK Metrics 实现，能够收集和导出各种性能指标。系统提供了灵活的指标读取器（Metric Reader）机制，支持多种导出方式。

```mermaid
classDiagram
class Metric {
+meterName : string
+version : string
+readerName : string | string[]
+readers : Registry<GetMetricReader>
+provider : MeterProvider
+views : View[]
+init(resource : Resource)
+registerReader(name : string, reader : GetMetricReader)
+getReader(name : string)
+addView(...view : View[])
+getMeter(name? : string, version? : string)
+start()
+shutdown()
}
class MetricOptions {
+meterName? : string
+version? : string
+readerName? : string | string[]
}
Metric --> MetricOptions : "使用"
Metric --> Registry : "包含"
Metric --> MeterProvider : "使用"
Metric --> View : "包含"
```

**Diagram sources **
- [metric.ts](file://packages/core/telemetry/src/metric.ts)

**Section sources**
- [metric.ts](file://packages/core/telemetry/src/metric.ts)

## 分布式追踪
NocoBase 的分布式追踪系统基于 OpenTelemetry SDK Trace 实现，支持跨服务的请求追踪。系统通过追踪处理器（Span Processor）将追踪数据导出到不同的后端系统。

```mermaid
classDiagram
class Trace {
+processorName : string | string[]
+processors : Registry<GetSpanProcessor>
+tracerName : string
+version : string
+provider : NodeTracerProvider
+init(resource : Resource)
+registerProcessor(name : string, processor : GetSpanProcessor)
+getProcessor(name : string)
+getTracer(name? : string, version? : string)
+start()
+shutdown()
}
class TraceOptions {
+tracerName? : string
+version? : string
+processorName? : string | string[]
}
Trace --> TraceOptions : "使用"
Trace --> Registry : "包含"
Trace --> NodeTracerProvider : "使用"
```

**Diagram sources **
- [trace.ts](file://packages/core/telemetry/src/trace.ts)

**Section sources**
- [trace.ts](file://packages/core/telemetry/src/trace.ts)

## 指标聚合与采样
NocoBase 的性能监控系统支持灵活的指标聚合和采样策略。系统通过视图（View）机制定义指标的聚合方式，并通过配置控制采样率和存储周期。

```mermaid
flowchart TD
Start([开始]) --> ConfigureViews["配置指标视图"]
ConfigureViews --> RegisterReader["注册指标读取器"]
RegisterReader --> InitResource["初始化资源"]
InitResource --> SetGlobalProvider["设置全局MeterProvider"]
SetGlobalProvider --> AddMetricReader["添加指标读取器"]
AddMetricReader --> CollectMetrics["收集性能指标"]
CollectMetrics --> ExportMetrics["导出指标数据"]
ExportMetrics --> End([结束])
```

**Diagram sources **
- [metric.ts](file://packages/core/telemetry/src/metric.ts)

**Section sources**
- [metric.ts](file://packages/core/telemetry/src/metric.ts)

## 监控系统集成
NocoBase 支持与多种监控工具集成，包括 Grafana 和 Jaeger。通过配置不同的指标读取器和追踪处理器，可以将性能数据导出到相应的监控系统。

```mermaid
graph TB
subgraph "NocoBase 应用"
Telemetry[遥测系统]
Metric[指标收集]
Trace[分布式追踪]
end
subgraph "监控系统"
Grafana[Grafana]
Jaeger[Jaeger]
Prometheus[Prometheus]
end
Metric --> Grafana
Metric --> Prometheus
Trace --> Jaeger
Telemetry --> |配置| Exporters[导出器]
Exporters --> Grafana
Exporters --> Jaeger
Exporters --> Prometheus
```

**Diagram sources **
- [telemetry.ts](file://packages/core/telemetry/src/telemetry.ts)

**Section sources**
- [telemetry.ts](file://packages/core/telemetry/src/telemetry.ts)

## 性能基线与异常分析
NocoBase 提供了性能基线参考和异常指标解读方法，帮助用户进行系统优化和容量规划。系统通过性能直方图（Histogram）记录关键操作的执行时间分布。

```mermaid
sequenceDiagram
participant App as "NocoBase 应用"
participant Perf as "性能监控"
participant User as "用户"
App->>Perf : 启用性能钩子
Perf->>App : 创建性能直方图
App->>Perf : 记录操作耗时
Perf->>Perf : 更新直方图数据
User->>App : 请求性能数据
App->>Perf : 获取直方图
Perf-->>App : 返回性能数据
App-->>User : 显示性能指标
```

**Diagram sources **
- [helper.ts](file://packages/core/server/src/helper.ts)

**Section sources**
- [helper.ts](file://packages/core/server/src/helper.ts)

## 配置与环境变量
NocoBase 的性能监控系统通过环境变量进行配置，支持灵活的启用和配置选项。主要配置项包括指标读取器和追踪处理器的选择。

```mermaid
erDiagram
CONFIGURATION {
string TELEMETRY_ENABLED PK
string TELEMETRY_METRIC_READER
string TELEMETRY_TRACE_PROCESSOR
string SERVICE_NAME
string SERVICE_VERSION
}
METRIC_READER {
string NAME PK
string EXPORTER_TYPE
string EXPORT_INTERVAL
boolean ENABLED
}
TRACE_PROCESSOR {
string NAME PK
string EXPORTER_TYPE
string BATCH_SIZE
string SCHEDULE_DELAY
boolean ENABLED
}
CONFIGURATION ||--o{ METRIC_READER : "使用"
CONFIGURATION ||--o{ TRACE_PROCESSOR : "使用"
```

**Diagram sources **
- [telemetry.ts](file://packages/core/app/src/config/telemetry.ts)

**Section sources**
- [telemetry.ts](file://packages/core/app/src/config/telemetry.ts)

## 性能测试工具
NocoBase 提供了专门的性能测试工具，用于评估系统在不同负载下的表现。这些工具可以帮助开发者识别性能瓶颈并进行优化。

```mermaid
flowchart LR
TestScript[性能测试脚本] --> CLI["NocoBase CLI"]
CLI --> Benchmark["基准测试"]
CLI --> PerfTest["性能测试"]
Benchmark --> K6[k6 工具]
PerfTest --> TSX[tsx 执行器]
K6 --> Results["测试结果"]
TSX --> Results
Results --> Analysis["性能分析"]
Analysis --> Optimization["系统优化"]
```

**Diagram sources **
- [index.js](file://benchmark/nocobase-server/index.js)

**Section sources**
- [index.js](file://benchmark/nocobase-server/index.js)