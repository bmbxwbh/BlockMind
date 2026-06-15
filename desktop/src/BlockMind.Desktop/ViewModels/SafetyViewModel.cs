using CommunityToolkit.Mvvm.ComponentModel;
using BlockMind.Desktop.Services;

namespace BlockMind.Desktop.ViewModels;

public partial class SafetyViewModel : ObservableObject
{
    private readonly AppService _service;

    public SafetyViewModel(AppService service) { _service = service; }
}
