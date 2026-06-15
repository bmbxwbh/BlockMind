using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using BlockMind.Desktop.Services;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class TasksViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private int _pendingCount;
    [ObservableProperty] private int _runningCount;
    [ObservableProperty] private int _completedCount;

    public ObservableCollection<string> Tasks { get; } = new();

    public TasksViewModel(AppService service)
    {
        _service = service;
    }

    [RelayCommand]
    private async Task LoadTasksAsync()
    {
        try
        {
            var r = await _service.PythonBridge.GetAsync("/api/tasks/queue");
            if (r == null) return;
            var v = r.Value;
            PendingCount = v.TryGetProperty("pending", out var p) ? p.GetInt32() : 0;
            RunningCount = v.TryGetProperty("running", out var ru) ? ru.GetInt32() : 0;
            CompletedCount = v.TryGetProperty("completed", out var c) ? c.GetInt32() : 0;
        }
        catch { }
    }
}
