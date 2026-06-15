using CommunityToolkit.Mvvm.ComponentModel;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class MarketplaceViewModel : ObservableObject
{
    [ObservableProperty] private string _searchQuery = "";
    [ObservableProperty] private string _selectedCategory = "全部";
    public ObservableCollection<MarketItem> Items { get; } = new();
}

public record MarketItem(string Name, string Author, string Description, int Downloads, bool IsInstalled);
