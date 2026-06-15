using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using BlockMind.Desktop.Services;
using System.Text.Json;

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

    public DashboardViewModel(AppService service)
    {
        _service = service;
        _pollTimer = new System.Timers.Timer(2000);
        _pollTimer.Elapsed += (s, e) => PollStatusAsync();
        _pollTimer.AutoReset = true;
        _pollTimer.Start();
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
