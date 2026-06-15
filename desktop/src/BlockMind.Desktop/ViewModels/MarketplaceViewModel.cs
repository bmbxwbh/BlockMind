using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using BlockMind.Desktop.Services;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class MarketplaceViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private string _searchQuery = "";
    [ObservableProperty] private bool _isLoading;

    public ObservableCollection<MarketplaceItem> Items { get; } = new();

    public MarketplaceViewModel(AppService service)
    {
        _service = service;
    }

    [RelayCommand]
    private async Task SearchAsync()
    {
        IsLoading = true;
        try
        {
            var q = string.IsNullOrWhiteSpace(SearchQuery) ? "" : $"?q={Uri.EscapeDataString(SearchQuery)}";
            var r = await _service.PythonBridge.GetAsync($"/api/marketplace/search{q}");
            if (r == null) return;
            Items.Clear();
            foreach (var item in r.Value.EnumerateArray())
            {
                Items.Add(new MarketplaceItem
                {
                    SkillId = item.GetProperty("skill_id").GetString() ?? "",
                    Name = item.GetProperty("name").GetString() ?? "",
                    Description = item.TryGetProperty("description", out var d) ? d.GetString() ?? "" : "",
                    Rating = item.TryGetProperty("rating", out var rat) ? rat.GetDouble() : 0,
                });
            }
        }
        catch { }
        finally { IsLoading = false; }
    }

    [RelayCommand]
    private async Task InstallAsync(string skillId)
    {
        try
        {
            await _service.PythonBridge.PostAsync($"/api/marketplace/{skillId}/install", new { });
            await SearchAsync();
        }
        catch { }
    }
}

public class MarketplaceItem
{
    public string SkillId { get; set; } = "";
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
    public double Rating { get; set; }
}
