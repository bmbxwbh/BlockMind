using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class MainWindowViewModel : ObservableObject
{
    [ObservableProperty]
    private object? _currentPage;

    [ObservableProperty]
    private NavItem? _selectedNavItem;

    public ObservableCollection<NavItem> NavItems { get; } = new()
    {
        new("layout-dashboard", "仪表盘", "dashboard"),
        new("map", "地图", "map"),
        new("message-square", "AI 对话", "chat"),
        new("brain", "记忆系统", "memory"),
        new("wrench", "技能管理", "skills"),
        new("shopping-bag", "技能市场", "marketplace"),
        new("bot", "模型配置", "model"),
        new("shield", "安全设置", "safety"),
        new("refresh-cw", "任务队列", "tasks"),
        new("file-text", "日志中心", "logs"),
        new("settings", "设置", "settings"),
    };

    public MainWindowViewModel()
    {
        SelectedNavItem = NavItems[0];
        CurrentPage = new DashboardViewModel();
    }

    partial void OnSelectedNavItemChanged(NavItem? value)
    {
        if (value?.Page == null) return;
        CurrentPage = value.Page switch
        {
            "dashboard" => new DashboardViewModel(),
            "map" => new MapViewModel(),
            "chat" => new ChatViewModel(),
            "memory" => new MemoryViewModel(),
            "skills" => new SkillsViewModel(),
            "marketplace" => new MarketplaceViewModel(),
            "model" => new ModelConfigViewModel(),
            "safety" => new SafetyViewModel(),
            "tasks" => new TasksViewModel(),
            "logs" => new LogsViewModel(),
            "settings" => new SettingsViewModel(),
            _ => new DashboardViewModel(),
        };
    }
}

public record NavItem(string Icon, string Label, string Page);
