using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using BlockMind.Desktop.Services;

namespace BlockMind.Desktop.ViewModels;

public partial class SettingsViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private string _mcMode = "server";
    [ObservableProperty] private string _mcVersion = "1.20.4";
    [ObservableProperty] private string _maxRam = "2G";
    [ObservableProperty] private bool _dynmapEnabled;
    [ObservableProperty] private int _dynmapPort = 8163;
    [ObservableProperty] private string _selectedTheme = "dark";
    [ObservableProperty] private string _selectedLanguage = "zh";

    public SettingsViewModel(AppService service)
    {
        _service = service;
        LoadFromConfig();
    }

    private void LoadFromConfig()
    {
        var cfg = _service.Config;
        McVersion = cfg.Game.Version;
        DynmapEnabled = cfg.Dynmap.Enabled;
        DynmapPort = cfg.Dynmap.Port;
    }

    [RelayCommand]
    private void SaveSettings()
    {
        var cfg = _service.Config;
        cfg.Game.Version = McVersion;
        cfg.Dynmap.Enabled = DynmapEnabled;
        cfg.Dynmap.Port = DynmapPort;
        _service.SaveConfig();
    }

    [RelayCommand]
    private void ResetSettings()
    {
        _service.Config = new BlockMind.Core.Config.AppConfig();
        _service.SaveConfig();
        LoadFromConfig();
    }
}
