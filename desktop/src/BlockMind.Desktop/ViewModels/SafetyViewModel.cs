using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using BlockMind.Desktop.Services;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class SafetyViewModel : ObservableObject
{
    private readonly AppService _service;

    public ObservableCollection<string> AuditLog { get; } = new();

    public SafetyViewModel(AppService service)
    {
        _service = service;
    }

    [RelayCommand]
    private async Task LoadAuditLogAsync()
    {
        try
        {
            var r = await _service.PythonBridge.GetAsync("/api/safety/audit?limit=50");
            if (r == null) return;
            AuditLog.Clear();
            if (r.Value.TryGetProperty("entries", out var entries))
            {
                foreach (var e in entries.EnumerateArray())
                {
                    var time = e.TryGetProperty("time", out var t) ? t.GetString() : "";
                    var action = e.TryGetProperty("action", out var a) ? a.GetString() : "";
                    var allowed = e.TryGetProperty("allowed", out var al) && al.GetBoolean();
                    AuditLog.Add($"{time} {(allowed ? "OK" : "DENY")} {action}");
                }
            }
        }
        catch { }
    }
}
