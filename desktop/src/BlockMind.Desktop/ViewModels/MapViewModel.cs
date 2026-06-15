using CommunityToolkit.Mvvm.ComponentModel;

namespace BlockMind.Desktop.ViewModels;

public partial class MapViewModel : ObservableObject
{
    [ObservableProperty] private string _worldName = "主世界";
    [ObservableProperty] private string _playerPosition = "0, 64, 0";
    [ObservableProperty] private double _mapZoom = 1.0;
    [ObservableProperty] private bool _showEntities = true;
    [ObservableProperty] private bool _showPlayers = true;
}
