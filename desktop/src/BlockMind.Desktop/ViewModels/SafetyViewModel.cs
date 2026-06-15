using CommunityToolkit.Mvvm.ComponentModel;

namespace BlockMind.Desktop.ViewModels;

public partial class SafetyViewModel : ObservableObject
{
    [ObservableProperty] private bool _autoReply = true;
    [ObservableProperty] private bool _commandWhitelist = false;
    [ObservableProperty] private int _maxCommandsPerMinute = 10;
    [ObservableProperty] private bool _logAllActions = true;
    [ObservableProperty] private bool _confirmDangerous = true;
}
