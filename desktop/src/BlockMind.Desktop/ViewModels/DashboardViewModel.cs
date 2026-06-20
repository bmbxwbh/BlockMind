using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;
using BlockMind.Desktop.Services;

namespace BlockMind.Desktop.ViewModels;

public partial class DashboardViewModel : ObservableObject
{
    private readonly AppService _service;
    private readonly System.Timers.Timer _pollTimer;

    [ObservableProperty] private double _health;
    [ObservableProperty] private double _hunger;
    [ObservableProperty] private string _position = "--";
    [ObservableProperty] private string _dimension = "--";
    [ObservableProperty] private bool _modConnected;
    [ObservableProperty] private bool _pythonRunning;
    [ObservableProperty] private string _statusText = "未连接";
    [ObservableProperty] private bool _hasRealData;

    public ObservableCollection<string> RecentEvents { get; } = new();

    public DashboardViewModel(AppService service)
    {
        _service = service;
        _service.StatusChanged += OnServiceStatusChanged;
        ModConnected = _service.ModConnected;
        PythonRunning = _service.PythonRunning;
        UpdateStatus();

        _pollTimer = new System.Timers.Timer(2000);
        _pollTimer.Elapsed += (s, e) => PollStatusAsync();
        _pollTimer.AutoReset = true;
        _pollTimer.Start();
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
        UpdateStatus();
    }

    private void OnServiceStatusChanged()
    {
        ModConnected = _service.ModConnected;
        PythonRunning = _service.PythonRunning;
        UpdateStatus();
    }

    private void UpdateStatus()
    {
        StatusText = PythonRunning ? "运行中" : (ModConnected ? "已连接" : "未连接");
    }

    private async void PollStatusAsync()
    {
        if (!_service.ModConnected)
        {
            HasRealData = false;
            return;
        }
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
                HasRealData = true;
            }
        }
        catch
        {
            HasRealData = false;
        }
    }
}
