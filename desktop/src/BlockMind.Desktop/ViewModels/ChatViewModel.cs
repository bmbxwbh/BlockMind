using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using BlockMind.Desktop.Services;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class ChatViewModel : ObservableObject
{
    private readonly AppService _service;
    private readonly List<Dictionary<string, string>> _history = new();

    [ObservableProperty] private string _inputText = "";
    [ObservableProperty] private bool _isBusy;

    public ObservableCollection<ChatMessageViewModel> Messages { get; } = new();

    public ChatViewModel(AppService service)
    {
        _service = service;
        Messages.Add(new("🤖", "你好！我是 BlockMind，你的 AI 玩伴。有什么可以帮你的？", false, DateTime.Now));
    }

    [RelayCommand]
    private async Task SendAsync()
    {
        if (string.IsNullOrWhiteSpace(InputText)) return;

        var userMsg = InputText;
        InputText = "";
        Messages.Add(new("👤", userMsg, true, DateTime.Now));
        IsBusy = true;

        try
        {
            _history.Add(new() { { "role", "user" }, { "content", userMsg } });

            var aiConfig = _service.Config.Ai.MainAgent;
            var format = aiConfig.Format == "anthropic" ? Core.Api.AiFormat.Anthropic : Core.Api.AiFormat.OpenAI;
            var reply = await _service.AiClient.ChatAsync(_history, format, aiConfig.BaseUrl, aiConfig.ApiKey, aiConfig.Model, aiConfig.Temperature, aiConfig.MaxTokens);

            if (reply != null)
            {
                _history.Add(new() { { "role", "assistant" }, { "content", reply } });
                Messages.Add(new("🤖", reply, false, DateTime.Now));
            }
            else
            {
                Messages.Add(new("🤖", "抱歉，AI 暂时无法回复。", false, DateTime.Now));
            }
        }
        catch (Exception ex)
        {
            Messages.Add(new("🤖", $"错误: {ex.Message}", false, DateTime.Now));
        }
        finally
        {
            IsBusy = false;
        }
    }
}

public record ChatMessageViewModel(string Sender, string Text, bool IsUser, DateTime Timestamp);
