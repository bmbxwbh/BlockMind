using CommunityToolkit.Mvvm.ComponentModel;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class SkillsViewModel : ObservableObject
{
    [ObservableProperty] private int _enabledCount = 0;
    [ObservableProperty] private int _totalCount = 0;
    public ObservableCollection<SkillItem> Skills { get; } = new();
}

public record SkillItem(string Name, string Description, bool IsEnabled, string Version);
