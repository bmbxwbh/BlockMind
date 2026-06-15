using BlockMind.Core.Api;
using BlockMind.Core.Config;
using System.Text.Json;

namespace BlockMind.Desktop.Services;

public class AppService : IDisposable
{
    private readonly string _configPath;
    public AppConfig Config { get; set; }
    public ModApiClient ModClient { get; }
    public AiApiClient AiClient { get; }
    public PythonBridge PythonBridge { get; }
    public DynmapApiClient? DynmapClient { get; }

    public bool ModConnected { get; private set; }
    public bool PythonRunning { get; private set; }

    public event Action? StatusChanged;

    private AppService(string configPath, AppConfig config)
    {
        _configPath = configPath;
        Config = config;
        ModClient = new ModApiClient(config.Game.ServerIp, 25580);
        AiClient = new AiApiClient();
        PythonBridge = new PythonBridge("python", ".", config.WebUI.Port);
        if (config.Dynmap.Enabled)
            DynmapClient = new DynmapApiClient(config.Dynmap.Host, config.Dynmap.Port);
    }

    public static AppService CreateSafe(string configPath = "config.json")
    {
        try
        {
            var config = ConfigLoader.Load(configPath);
            return new AppService(configPath, config);
        }
        catch
        {
            var config = new AppConfig();
            try { ConfigLoader.Save(config, configPath); } catch { }
            return new AppService(configPath, config);
        }
    }

    public async Task<bool> ConnectToModAsync()
    {
        try { ModConnected = await ModClient.IsConnectedAsync(); } catch { ModConnected = false; }
        StatusChanged?.Invoke();
        return ModConnected;
    }

    public async Task<bool> StartPythonAsync()
    {
        try { PythonRunning = await PythonBridge.StartAsync(); } catch { PythonRunning = false; }
        StatusChanged?.Invoke();
        return PythonRunning;
    }

    public async Task StopPythonAsync()
    {
        try { await PythonBridge.StopAsync(); } catch { }
        PythonRunning = false;
        StatusChanged?.Invoke();
    }

    public void ResetConfig()
    {
        Config = new AppConfig();
        SaveConfig();
    }

    public void SaveConfig()
    {
        try { ConfigLoader.Save(Config, _configPath); } catch { }
    }

    public void Dispose()
    {
        try { PythonBridge.Dispose(); } catch { }
    }
}
