using CommunityToolkit.Mvvm.ComponentModel;
using System.Collections.ObjectModel;
using BlockMind.Desktop.Services;

namespace BlockMind.Desktop.ViewModels;

public partial class SkillsViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private int _enabledCount = 0;
    [ObservableProperty] private int _totalCount = 0;
    public ObservableCollection<SkillItem> Skills { get; } = new();

    public SkillsViewModel(AppService service)
    {
        _service = service;
    }
}

public record SkillItem(string Name, string Description, bool IsEnabled, string Version);
