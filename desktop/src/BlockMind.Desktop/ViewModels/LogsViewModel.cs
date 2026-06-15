using CommunityToolkit.Mvvm.ComponentModel;
using BlockMind.Desktop.Services;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class LogsViewModel : ObservableObject
{
    private readonly AppService _service;

    public ObservableCollection<string> Logs { get; } = new();

    public LogsViewModel(AppService service)
    {
        _service = service;
    }
}
