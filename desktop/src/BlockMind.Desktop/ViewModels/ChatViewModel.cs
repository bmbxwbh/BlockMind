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
        Messages.Add(new("Bot", "Hello! I'm BlockMind, your AI companion. How can I help?", false));
    }

    [RelayCommand]
    private async Task SendAsync()
    {
        if (string.IsNullOrWhiteSpace(InputText)) return;
        var userMsg = InputText;
        InputText = "";
        Messages.Add(new("You", userMsg, true));
        IsBusy = true;

        try
        {
            _history.Add(new() { { "role", "user" }, { "content", userMsg } });
            var cfg = _service.Config.Ai.MainAgent;
            var format = cfg.Format == "anthropic"
                ? BlockMind.Core.Api.AiFormat.Anthropic
                : BlockMind.Core.Api.AiFormat.OpenAI;
            var reply = await _service.AiClient.ChatAsync(
                _history, format, cfg.BaseUrl, cfg.ApiKey, cfg.Model, cfg.Temperature, cfg.MaxTokens);

            if (reply != null)
            {
                _history.Add(new() { { "role", "assistant" }, { "content", reply } });
                Messages.Add(new("Bot", reply, false));
            }
            else
            {
                Messages.Add(new("Bot", "Sorry, the AI is not responding right now.", false));
            }
        }
        catch (Exception ex)
        {
            Messages.Add(new("Bot", $"Error: {ex.Message}", false));
        }
        finally
        {
            IsBusy = false;
        }
    }
}

public record ChatMessageViewModel(string Sender, string Text, bool IsUser);
