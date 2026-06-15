using CommunityToolkit.Mvvm.ComponentModel;
using BlockMind.Desktop.Services;

namespace BlockMind.Desktop.ViewModels;

public partial class MapViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private string _worldName = "overworld";
    [ObservableProperty] private string _playerPosition = "0, 64, 0";
    [ObservableProperty] private double _mapZoom = 1.0;
    [ObservableProperty] private bool _showEntities = true;
    [ObservableProperty] private bool _showPlayers = true;

    public MapViewModel(AppService service) { _service = service; }
}
