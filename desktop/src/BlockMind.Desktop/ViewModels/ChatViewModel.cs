using CommunityToolkit.Mvvm.ComponentModel;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class ChatViewModel : ObservableObject
{
    [ObservableProperty] private string _inputMessage = "";
    [ObservableProperty] private bool _isProcessing = false;
    public ObservableCollection<ChatMessage> Messages { get; } = new();
}

public record ChatMessage(string Role, string Content, string Timestamp);
