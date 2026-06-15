using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using BlockMind.Desktop.Services;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class MapViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private string _worldName = "overworld";
    [ObservableProperty] private string _playerPosition = "0, 64, 0";
    [ObservableProperty] private bool _dynmapConnected;
    [ObservableProperty] private string _dynmapUrl = "";

    public MapViewModel(AppService service)
    {
        _service = service;
    }

    [RelayCommand]
    private async Task CheckDynmapAsync()
    {
        if (_service.DynmapClient == null) { DynmapConnected = false; return; }
        DynmapConnected = await _service.DynmapClient.IsConnectedAsync();
        if (DynmapConnected) DynmapUrl = $"http://{_service.Config.Dynmap.Host}:{_service.Config.Dynmap.Port}";
    }
}
