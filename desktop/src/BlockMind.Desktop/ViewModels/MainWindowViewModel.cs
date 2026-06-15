using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using BlockMind.Desktop.Services;
using System.Text.Json;

namespace BlockMind.Desktop.ViewModels;

public partial class MainWindowViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private object? _currentPage;
    [ObservableProperty] private NavItem? _selectedNavItem;
    [ObservableProperty] private bool _modConnected;
    [ObservableProperty] private bool _pythonRunning;
    [ObservableProperty] private string _statusText = "未连接";

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

    public MainWindowViewModel(AppService service)
    {
        _service = service;
        _service.StatusChanged += OnServiceStatusChanged;
        SelectedNavItem = NavItems[0];
        CurrentPage = new DashboardViewModel(service);
    }

    [RelayCommand]
    private async Task ToggleBlockMindAsync()
    {
        if (_pythonRunning)
            await _service.StopPythonAsync();
        else
            await _service.StartPythonAsync();
    }

    [RelayCommand]
    private async Task ConnectModAsync()
    {
        ModConnected = await _service.ConnectToModAsync();
        StatusText = ModConnected ? "已连接" : "未连接";
    }

    private void OnServiceStatusChanged()
    {
        ModConnected = _service.ModConnected;
        PythonRunning = _service.PythonRunning;
        StatusText = ModConnected ? (PythonRunning ? "运行中" : "Mod已连接") : "未连接";
    }

    partial void OnSelectedNavItemChanged(NavItem? value)
    {
        if (value?.Page == null) return;
        CurrentPage = value.Page switch
        {
            "dashboard" => new DashboardViewModel(_service),
            "chat" => new ChatViewModel(_service),
            "memory" => new MemoryViewModel(_service),
            "skills" => new SkillsViewModel(_service),
            "model" => new ModelConfigViewModel(_service),
            "settings" => new SettingsViewModel(_service),
            _ => new DashboardViewModel(_service),
        };
    }
}

public record NavItem(string Icon, string Label, string Page);
