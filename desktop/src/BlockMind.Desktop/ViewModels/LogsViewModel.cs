using CommunityToolkit.Mvvm.ComponentModel;
using BlockMind.Desktop.Services;

namespace BlockMind.Desktop.ViewModels;

public partial class LogsViewModel : ObservableObject
{
    private readonly AppService _service;

    public LogsViewModel(AppService service) { _service = service; }
}
