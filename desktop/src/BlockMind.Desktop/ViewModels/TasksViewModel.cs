using CommunityToolkit.Mvvm.ComponentModel;
using BlockMind.Desktop.Services;

namespace BlockMind.Desktop.ViewModels;

public partial class TasksViewModel : ObservableObject
{
    private readonly AppService _service;

    public TasksViewModel(AppService service) { _service = service; }
}
