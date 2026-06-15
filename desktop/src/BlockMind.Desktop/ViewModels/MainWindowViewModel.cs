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

    public ObservableCollection<NavItemViewModel> NavItems { get; } = new()
    {
        new("layout-dashboard", "Dashboard", "dashboard"),
        new("map", "Map", "map"),
        new("message-square", "AI Chat", "chat"),
        new("brain", "Memory", "memory"),
        new("wrench", "Skills", "skills"),
        new("shopping-bag", "Marketplace", "marketplace"),
        new("bot", "Model Config", "model"),
        new("shield", "Safety", "safety"),
        new("refresh-cw", "Tasks", "tasks"),
        new("file-text", "Logs", "logs"),
        new("settings", "Settings", "settings"),
    };

    public MainWindowViewModel(AppService service)
    {
        _service = service;
        _service.StatusChanged += OnServiceStatusChanged;
        NavItems[0].IsSelected = true;
        _selectedNav = NavItems[0];
        CurrentPage = new DashboardViewModel(service);
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
        StatusText = PythonRunning ? "运行中" : (ModConnected ? "Mod 已连接" : "未连接");
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
