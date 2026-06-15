# BlockMind Desktop — 完整设计文档

> 版本：1.0 · 日期：2026-06-15

---

## 1. 技术栈

| 层 | 技术 | 版本 | 说明 |
|---|------|------|------|
| UI 框架 | Avalonia UI | 11.x | 原生跨平台 XAML 渲染 |
| 运行时 | .NET | 8.0 LTS | C# 后端 + 构建工具 |
| 语言 | C# | 12 | 主语言 |
| UI 标记 | AXAML | — | Avalonia XAML，声明式 UI |
| AI 推理 | Python 3.10+ | 子进程 | 复用现有 AI 引擎 |
| 设计风格 | Linear 风格 | — | 深色极简 |
| 图标 | Lucide | SVG | 与 WebUI 一致 |
| 打包 | Avalonia Native | — | Windows .exe / macOS .app / Linux AppImage |

### NuGet 依赖

```
Avalonia                11.x        UI 框架
Avalonia.Desktop        11.x        桌面平台支持
Avalonia.Themes.Fluent  11.x        Fluent 主题基础
CommunityToolkit.Mvvm   8.x         MVVM 工具包
Microsoft.Extensions.Hosting  8.x   依赖注入 + 生命周期
System.Text.Json        8.x         JSON 序列化
```

---

## 2. 项目结构

```
desktop/
├── BlockMind.Desktop.sln
│
├── src/
│   ├── BlockMind.Desktop/              # 主应用项目
│   │   ├── BlockMind.Desktop.csproj
│   │   ├── Program.cs                  # 入口点
│   │   ├── App.axaml                   # Avalonia 应用定义
│   │   ├── App.axaml.cs
│   │   │
│   │   ├── Models/                     # 数据模型
│   │   │   ├── AppConfig.cs            # 应用配置
│   │   │   ├── AiConfig.cs             # AI 模型配置
│   │   │   ├── ModConfig.cs            # Mod 连接配置
│   │   │   ├── PlayerStatus.cs         # 玩家状态
│   │   │   ├── InventoryItem.cs        # 背包物品
│   │   │   ├── EntityInfo.cs           # 实体信息
│   │   │   ├── MemoryData.cs           # 记忆数据
│   │   │   ├── SkillInfo.cs            # 技能信息
│   │   │   ├── ChatMessage.cs          # 聊天消息
│   │   │   ├── LogEntry.cs             # 日志条目
│   │   │   └── TaskInfo.cs             # 任务信息
│   │   │
│   │   ├── Services/                   # 业务服务
│   │   │   ├── IModService.cs          # Mod 通信接口
│   │   │   ├── ModHttpService.cs       # Mod HTTP 客户端
│   │   │   ├── IAiService.cs           # AI 推理接口
│   │   │   ├── AiHttpService.cs        # AI HTTP 客户端 (OpenAI/Anthropic)
│   │   │   ├── IMemoryService.cs       # 记忆系统接口
│   │   │   ├── MemoryJsonService.cs    # 记忆 JSON 读写
│   │   │   ├── ISkillService.cs        # 技能管理接口
│   │   │   ├── SkillYamlService.cs     # 技能 YAML 解析
│   │   │   ├── IConfigService.cs       # 配置管理接口
│   │   │   ├── ConfigYamlService.cs    # 配置 YAML 读写
│   │   │   ├── PythonBridge.cs         # Python 子进程管理
│   │   │   ├── TrayService.cs          # 系统托盘
│   │   │   ├── NotificationService.cs  # 系统通知
│   │   │   └── UpdateService.cs        # 自动更新检查
│   │   │
│   │   ├── ViewModels/                 # MVVM 视图模型
│   │   │   ├── MainWindowViewModel.cs  # 主窗口
│   │   │   ├── DashboardViewModel.cs   # 仪表盘
│   │   │   ├── MapViewModel.cs         # 地图
│   │   │   ├── ChatViewModel.cs        # AI 对话
│   │   │   ├── MemoryViewModel.cs      # 记忆系统
│   │   │   ├── SkillsViewModel.cs      # 技能管理
│   │   │   ├── MarketplaceViewModel.cs # 技能市场
│   │   │   ├── ModelConfigViewModel.cs # 模型配置
│   │   │   ├── SafetyViewModel.cs      # 安全设置
│   │   │   ├── TasksViewModel.cs       # 任务队列
│   │   │   ├── LogsViewModel.cs        # 日志中心
│   │   │   └── SettingsViewModel.cs    # 设置
│   │   │
│   │   ├── Views/                      # XAML 页面
│   │   │   ├── MainWindow.axaml        # 主窗口壳
│   │   │   ├── MainWindow.axaml.cs
│   │   │   ├── Controls/               # 自定义控件
│   │   │   │   ├── StatusCard.axaml    # 状态卡片
│   │   │   │   ├── NavSidebar.axaml    # 侧栏导航
│   │   │   │   ├── ChatBubble.axaml    # 聊天气泡
│   │   │   │   ├── SkillRow.axaml      # 技能行
│   │   │   │   ├── LogLine.axaml       # 日志行
│   │   │   │   └── StatRing.axaml      # 环形统计图
│   │   │   ├── Pages/                  # 页面视图
│   │   │   │   ├── DashboardPage.axaml
│   │   │   │   ├── MapPage.axaml
│   │   │   │   ├── ChatPage.axaml
│   │   │   │   ├── MemoryPage.axaml
│   │   │   │   ├── SkillsPage.axaml
│   │   │   │   ├── MarketplacePage.axaml
│   │   │   │   ├── ModelConfigPage.axaml
│   │   │   │   ├── SafetyPage.axaml
│   │   │   │   ├── TasksPage.axaml
│   │   │   │   ├── LogsPage.axaml
│   │   │   │   └── SettingsPage.axaml
│   │   │   └── Dialogs/               # 对话框
│   │   │       ├── ConfirmDialog.axaml
│   │   │       ├── SkillEditDialog.axaml
│   │   │       └── FirstRunWizard.axaml
│   │   │
│   │   ├── Themes/                     # 主题资源
│   │   │   ├── LinearDark.axaml        # Linear 暗色主题
│   │   │   ├── Colors.axaml            # 颜色定义
│   │   │   ├── Typography.axaml        # 字体定义
│   │   │   └── Controls.axaml          # 控件样式覆写
│   │   │
│   │   ├── Converters/                 # XAML 值转换器
│   │   │   ├── BoolToColorConverter.cs
│   │   │   ├── HealthToColorConverter.cs
│   │   │   └── TimeAgoConverter.cs
│   │   │
│   │   └── Assets/                     # 静态资源
│   │       ├── icon.ico                # Windows 图标
│   │       ├── icon.icns               # macOS 图标
│   │       ├── icon.png                # Linux 图标
│   │       └── lucide/                 # Lucide SVG 图标
│   │
│   └── BlockMind.Core/                 # 核心库 (可复用)
│       ├── BlockMind.Core.csproj
│       ├── Api/
│       │   ├── ModApiClient.cs         # Mod REST 客户端
│       │   ├── AiApiClient.cs          # AI API 客户端
│       │   └── DynmapApiClient.cs      # Dynmap 客户端
│       ├── Memory/
│       │   ├── MemoryStore.cs          # 记忆存储
│       │   ├── ZoneMemory.cs           # 空间记忆
│       │   ├── PathMemory.cs           # 路径记忆
│       │   └── StrategyMemory.cs       # 策略记忆
│       ├── Skills/
│       │   ├── SkillParser.cs          # YAML 解析
│       │   ├── SkillValidator.cs       # 校验
│       │   └── SkillMatcher.cs         # 匹配
│       └── Config/
│           ├── ConfigLoader.cs         # YAML 配置加载
│           └── ConfigModels.cs         # 配置数据模型
```

---

## 3. 设计系统 (Linear 风格)

### 3.1 色板

```xml
<!-- Themes/Colors.axaml -->
<SolidColorBrush x:Key="BgBase"      Color="#0A0A0A"/>   <!-- 最深背景 -->
<SolidColorBrush x:Key="BgSurface"   Color="#111111"/>   <!-- 卡片/面板 -->
<SolidColorBrush x:Key="BgHover"     Color="#1A1A1A"/>   <!-- 悬停 -->
<SolidColorBrush x:Key="BgActive"    Color="#222222"/>   <!-- 按下 -->
<SolidColorBrush x:Key="Border"      Color="#1F1F1F"/>   <!-- 边框 -->
<SolidColorBrush x:Key="BorderLight" Color="#2A2A2A"/>   <!-- 浅边框 -->

<SolidColorBrush x:Key="TextPrimary"   Color="#EDEDED"/> <!-- 主文字 -->
<SolidColorBrush x:Key="TextSecondary" Color="#888888"/> <!-- 次要文字 -->
<SolidColorBrush x:Key="TextTertiary"  Color="#555555"/> <!-- 更淡文字 -->

<SolidColorBrush x:Key="Accent"        Color="#7C5CFC"/> <!-- 强调色 (紫) -->
<SolidColorBrush x:Key="AccentHover"   Color="#9B7FFF"/> <!-- 强调悬停 -->
<SolidColorBrush x:Key="Success"       Color="#00D68F"/> <!-- 成功 (绿) -->
<SolidColorBrush x:Key="Warning"       Color="#FFAA00"/> <!-- 警告 (橙) -->
<SolidColorBrush x:Key="Error"         Color="#FF3B3B"/> <!-- 错误 (红) -->
<SolidColorBrush x:Key="Info"          Color="#3B82F6"/> <!-- 信息 (蓝) -->

<SolidColorBrush x:Key="HealthFull"    Color="#00D68F"/> <!-- 满血 -->
<SolidColorBrush x:Key="HealthMid"     Color="#FFAA00"/> <!-- 半血 -->
<SolidColorBrush x:Key="HealthLow"     Color="#FF3B3B"/> <!-- 低血 -->
```

### 3.2 字体

```xml
<!-- Themes/Typography.axaml -->
<FontFamily x:Key="FontPrimary">Inter, -apple-system, BlinkMacSystemFont, sans-serif</FontFamily>
<FontFamily x:Key="FontMono">JetBrains Mono, Cascadia Code, monospace</FontFamily>

<!-- 字号 -->
<x:Double x:Key="TextXs">11</x:Double>    <!-- 极小 -->
<x:Double x:Key="TextSm">12</x:Double>    <!-- 小 -->
<x:Double x:Key="TextMd">13</x:Double>    <!-- 正文 -->
<x:Double x:Key="TextLg">15</x:Double>    <!-- 标题 -->
<x:Double x:Key="TextXl">18</x:Double>    <!-- 大标题 -->
<x:Double x:Key="Text2xl">24</x:Double>   <!-- 页面标题 -->
```

### 3.3 间距

```xml
<x:Double x:Key="SpaceXs">4</x:Double>
<x:Double x:Key="SpaceSm">8</x:Double>
<x:Double x:Key="SpaceMd">12</x:Double>
<x:Double x:Key="SpaceLg">16</x:Double>
<x:Double x:Key="SpaceXl">24</x:Double>
<x:Double x:Key="Space2xl">32</x:Double>
```

### 3.4 圆角

```xml
<CornerRadius x:Key="RadiusSm">4</CornerRadius>
<CornerRadius x:Key="RadiusMd">6</CornerRadius>
<CornerRadius x:Key="RadiusLg">8</CornerRadius>
<CornerRadius x:Key="RadiusFull">999</CornerRadius>
```

### 3.5 阴影

无阴影。Linear 风格不使用阴影，用边框和背景色区分层级。

---

## 4. 主窗口布局

```xml
<!-- MainWindow.axaml -->
<Window>
  <Grid ColumnDefinitions="240, *">
    <!-- 左侧导航栏 (240px) -->
    <Grid Grid.Column="0" Background="{DynamicResource BgSurface}">
      <!-- Logo + 版本 -->
      <!-- 导航项列表 -->
      <!-- 底部: 状态指示 + 设置入口 -->
    </Grid>

    <!-- 右侧内容区 -->
    <Grid Grid.Column="1">
      <!-- 页面内容 (ContentControl 绑定 ViewModel) -->
      <ContentControl Content="{Binding CurrentPage}"/>
    </Grid>
  </Grid>
</Window>
```

### 侧栏导航项

```xml
<StackPanel>
  <NavItem Icon="layout-dashboard"  Label="仪表盘"   Page="Dashboard"/>
  <NavItem Icon="map"               Label="地图"      Page="Map"/>
  <NavItem Icon="message-square"    Label="AI 对话"   Page="Chat"/>
  <NavItem Icon="brain"             Label="记忆系统"   Page="Memory"/>
  <NavItem Icon="wrench"            Label="技能管理"   Page="Skills"/>
  <NavItem Icon="shopping-bag"      Label="技能市场"   Page="Marketplace"/>
  <Separator/>
  <NavItem Icon="bot"               Label="模型配置"   Page="ModelConfig"/>
  <NavItem Icon="shield"            Label="安全设置"   Page="Safety"/>
  <NavItem Icon="refresh-cw"        Label="任务队列"   Page="Tasks"/>
  <NavItem Icon="file-text"         Label="日志中心"   Page="Logs"/>
  <NavItem Icon="settings"          Label="设置"       Page="Settings"/>
</StackPanel>
```

---

## 5. 页面详细设计

### 5.1 仪表盘 (DashboardPage)

```
┌────────────────────────────────────────────────────────┐
│  仪表盘                                                  │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 生命值    │ │ 饥饿值    │ │ 位置      │ │ 维度      │  │
│  │ 20/20    │ │ 18/20    │ │ 64,-120  │ │ 主世界    │  │
│  │ ████████ │ │ ███████░ │ │          │ │          │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────┐     │
│  │ 服务控制                                        │     │
│  │  [▶ 启动 MC 服务端]  [▶ 启动 BlockMind]        │     │
│  │  状态: ● 运行中  |  MC: 1.20.4  |  Bot: Steve  │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  ┌───────────────────────────────────────────────┐     │
│  │ 快捷操作                                        │     │
│  │  [回家] [挖矿] [砍树] [吃东西] [巡逻] [停止]   │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  ┌───────────────────────────────────────────────┐     │
│  │ 最近事件                                        │     │
│  │  14:32  挖掘了 16 个铁矿石                       │     │
│  │  14:28  回到了基地                               │     │
│  │  14:15  开始巡逻                                 │     │
│  └───────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────┘
```

**ViewModel 绑定：**
- `PlayerStatus` — 生命/饥饿/位置/维度（每 2 秒轮询 Mod API）
- `ServerStatus` — MC 服务端 + BlockMind 运行状态
- `RecentEvents` — EventBus 事件流（最近 20 条）
- `QuickCommands` — 预设命令列表

### 5.2 AI 对话 (ChatPage)

```
┌────────────────────────────────────────────────────────┐
│  AI 对话                                                │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  🤖 你好！我是 BlockMind，有什么可以帮你的？      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  👤 帮我去挖点钻石                               │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  🤖 好的，我去挖钻石！                           │   │
│  │  ┌─────────────────────────────────────────┐    │   │
│  │  │ 任务执行中...                              │    │   │
│  │  │ 策略: 缓存技能 [挖钻石]                   │    │   │
│  │  │ 状态: 前往钻石层                          │    │   │
│  │  └─────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────┐ ┌────┐      │
│  │ 输入消息...                           │ │发送│      │
│  └──────────────────────────────────────┘ └────┘      │
└────────────────────────────────────────────────────────┘
```

**交互流程：**
1. 用户输入 → 调用 Python 后端 `/api/command/panel`
2. Python 返回 AI 回复 + 任务状态
3. 如果有任务 → 显示执行状态卡片
4. 任务完成 → 更新卡片显示结果

### 5.3 记忆系统 (MemoryPage)

```
┌────────────────────────────────────────────────────────┐
│  记忆系统                                    [备份] [清理] │
├────────────────────────────────────────────────────────┤
│  [区域] [路径] [策略] [玩家]  ← Tab 切换                │
│                                                         │
│  ── 区域 Tab ──                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 名称        类型    坐标          半径            │   │
│  │ 基地        BASE    (50,64,-100)  30              │   │
│  │ 主城        BUILD   (100,64,200)  20              │   │
│  │ 岩浆湖      DANGER  (80,12,-50)   10              │   │
│  │ 钻石矿      RESOURCE(45,-59,78)   5               │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ── 路径 Tab ──                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 起点 → 终点         成功率   次数   最后使用      │   │
│  │ 基地 → 钻石矿       95%     20     2分钟前       │   │
│  │ 基地 → 矿洞入口     88%     15     1小时前       │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

### 5.4 技能管理 (SkillsPage)

```
┌────────────────────────────────────────────────────────┐
│  技能管理                              [+ 新建] [导入]   │
├────────────────────────────────────────────────────────┤
│  🔍 搜索技能...                            [全部▼]      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 名称        等级  成功率  执行次数  操作           │   │
│  │ 挖钻石      L2    95%    20       [▶] [编辑] [删除]│   │
│  │ 自动种田    L2    88%    8        [▶] [编辑] [删除]│   │
│  │ 回家        L1    100%   56       [▶] [编辑] [删除]│   │
│  │ 击杀末影龙  L4    72%    3        [▶] [编辑] [删除]│   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ YAML 编辑器                                      │   │
│  │ skill_id: mine_diamonds                          │   │
│  │ name: "挖钻石"                                    │   │
│  │ tags: ["挖矿", "钻石"]                            │   │
│  │ ...                                              │   │
│  │                                      [保存] [校验] │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

### 5.5 模型配置 (ModelConfigPage)

```
┌────────────────────────────────────────────────────────┐
│  模型配置                                                │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ── 主 Agent（聊天 + 识别）──                            │
│  格式:  (●) OpenAI 兼容  (○) Anthropic                   │
│  URL:   [https://api.openai.com/v1              ]       │
│  Key:   [sk-••••••••••••••••••••••              ]       │
│  模型:  [gpt-4o                                 ]       │
│  温度:  [0.7 ────────●─────]                             │
│  [测试连接]  状态: ● 已连接                               │
│                                                         │
│  ── 操作 Agent（执行）──                                 │
│  格式:  (●) OpenAI 兼容  (○) Anthropic                   │
│  URL:   [https://api.openai.com/v1              ]       │
│  Key:   [sk-••••••••••••••••••••••              ]       │
│  模型:  [gpt-4o                                 ]       │
│  温度:  [0.3 ────●─────────]                             │
│  [测试连接]  状态: ● 已连接                               │
│                                                         │
│                                        [保存配置]        │
└────────────────────────────────────────────────────────┘
```

### 5.6 设置 (SettingsPage)

```
┌────────────────────────────────────────────────────────┐
│  设置                                                    │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ── Minecraft ──                                        │
│  模式:  (●) 服务端  (○) 客户端                           │
│  版本:  [1.20.4 ▼]                                      │
│  Java:  [/usr/bin/java ▼]                               │
│  内存:  [2G ▼]                                          │
│                                                         │
│  ── Dynmap 地图 ──                                      │
│  启用:  [✓]                                             │
│  端口:  [8163]                                          │
│  状态:  ● 已连接                                         │
│                                                         │
│  ── 外观 ──                                             │
│  主题:  暗色 (Linear)                                    │
│  语言:  [中文 ▼]                                         │
│                                                         │
│  ── 关于 ──                                             │
│  版本:  3.4.0                                           │
│  [检查更新] [查看日志] [导出配置] [恢复默认]              │
└────────────────────────────────────────────────────────┘
```

---

## 6. 核心服务设计

### 6.1 ModHttpService

```csharp
public class ModHttpService : IModService
{
    private readonly HttpClient _http;
    private readonly string _baseUrl; // http://localhost:25580

    // 状态查询
    Task<PlayerStatus> GetStatusAsync();
    Task<InventoryData> GetInventoryAsync();
    Task<EntityList> GetEntitiesAsync(int radius);
    Task<BlockList> GetBlocksAsync(int radius, string type);

    // 动作执行
    Task<ActionResult> MoveAsync(double x, double y, double z, bool sprint);
    Task<ActionResult> DigAsync(int x, int y, int z);
    Task<ActionResult> PlaceAsync(string item, int x, int y, int z);
    Task<ActionResult> AttackAsync(int entityId);
    Task<ActionResult> EatAsync(string item);
    Task<ActionResult> ChatAsync(string message);

    // Bot 管理
    Task<BotResult> SpawnBotAsync(string name);
    Task<BotResult> DespawnBotAsync();

    // 导航
    Task<NavResult> NavigateAsync(int x, int y, int z);
    Task<NavResult> StopNavigationAsync();

    // 连接管理
    Task<bool> ConnectAsync();
    Task<VersionInfo> GetVersionAsync();
}
```

### 6.2 AiHttpService

```csharp
public class AiHttpService : IAiService
{
    private readonly HttpClient _http;

    // 根据用户选择的格式构造请求
    Task<ChatResult> ChatAsync(List<ChatMessage> messages, AiConfig config);

    // 测试连接
    Task<bool> TestConnectionAsync(AiConfig config);
}

public class AiConfig
{
    public AiFormat Format { get; set; }  // OpenAI | Anthropic
    public string BaseUrl { get; set; }
    public string ApiKey { get; set; }
    public string Model { get; set; }
    public float Temperature { get; set; }
    public int MaxTokens { get; set; }
}

public enum AiFormat { OpenAI, Anthropic }
```

### 6.3 PythonBridge

```csharp
public class PythonBridge : IDisposable
{
    private Process _pythonProcess;

    // 启动 Python 后端子进程
    Task StartAsync(string pythonPath, string workingDir, int port);

    // 停止
    Task StopAsync();

    // 健康检查
    Task<bool> IsHealthyAsync();

    // 自动重启
    Task RestartAsync();
}
```

### 6.4 MemoryJsonService

```csharp
public class MemoryJsonService : IMemoryService
{
    private readonly string _dataDir; // data/memory/

    // 读取
    Task<MemoryData> LoadAsync();

    // 区域
    Task<List<ZoneInfo>> GetZonesAsync();
    Task AddZoneAsync(ZoneInfo zone);
    Task RemoveZoneAsync(string name);

    // 路径
    Task<List<PathInfo>> GetPathsAsync();
    Task CachePathAsync(PathInfo path);

    // 策略
    Task<List<StrategyInfo>> GetStrategiesAsync();
    Task<StrategyInfo> GetBestStrategyAsync(string taskType);

    // 备份/恢复
    Task<string> BackupAsync();
    Task RestoreAsync(string backupPath);
    Task<int> CleanupAsync();
}
```

---

## 7. 数据流

### 7.1 启动流程

```
用户双击 BlockMind.exe
  → Program.cs → App.axaml → MainWindow
  → 检查 config.yaml 是否存在
    → 不存在: 显示首次配置向导 (FirstRunWizard)
    → 存在: 加载配置
  → 启动 PythonBridge (Python 子进程)
  → 连接 Mod (ModHttpService.ConnectAsync)
  → 显示仪表盘
  → 开始轮询状态 (每 2 秒)
```

### 7.2 AI 对话流程

```
用户输入 "帮我挖钻石"
  → ChatViewModel.SendMessage()
  → AiHttpService.ChatAsync(messages, config)
    → 构造请求 (OpenAI/Anthropic 格式)
    → POST /v1/chat/completions 或 /v1/messages
    → 解析响应
  → 检查 [TASK:xxx] 标签
    → 有任务: 显示执行状态卡片
    → 调用 Python 后端执行
  → 更新对话列表
```

### 7.3 状态轮询流程

```
MainWindowViewModel 启动定时器 (2秒)
  → ModHttpService.GetStatusAsync()
  → 更新 PlayerStatus (生命/饥饿/位置/维度)
  → 更新 ServerStatus (MC 运行状态)
  → 更新 InventoryData (背包)
  → 触发 UI 刷新 (MVVM 绑定自动更新)
```

---

## 8. 打包方案

### Windows (.exe)

```bash
dotnet publish -c Release -r win-x64 --self-contained
# 输出: desktop/src/BlockMind.Desktop/bin/Release/net8.0/win-x64/publish/
```

### macOS (.app)

```bash
dotnet publish -c Release -r osx-arm64 --self-contained  # Apple Silicon
dotnet publish -c Release -r osx-x64 --selfcontained     # Intel
```

### Linux (AppImage)

```bash
dotnet publish -c Release -r linux-x64 --self-contained
# 使用 dotnet-bundle 或 AppImage 打包
```

### 内嵌 Python

打包时将 Python 运行时 + 依赖一起打包：
```
publish/
├── BlockMind.exe
├── python/               # 嵌入式 Python
│   ├── python.exe
│   ├── Lib/site-packages/
│   └── ...
├── src/                  # Python AI 代码
├── skills/               # Skill 文件
├── config.yaml           # 用户配置
└── data/                 # 运行时数据
```

---

## 9. 首次运行向导

```
┌─────────────────────────────────────────────────┐
│  欢迎使用 BlockMind                              │
│                                                  │
│  ┌─ 步骤 1/4: 选择语言 ─────────────────────┐   │
│  │  (●) 中文  (○) English                    │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌─ 步骤 2/4: AI 模型配置 ──────────────────┐   │
│  │  格式: (●) OpenAI  (○) Anthropic          │   │
│  │  URL:  [________________]                  │   │
│  │  Key:  [________________]                  │   │
│  │  模型: [________________]                  │   │
│  │  [测试连接]                                │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌─ 步骤 3/4: Minecraft 模式 ───────────────┐   │
│  │  (●) 服务端 — 自动下载 MC 服务端          │   │
│  │  (○) 客户端 — 我已安装 Minecraft          │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌─ 步骤 4/4: 完成 ────────────────────────┐   │
│  │  配置已保存，点击开始使用！               │   │
│  │  [开始使用]                               │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## 10. 系统托盘

```
右键菜单:
├── 显示主窗口
├── ─────────────
├── ● BlockMind 运行中
├── ● MC 服务端 运行中
├── ─────────────
├── 启动 BlockMind
├── 停止 BlockMind
├── 启动 MC 服务端
├── 停止 MC 服务端
├── ─────────────
├── 打开 WebUI (http://localhost:19951)
├── ─────────────
└── 退出
```

通知：
- 任务完成 → 系统通知
- 连接断开 → 系统通知
- 错误发生 → 系统通知

---

## 11. 依赖关系图

```
Program.cs
  └── App.axaml
        └── MainWindow
              ├── NavSidebar (导航)
              ├── DashboardPage → DashboardViewModel → IModService + IAiService
              ├── MapPage → MapViewModel → DynmapApiClient
              ├── ChatPage → ChatViewModel → IAiService + PythonBridge
              ├── MemoryPage → MemoryViewModel → IMemoryService
              ├── SkillsPage → SkillsViewModel → ISkillService
              ├── MarketplacePage → MarketplaceViewModel → ISkillService
              ├── ModelConfigPage → ModelConfigViewModel → IAiService
              ├── SafetyPage → SafetyViewModel → IModService
              ├── TasksPage → TasksViewModel → PythonBridge
              ├── LogsPage → LogsViewModel → (日志订阅)
              └── SettingsPage → SettingsViewModel → IConfigService
```
