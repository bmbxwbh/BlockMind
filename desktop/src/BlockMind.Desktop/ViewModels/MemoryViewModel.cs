using CommunityToolkit.Mvvm.ComponentModel;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class MemoryViewModel : ObservableObject
{
    [ObservableProperty] private int _totalMemories = 0;
    [ObservableProperty] private int _recentMemories = 0;
    [ObservableProperty] private string _searchQuery = "";
    public ObservableCollection<MemoryEntry> Memories { get; } = new();
}

public record MemoryEntry(string Id, string Content, string Timestamp, string Type);
