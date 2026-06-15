using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using BlockMind.Desktop.Services;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class SkillsViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private string _searchQuery = "";
    [ObservableProperty] private string _selectedSkillYaml = "";
    [ObservableProperty] private bool _isLoading;

    public ObservableCollection<SkillListItem> Skills { get; } = new();

    public SkillsViewModel(AppService service)
    {
        _service = service;
    }

    [RelayCommand]
    private async Task LoadSkillsAsync()
    {
        IsLoading = true;
        try
        {
            var r = await _service.PythonBridge.GetAsync("/api/skills");
            if (r == null) return;
            Skills.Clear();
            foreach (var item in r.Value.EnumerateArray())
            {
                Skills.Add(new SkillListItem
                {
                    SkillId = item.GetProperty("skill_id").GetString() ?? "",
                    Name = item.GetProperty("name").GetString() ?? "",
                    Tags = item.TryGetProperty("tags", out var t) ? string.Join(", ", t.EnumerateArray().Select(x => x.GetString())) : "",
                });
            }
        }
        catch { }
        finally { IsLoading = false; }
    }

    [RelayCommand]
    private async Task ExecuteSkillAsync(string skillId)
    {
        try
        {
            var r = await _service.PythonBridge.PostAsync($"/api/skills/{skillId}/execute", new { });
            if (r?.GetProperty("success").GetBoolean() == true)
            {
                // Show success
            }
        }
        catch { }
    }

    [RelayCommand]
    private async Task DeleteSkillAsync(string skillId)
    {
        try
        {
            await _service.PythonBridge.PostAsync($"/api/skills/{skillId}", new { _method = "DELETE" });
            await LoadSkillsAsync();
        }
        catch { }
    }
}

public class SkillListItem
{
    public string SkillId { get; set; } = "";
    public string Name { get; set; } = "";
    public string Tags { get; set; } = "";
}
