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
    [ObservableProperty] private string _statusText = "";
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
        NavItems.Add(new("layout-dashboard", Lang.T("Dashboard"), "dashboard"));
        NavItems.Add(new("map", Lang.T("Map"), "map"));
        NavItems.Add(new("message-square", Lang.T("AI Chat"), "chat"));
        NavItems.Add(new("brain", Lang.T("Memory"), "memory"));
        NavItems.Add(new("wrench", Lang.T("Skills"), "skills"));
        NavItems.Add(new("shopping-bag", Lang.T("Marketplace"), "marketplace"));
        NavItems.Add(new("bot", Lang.T("Model Config"), "model"));
        NavItems.Add(new("shield", Lang.T("Safety"), "safety"));
        NavItems.Add(new("refresh-cw", Lang.T("Tasks"), "tasks"));
        NavItems.Add(new("file-text", Lang.T("Logs"), "logs"));
        NavItems.Add(new("settings", Lang.T("Settings"), "settings"));
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
        StatusText = ModConnected ? Lang.T("Connected") : Lang.T("Not connected");
    }

    private void OnServiceStatusChanged()
    {
        ModConnected = _service.ModConnected;
        PythonRunning = _service.PythonRunning;
        StatusText = PythonRunning ? Lang.T("Running") : (ModConnected ? Lang.T("Connected") : Lang.T("Not connected"));
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
