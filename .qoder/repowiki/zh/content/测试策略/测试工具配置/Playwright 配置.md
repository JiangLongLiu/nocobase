# Playwright 配置

<cite>
**本文档中引用的文件**  
- [playwright.config.ts](file://playwright.config.ts)
- [packages/core/test/src/e2e/defineConfig.ts](file://packages/core/test/src/e2e/defineConfig.ts)
- [packages/core/test/src/e2e/e2eUtils.ts](file://packages/core/test/src/e2e/e2eUtils.ts)
- [packages/core/test/playwright/tests/auth.setup.ts](file://packages/core/test/playwright/tests/auth.setup.ts)
- [packages/core/test/package.json](file://packages/core/test/package.json)
- [.env.e2e.example](file://.env.e2e.example)
</cite>

## 目录
1. [简介](#简介)
2. [核心配置选项](#核心配置选项)
3. [多浏览器测试环境配置](#多浏览器测试环境配置)
4. [测试项目组织与环境配置](#测试项目组织与环境配置)
5. [UI交互测试配置最佳实践](#ui交互测试配置最佳实践)
6. [视觉回归与性能测试集成](#视觉回归与性能测试集成)
7. [环境变量与外部配置](#环境变量与外部配置)

## 简介
Playwright 是 NocoBase 项目中用于端到端测试的核心框架。本配置文档详细介绍了 `playwright.config.ts` 文件中的各项配置选项，包括浏览器类型选择、测试执行模式、视频录制和截图配置等。通过本配置，开发者可以有效地组织多浏览器测试环境，实现跨浏览器兼容性测试，并优化UI交互测试的等待策略、超时设置和网络拦截配置。

## 核心配置选项

Playwright 配置通过 `@nocobase/test/e2e` 模块中的 `defineConfig` 函数进行定义。该配置包含了超时设置、期望断言配置、测试目录匹配规则等关键参数。配置中设置了全局超时时间为60分钟，测试超时时间根据是否在CI环境中运行而动态调整（CI环境为60秒，本地为30秒）。

```mermaid
flowchart TD
Start([配置入口]) --> DefineConfig["defineConfig 函数"]
DefineConfig --> Timeout["超时设置"]
DefineConfig --> Expect["期望断言配置"]
DefineConfig --> TestDir["测试目录配置"]
DefineConfig --> TestMatch["测试文件匹配"]
DefineConfig --> Reporter["报告生成器"]
DefineConfig --> Use["使用配置"]
DefineConfig --> Projects["测试项目"]
Timeout --> GlobalTimeout["全局超时: 60分钟"]
Timeout --> TestTimeout["测试超时: 30/60秒"]
Expect --> ExpectTimeout["期望超时: 10秒"]
TestDir --> DirPath["测试目录: packages"]
TestMatch --> MatchPattern["匹配模式: e2e/__e2e__"]
Reporter --> CIReporter["CI环境: blob 报告"]
Reporter --> LocalReporter["本地环境: html 报告"]
Use --> BaseURL["基础URL"]
Use --> Trace["跟踪: 首次重试时开启"]
Projects --> AuthProject["authSetup 项目"]
Projects --> ChromiumProject["chromium 项目"]
```

**图源**  
- [packages/core/test/src/e2e/defineConfig.ts](file://packages/core/test/src/e2e/defineConfig.ts#L12-L76)

**本节来源**  
- [playwright.config.ts](file://playwright.config.ts#L1-L4)
- [packages/core/test/src/e2e/defineConfig.ts](file://packages/core/test/src/e2e/defineConfig.ts#L12-L76)

## 多浏览器测试环境配置

NocoBase 的 Playwright 配置支持多浏览器测试环境，通过 `projects` 配置项实现。当前配置主要针对 Chromium 浏览器，但通过 Playwright 的设备模拟功能，可以轻松扩展到其他浏览器类型。配置中使用了 `devices['Desktop Chrome']` 来模拟桌面版 Chrome 浏览器的环境。

测试项目中的 `chromium` 项目配置了特定的上下文选项，包括剪贴板读写权限，这对于测试涉及剪贴板操作的功能至关重要。同时，通过 `storageState` 配置，实现了登录状态的持久化，避免了每次测试都需要重新登录的开销。

```mermaid
classDiagram
class PlaywrightConfig {
+timeout : number
+expect : ExpectConfig
+globalTimeout : number
+testDir : string
+testMatch : string
+fullyParallel : boolean
+forbidOnly : boolean
+retries : number
+workers : number
+maxFailures : number
+reporter : ReporterConfig
+outputDir : string
+use : UseConfig
+projects : ProjectConfig[]
}
class ExpectConfig {
+timeout : number
}
class UseConfig {
+baseURL : string
+trace : string
}
class ProjectConfig {
+name : string
+testDir : string
+testMatch : string
+use : UseConfig
+dependencies : string[]
}
class ChromiumConfig {
+...devices['Desktop Chrome']
+storageState : string
+contextOptions : ContextOptions
}
class ContextOptions {
+permissions : string[]
}
PlaywrightConfig --> ExpectConfig : "包含"
PlaywrightConfig --> UseConfig : "包含"
PlaywrightConfig --> ProjectConfig : "包含多个"
ProjectConfig --> ChromiumConfig : "使用"
ChromiumConfig --> ContextOptions : "包含"
```

**图源**  
- [packages/core/test/src/e2e/defineConfig.ts](file://packages/core/test/src/e2e/defineConfig.ts#L56-L74)

**本节来源**  
- [packages/core/test/src/e2e/defineConfig.ts](file://packages/core/test/src/e2e/defineConfig.ts#L56-L74)
- [packages/core/test/playwright/tests/auth.setup.ts](file://packages/core/test/playwright/tests/auth.setup.ts#L4-L21)

## 测试项目组织与环境配置

Playwright 配置通过测试项目（test projects）的方式组织测试流程。当前配置定义了两个主要的测试项目：`authSetup` 和 `chromium`。`authSetup` 项目专门用于设置认证状态，而 `chromium` 项目则依赖于 `authSetup` 项目，确保所有测试都在已认证的状态下运行。

这种项目依赖关系的配置方式，实现了测试环境的预设置，大大提高了测试效率。通过 `dependencies` 字段，Playwright 能够确保 `authSetup` 项目在 `chromium` 项目之前执行，从而为后续测试提供必要的认证状态。

```mermaid
sequenceDiagram
participant CI as CI环境
participant Config as Playwright配置
participant Auth as authSetup项目
participant Chromium as chromium项目
participant Browser as 浏览器
CI->>Config : 检测CI环境
Config->>Config : 设置forbidOnly=true
Config->>Config : retries=2
Config->>Config : workers=1
Config->>Auth : 执行认证设置
Auth->>Browser : 导航到首页
Browser-->>Auth : 页面加载完成
Auth->>Browser : 填写登录表单
Auth->>Browser : 点击登录按钮
Browser-->>Auth : 登录成功
Auth->>Browser : 设置localStorage
Auth->>Browser : 保存存储状态
Auth-->>Config : 认证完成
Config->>Chromium : 开始执行测试
Chromium->>Browser : 使用已保存的认证状态
loop 每个测试用例
Chromium->>Browser : 执行测试步骤
Browser-->>Chromium : 返回结果
Chromium->>Chromium : 断言验证
end
```

**图源**  
- [packages/core/test/src/e2e/defineConfig.ts](file://packages/core/test/src/e2e/defineConfig.ts#L57-L74)
- [packages/core/test/playwright/tests/auth.setup.ts](file://packages/core/test/playwright/tests/auth.setup.ts#L4-L21)

**本节来源**  
- [packages/core/test/src/e2e/defineConfig.ts](file://packages/core/test/src/e2e/defineConfig.ts#L57-L74)
- [packages/core/test/playwright/tests/auth.setup.ts](file://packages/core/test/playwright/tests/auth.setup.ts#L4-L21)

## UI交互测试配置最佳实践

在UI交互测试中，合理的等待策略、超时设置和网络拦截配置是确保测试稳定性的关键。NocoBase 的 Playwright 配置通过 `expect` 配置项设置了10秒的期望超时时间，这为元素查找和状态验证提供了足够的时间。

配置中启用了跟踪功能（`trace: 'on-first-retry'`），这在测试失败时能够提供详细的执行记录，帮助开发者快速定位问题。同时，通过 `process.env.CI` 环境变量的判断，实现了CI环境和本地环境的不同配置策略，如CI环境中禁用 `test.only`、增加重试次数等。

```mermaid
flowchart TD
Start([UI测试开始]) --> WaitForElement["等待元素出现"]
WaitForElement --> ElementFound{"元素找到?"}
ElementFound --> |是| Interact["与元素交互"]
ElementFound --> |否| Retry["重试或失败"]
Interact --> WaitForResponse["等待网络响应"]
WaitForResponse --> ResponseReceived{"响应收到?"}
ResponseReceived --> |是| Verify["验证结果"]
ResponseReceived --> |否| Timeout["超时处理"]
Verify --> Assertion["断言验证"]
Assertion --> Pass["测试通过"]
Assertion --> Fail["测试失败"]
Fail --> Trace["生成跟踪报告"]
Trace --> RetryOrFail["重试或标记失败"]
style Start fill:#4CAF50,stroke:#388E3C
style Pass fill:#4CAF50,stroke:#388E3C
style Fail fill:#F44336,stroke:#D32F2F
style Trace fill:#FF9800,stroke:#F57C00
```

**图源**  
- [packages/core/test/src/e2e/defineConfig.ts](file://packages/core/test/src/e2e/defineConfig.ts#L14-L18)
- [packages/core/test/src/e2e/defineConfig.ts#L53](file://packages/core/test/src/e2e/defineConfig.ts#L53)

**本节来源**  
- [packages/core/test/src/e2e/defineConfig.ts](file://packages/core/test/src/e2e/defineConfig.ts#L14-L18)
- [packages/core/test/src/e2e/defineConfig.ts#L53](file://packages/core/test/src/e2e/defineConfig.ts#L53)

## 视觉回归与性能测试集成

虽然当前配置未直接包含视觉回归测试和性能测试的集成，但通过 Playwright 的扩展能力，可以轻松实现这些功能。例如，可以通过自定义测试扩展来集成视觉回归测试库，或通过性能API来收集和分析页面性能指标。

Playwright 的 `request` 模块可用于模拟API调用，这对于性能测试中的负载测试和压力测试非常有用。同时，通过 `page.evaluate` 方法，可以直接在浏览器上下文中执行JavaScript代码，获取详细的性能数据。

```mermaid
graph TB
subgraph "视觉回归测试"
A[截图基准] --> B[当前截图]
B --> C[图像比较]
C --> D[差异分析]
D --> E[结果报告]
end
subgraph "性能测试"
F[页面加载] --> G[性能指标收集]
G --> H[资源加载时间]
G --> I[首屏时间]
G --> J[交互时间]
H --> K[性能分析]
I --> K
J --> K
K --> L[性能报告]
end
M[Playwright测试] --> A
M --> F
E --> N[测试结果]
L --> N
```

**图源**  
- [packages/core/test/src/e2e/e2eUtils.ts](file://packages/core/test/src/e2e/e2eUtils.ts#L11-L14)
- [packages/core/test/src/e2e/e2eUtils.ts#L502-L508](file://packages/core/test/src/e2e/e2eUtils.ts#L502-L508)

**本节来源**  
- [packages/core/test/src/e2e/e2eUtils.ts](file://packages/core/test/src/e2e/e2eUtils.ts#L11-L14)
- [packages/core/test/src/e2e/e2eUtils.ts#L502-L508)

## 环境变量与外部配置

Playwright 配置与环境变量紧密结合，通过 `.env.e2e.example` 文件定义了测试所需的各项环境变量。这些变量包括应用端口、数据库配置、认证文件路径等，使得测试配置能够适应不同的运行环境。

`APP_BASE_URL` 环境变量用于设置测试的基础URL，`PLAYWRIGHT_AUTH_FILE` 用于指定认证状态的存储文件。这些环境变量的使用，使得测试配置更加灵活，能够在不同环境中无缝切换。

```mermaid
erDiagram
ENVIRONMENT_VARIABLES {
string APP_PORT "应用端口"
string APP_BASE_URL "应用基础URL"
string DB_DIALECT "数据库类型"
string DB_DATABASE "数据库名称"
string DB_USER "数据库用户"
string DB_PASSWORD "数据库密码"
string PLAYWRIGHT_AUTH_FILE "认证文件路径"
string E2E_JOB_ID "E2E作业ID"
}
TEST_CONFIGURATION {
string testDir "测试目录"
string testMatch "测试匹配模式"
string outputDir "输出目录"
string reporter "报告生成器"
}
ENVIRONMENT_VARIABLES ||--o{ TEST_CONFIGURATION : "影响"
```

**图源**  
- [.env.e2e.example](file://.env.e2e.example#L13-L42)
- [packages/core/test/src/e2e/defineConfig.ts#L51](file://packages/core/test/src/e2e/defineConfig.ts#L51)

**本节来源**  
- [.env.e2e.example](file://.env.e2e.example#L13-L42)
- [packages/core/test/src/e2e/defineConfig.ts#L51](file://packages/core/test/src/e2e/defineConfig.ts#L51)