using CommunityToolkit.Mvvm.ComponentModel;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class TasksViewModel : ObservableObject
{
    [ObservableProperty] private int _pendingCount = 0;
    [ObservableProperty] private int _runningCount = 0;
    [ObservableProperty] private int _completedCount = 0;
    public ObservableCollection<TaskItem> Tasks { get; } = new();
}

public record TaskItem(string Id, string Description, string Status, string Timestamp);
