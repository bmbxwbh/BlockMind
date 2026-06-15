using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using BlockMind.Desktop.Services;
using BlockMind.Core.Config;

namespace BlockMind.Desktop.ViewModels;

public partial class ModelConfigViewModel : ObservableObject
{
    private readonly AppService _service;

    [ObservableProperty] private string _mainFormat = "openai";
    [ObservableProperty] private string _mainBaseUrl = "https://api.openai.com/v1";
    [ObservableProperty] private string _mainApiKey = "";
    [ObservableProperty] private string _mainModel = "gpt-4o";
    [ObservableProperty] private float _mainTemperature = 0.7f;
    [ObservableProperty] private int _mainMaxTokens = 2000;
    [ObservableProperty] private bool _mainTestOk;
    [ObservableProperty] private string _mainTestStatus = "";

    [ObservableProperty] private string _opFormat = "openai";
    [ObservableProperty] private string _opBaseUrl = "https://api.openai.com/v1";
    [ObservableProperty] private string _opApiKey = "";
    [ObservableProperty] private string _opModel = "gpt-4o";
    [ObservableProperty] private float _opTemperature = 0.3f;
    [ObservableProperty] private int _opMaxTokens = 4000;
    [ObservableProperty] private bool _opTestOk;
    [ObservableProperty] private string _opTestStatus = "";

    public ModelConfigViewModel(AppService service)
    {
        _service = service;
        LoadFromConfig();
    }

    private void LoadFromConfig()
    {
        var cfg = _service.Config.Ai;
        MainFormat = cfg.MainAgent.Format;
        MainBaseUrl = cfg.MainAgent.BaseUrl;
        MainApiKey = cfg.MainAgent.ApiKey;
        MainModel = cfg.MainAgent.Model;
        MainTemperature = cfg.MainAgent.Temperature;
        MainMaxTokens = cfg.MainAgent.MaxTokens;

        OpFormat = cfg.OperationAgent.Format;
        OpBaseUrl = cfg.OperationAgent.BaseUrl;
        OpApiKey = cfg.OperationAgent.ApiKey;
        OpModel = cfg.OperationAgent.Model;
        OpTemperature = cfg.OperationAgent.Temperature;
        OpMaxTokens = cfg.OperationAgent.MaxTokens;
    }

    [RelayCommand]
    private async Task TestMainConnectionAsync()
    {
        MainTestStatus = "Testing...";
        var cfg = new AiAgentConfig
        {
            Format = MainFormat, BaseUrl = MainBaseUrl,
            ApiKey = MainApiKey, Model = MainModel,
        };
        var format = MainFormat == "anthropic"
            ? BlockMind.Core.Api.AiFormat.Anthropic
            : BlockMind.Core.Api.AiFormat.OpenAI;
        var ok = await _service.AiClient.TestConnectionAsync(format, MainBaseUrl, MainApiKey, MainModel);
        MainTestOk = ok;
        MainTestStatus = ok ? "Connected" : "Failed";
    }

    [RelayCommand]
    private async Task TestOpConnectionAsync()
    {
        OpTestStatus = "Testing...";
        var format = OpFormat == "anthropic"
            ? BlockMind.Core.Api.AiFormat.Anthropic
            : BlockMind.Core.Api.AiFormat.OpenAI;
        var ok = await _service.AiClient.TestConnectionAsync(format, OpBaseUrl, OpApiKey, OpModel);
        OpTestOk = ok;
        OpTestStatus = ok ? "Connected" : "Failed";
    }

    [RelayCommand]
    private void SaveConfig()
    {
        var cfg = _service.Config.Ai;
        cfg.MainAgent.Format = MainFormat;
        cfg.MainAgent.BaseUrl = MainBaseUrl;
        cfg.MainAgent.ApiKey = MainApiKey;
        cfg.MainAgent.Model = MainModel;
        cfg.MainAgent.Temperature = MainTemperature;
        cfg.MainAgent.MaxTokens = MainMaxTokens;

        cfg.OperationAgent.Format = OpFormat;
        cfg.OperationAgent.BaseUrl = OpBaseUrl;
        cfg.OperationAgent.ApiKey = OpApiKey;
        cfg.OperationAgent.Model = OpModel;
        cfg.OperationAgent.Temperature = OpTemperature;
        cfg.OperationAgent.MaxTokens = OpMaxTokens;

        _service.SaveConfig();
    }
}
