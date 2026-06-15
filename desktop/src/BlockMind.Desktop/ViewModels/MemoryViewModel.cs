using CommunityToolkit.Mvvm.ComponentModel;
using BlockMind.Desktop.Services;

namespace BlockMind.Desktop.ViewModels;

public partial class MemoryViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private int _zoneCount;
    [ObservableProperty] private int _pathCount;
    [ObservableProperty] private int _strategyCount;

    public MemoryViewModel(AppService service) { _service = service; }
}
