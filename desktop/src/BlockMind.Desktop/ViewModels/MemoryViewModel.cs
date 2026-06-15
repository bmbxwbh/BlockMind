using CommunityToolkit.Mvvm.ComponentModel;
using System.Collections.ObjectModel;
using BlockMind.Desktop.Services;

namespace BlockMind.Desktop.ViewModels;

public partial class MemoryViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private int _totalMemories = 0;
    [ObservableProperty] private int _recentMemories = 0;
    [ObservableProperty] private string _searchQuery = "";
    public ObservableCollection<MemoryEntry> Memories { get; } = new();

    public MemoryViewModel(AppService service)
    {
        _service = service;
    }
}

public record MemoryEntry(string Id, string Content, string Timestamp, string Type);
