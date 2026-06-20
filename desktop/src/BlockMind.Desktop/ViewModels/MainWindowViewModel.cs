using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using BlockMind.Desktop.Services;

namespace BlockMind.Desktop.ViewModels;

public partial class MainWindowViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private object? _currentPage;
    [ObservableProperty] private NavItemViewModel? _selectedNav;
    [ObservableProperty] private bool _modConnected;
    [ObservableProperty] private bool _pythonRunning;
    [ObservableProperty] private string _statusText = "未连接";
    [ObservableProperty] private string _langLabel = "EN";

    public ObservableCollection<NavItemViewModel> NavItems { get; } = new();

    public MainWindowViewModel(AppService service)
    {
        _service = service;
        _service.StatusChanged += OnServiceStatusChanged;
        Lang.Load("zh");
        RebuildNav();
        NavItems[0].IsSelected = true;
        _selectedNav = NavItems[0];
        CurrentPage = new DashboardViewModel(service);
        StatusText = "未连接";
    }

    [RelayCommand]
    private void ToggleLang()
    {
        Lang.Toggle();
        LangLabel = Lang.Current == "zh" ? "EN" : "中文";
        RebuildNav();
        StatusText = Lang.T(PythonRunning ? "Running" : (ModConnected ? "Connected" : "Not connected"));
    }

    private void RebuildNav()
    {
        NavItems.Clear();
        NavItems.Add(new(Lang.T("仪表盘"), "dashboard"));
        NavItems.Add(new(Lang.T("地图"), "map"));
        NavItems.Add(new(Lang.T("AI 对话"), "chat"));
        NavItems.Add(new(Lang.T("记忆系统"), "memory"));
        NavItems.Add(new(Lang.T("技能管理"), "skills"));
        NavItems.Add(new(Lang.T("技能市场"), "marketplace"));
        NavItems.Add(new(Lang.T("模型配置"), "model"));
        NavItems.Add(new(Lang.T("安全设置"), "safety"));
        NavItems.Add(new(Lang.T("任务队列"), "tasks"));
        NavItems.Add(new(Lang.T("日志中心"), "logs"));
        NavItems.Add(new(Lang.T("设置"), "settings"));
    }

    [RelayCommand]
    private async Task ToggleBlockMindAsync()
    {
        if (PythonRunning) await _service.StopPythonAsync();
        else await _service.StartPythonAsync();
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
        StatusText = PythonRunning ? "运行中" : (ModConnected ? "已连接" : "未连接");
    }

    partial void OnSelectedNavChanged(NavItemViewModel? value)
    {
        if (value == null) return;
        foreach (var nav in NavItems) nav.IsSelected = false;
        value.IsSelected = true;

        CurrentPage = value.Page switch
        {
            "dashboard" => new DashboardViewModel(_service),
            "chat" => new ChatViewModel(_service),
            "memory" => new MemoryViewModel(_service),
            "skills" => new SkillsViewModel(_service),
            "model" => new ModelConfigViewModel(_service),
            "settings" => new SettingsViewModel(_service),
            "map" => new MapViewModel(_service),
            "marketplace" => new MarketplaceViewModel(_service),
            "safety" => new SafetyViewModel(_service),
            "tasks" => new TasksViewModel(_service),
            "logs" => new LogsViewModel(_service),
            _ => new DashboardViewModel(_service),
        };
    }
}

public partial class NavItemViewModel : ObservableObject
{
    public string Label { get; }
    public string Page { get; }
    [ObservableProperty] private bool _isSelected;

    public NavItemViewModel(string label, string page)
    {
        Label = label;
        Page = page;
    }
}
