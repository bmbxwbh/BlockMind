using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text.Json;

namespace BlockMind.Desktop.Services;

public static class Lang
{
    private static Dictionary<string, string> _strings = new();
    private static string _currentLang = "zh";

    public static string Current => _currentLang;

    public static void Load(string lang)
    {
        _currentLang = lang;
        _strings = lang switch
        {
            "en" => _en,
            _ => _zh,
        };
    }

    public static void Toggle()
    {
        Load(_currentLang == "zh" ? "en" : "zh");
    }

    public static string T(string key)
    {
        return _strings.TryGetValue(key, out var val) ? val : key;
    }

    private static readonly Dictionary<string, string> _zh = new()
    {
        ["Dashboard"] = "仪表盘",
        ["Map"] = "地图",
        ["AI Chat"] = "AI 对话",
        ["Memory"] = "记忆系统",
        ["Skills"] = "技能管理",
        ["Marketplace"] = "技能市场",
        ["Model Config"] = "模型配置",
        ["Safety"] = "安全设置",
        ["Tasks"] = "任务队列",
        ["Logs"] = "日志中心",
        ["Settings"] = "设置",
        ["Health"] = "生命值",
        ["Hunger"] = "饥饿值",
        ["Position"] = "位置",
        ["Dimension"] = "维度",
        ["Server Control"] = "服务控制",
        ["Start BlockMind"] = "启动 BlockMind",
        ["Stop BlockMind"] = "停止 BlockMind",
        ["Connect Mod"] = "连接 Mod",
        ["Quick Actions"] = "快捷操作",
        ["Home"] = "回家",
        ["Mine"] = "挖矿",
        ["Chop"] = "砍树",
        ["Eat"] = "吃东西",
        ["Patrol"] = "巡逻",
        ["Stop"] = "停止",
        ["Recent Events"] = "最近事件",
        ["Type a message..."] = "输入消息...",
        ["Send"] = "发送",
        ["Load"] = "加载",
        ["Save"] = "保存",
        ["Backup"] = "备份",
        ["Cleanup"] = "清理",
        ["Refresh"] = "刷新",
        ["Search"] = "搜索",
        ["Install"] = "安装",
        ["Run"] = "执行",
        ["Delete"] = "删除",
        ["Test Connection"] = "测试连接",
        ["Connected"] = "已连接",
        ["Failed"] = "连接失败",
        ["Running"] = "运行中",
        ["Not connected"] = "未连接",
        ["Minecraft"] = "Minecraft",
        ["Mode"] = "模式",
        ["Version"] = "版本",
        ["Max RAM"] = "最大内存",
        ["Enabled"] = "启用",
        ["Port"] = "端口",
        ["Reset"] = "重置",
        ["Save Config"] = "保存配置",
        ["Main Agent (Chat)"] = "主 Agent（聊天）",
        ["Operation Agent (Execute)"] = "操作 Agent（执行）",
        ["Format"] = "格式",
        ["URL"] = "地址",
        ["API Key"] = "密钥",
        ["Model"] = "模型",
        ["Temperature"] = "温度",
        ["Zones"] = "区域",
        ["Paths"] = "路径",
        ["Strategies"] = "策略",
        ["Players"] = "玩家",
        ["Pending"] = "待执行",
        ["Running Tasks"] = "运行中",
        ["Completed"] = "已完成",
        ["Audit Log"] = "审计日志",
        ["Load Audit Log"] = "加载审计日志",
        ["Dynmap"] = "Dynmap 地图",
        ["Dynmap Map View"] = "Dynmap 地图视图",
        ["Install Dynmap plugin to enable map view"] = "安装 Dynmap 插件后启用地图视图",
        ["Check Dynmap"] = "检查 Dynmap",
        ["Search skills..."] = "搜索技能...",
        ["Language"] = "语言",
        ["Theme"] = "主题",
        ["About"] = "关于",
        ["Version"] = "版本",
        ["License"] = "许可证",
        ["Non-Commercial Use Only"] = "仅限非商业用途",
        ["Dashboard"] = "仪表盘",
        ["BlockMind Desktop"] = "BlockMind 桌面版",
    };

    private static readonly Dictionary<string, string> _en = new()
    {
        ["仪表盘"] = "Dashboard",
        ["地图"] = "Map",
        ["AI 对话"] = "AI Chat",
        ["记忆系统"] = "Memory",
        ["技能管理"] = "Skills",
        ["技能市场"] = "Marketplace",
        ["模型配置"] = "Model Config",
        ["安全设置"] = "Safety",
        ["任务队列"] = "Tasks",
        ["日志中心"] = "Logs",
        ["设置"] = "Settings",
    };
}
