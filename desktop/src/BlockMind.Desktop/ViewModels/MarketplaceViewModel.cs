using CommunityToolkit.Mvvm.ComponentModel;
using BlockMind.Desktop.Services;

namespace BlockMind.Desktop.ViewModels;

public partial class MarketplaceViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private string _searchQuery = "";

    public MarketplaceViewModel(AppService service) { _service = service; }
}
