using CommunityToolkit.Mvvm.ComponentModel;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class LogsViewModel : ObservableObject
{
    [ObservableProperty] private string _filterLevel = "All";
    [ObservableProperty] private string _searchQuery = "";
    [ObservableProperty] private bool _autoScroll = true;
    public ObservableCollection<LogEntry> Logs { get; } = new();
}

public record LogEntry(string Timestamp, string Level, string Source, string Message);
