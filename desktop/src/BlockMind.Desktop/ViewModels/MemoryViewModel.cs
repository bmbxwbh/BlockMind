using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using BlockMind.Desktop.Services;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class MemoryViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private int _zoneCount;
    [ObservableProperty] private int _pathCount;
    [ObservableProperty] private int _strategyCount;
    [ObservableProperty] private int _playerCount;

    public ObservableCollection<string> Zones { get; } = new();
    public ObservableCollection<string> Paths { get; } = new();
    public ObservableCollection<string> Strategies { get; } = new();

    public MemoryViewModel(AppService service)
    {
        _service = service;
    }

    [RelayCommand]
    private async Task LoadMemoryAsync()
    {
        try
        {
            var mem = await _service.PythonBridge.GetAsync("/api/memory");
            if (mem == null) return;
            var m = mem.Value;

            ZoneCount = m.GetProperty("zones").GetInt32();
            PathCount = m.GetProperty("cached_paths").GetInt32();
            StrategyCount = m.GetProperty("strategies").GetInt32();
            PlayerCount = m.GetProperty("players").GetInt32();
        }
        catch { }
    }

    [RelayCommand]
    private async Task BackupMemoryAsync()
    {
        try
        {
            var r = await _service.PythonBridge.GetAsync("/api/memory/backup");
            if (r?.GetProperty("success").GetBoolean() == true)
            {
                // Show success notification
            }
        }
        catch { }
    }

    [RelayCommand]
    private async Task CleanupMemoryAsync()
    {
        try
        {
            var r = await _service.PythonBridge.PostAsync("/api/memory/cleanup", new { });
            if (r?.GetProperty("success").GetBoolean() == true)
            {
                await LoadMemoryAsync();
            }
        }
        catch { }
    }
}
