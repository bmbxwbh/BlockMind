using CommunityToolkit.Mvvm.ComponentModel;
using BlockMind.Desktop.Services;

namespace BlockMind.Desktop.ViewModels;

public partial class SettingsViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private string _selectedTheme = "dark";

    public SettingsViewModel(AppService service) { _service = service; }
}
