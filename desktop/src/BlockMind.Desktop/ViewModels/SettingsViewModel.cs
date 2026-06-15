using CommunityToolkit.Mvvm.ComponentModel;

namespace BlockMind.Desktop.ViewModels;

public partial class SettingsViewModel : ObservableObject
{
    [ObservableProperty] private string _language = "zh-CN";
    [ObservableProperty] private bool _minimizeToTray = true;
    [ObservableProperty] private bool _autoStart = false;
    [ObservableProperty] private int _webUiPort = 19951;
    [ObservableProperty] private string _theme = "Dark";
}
