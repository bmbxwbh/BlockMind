using BlockMind.Core.Api;
using BlockMind.Core.Config;
using System.Text.Json;

namespace BlockMind.Desktop.Services;

public class AppService : IDisposable
{
    private readonly string _configPath;
    public AppConfig Config { get; private set; }
    public ModApiClient ModClient { get; private set; }
    public AiApiClient AiClient { get; private set; }
    public PythonBridge PythonBridge { get; private set; }
    public DynmapApiClient? DynmapClient { get; private set; }

    public bool ModConnected { get; private set; }
    public bool PythonRunning { get; private set; }

    public event Action? StatusChanged;

    public AppService(string configPath = "config.json")
    {
        _configPath = configPath;
        Config = ConfigLoader.Load(configPath);
        ModClient = new ModApiClient(Config.Game.ServerIp, 25580);
        AiClient = new AiApiClient();
        PythonBridge = new PythonBridge("python", "..", Config.WebUI.Port);

        if (Config.Dynmap.Enabled)
            DynmapClient = new DynmapApiClient(Config.Dynmap.Host, Config.Dynmap.Port);
    }

    public async Task<bool> ConnectToModAsync()
    {
        ModConnected = await ModClient.IsConnectedAsync();
        StatusChanged?.Invoke();
        return ModConnected;
    }

    public async Task<bool> StartPythonAsync()
    {
        PythonRunning = await PythonBridge.StartAsync();
        StatusChanged?.Invoke();
        return PythonRunning;
    }

    public async Task StopPythonAsync()
    {
        await PythonBridge.StopAsync();
        PythonRunning = false;
        StatusChanged?.Invoke();
    }

    public void ResetConfig()
    {
        Config = new AppConfig();
        SaveConfig();
    }

    public void SaveConfig() => ConfigLoader.Save(Config, _configPath);

    public void Dispose()
    {
        PythonBridge.Dispose();
    }
}
