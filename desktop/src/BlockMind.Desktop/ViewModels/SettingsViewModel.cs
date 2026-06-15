using CommunityToolkit.Mvvm.ComponentModel;
using BlockMind.Desktop.Services;

namespace BlockMind.Desktop.ViewModels;

public partial class SettingsViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private string _language = "zh-CN";
    [ObservableProperty] private bool _minimizeToTray = true;
    [ObservableProperty] private bool _autoStart = false;
    [ObservableProperty] private int _webUiPort = 19951;
    [ObservableProperty] private string _theme = "Dark";

    public SettingsViewModel(AppService service)
    {
        _service = service;
    }
}
