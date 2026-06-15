using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using BlockMind.Desktop.Services;

namespace BlockMind.Desktop.ViewModels;

public partial class DashboardViewModel : ObservableObject
{
    private readonly AppService _service;
    private readonly System.Timers.Timer _pollTimer;

    [ObservableProperty] private double _health = 20;
    [ObservableProperty] private double _hunger = 20;
    [ObservableProperty] private string _position = "0, 64, 0";
    [ObservableProperty] private string _dimension = "主世界";
    [ObservableProperty] private bool _modConnected;
    [ObservableProperty] private bool _pythonRunning;
    [ObservableProperty] private string _statusText = "未连接";

    public ObservableCollection<string> RecentEvents { get; } = new();

    public DashboardViewModel(AppService service)
    {
        _service = service;
        _service.StatusChanged += OnServiceStatusChanged;
        ModConnected = _service.ModConnected;
        PythonRunning = _service.PythonRunning;
        StatusText = ModConnected ? (PythonRunning ? "运行中" : "Mod已连接") : "未连接";

        _pollTimer = new System.Timers.Timer(2000);
        _pollTimer.Elapsed += (s, e) => PollStatusAsync();
        _pollTimer.AutoReset = true;
        _pollTimer.Start();
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

    private async void PollStatusAsync()
    {
        if (!_service.ModConnected) return;
        try
        {
            var status = await _service.ModClient.GetStatusAsync();
            if (status.HasValue)
            {
                var s = status.Value;
                Health = s.GetProperty("health").GetDouble();
                Hunger = s.GetProperty("hunger").GetDouble();
                var pos = s.GetProperty("position");
                Position = $"{pos.GetProperty("x").GetDouble():F0}, {pos.GetProperty("y").GetDouble():F0}, {pos.GetProperty("z").GetDouble():F0}";
                Dimension = s.TryGetProperty("dimension", out var d) ? d.GetString() ?? "" : "";
            }
        }
        catch { }
    }
}
