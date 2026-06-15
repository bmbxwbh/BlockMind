using CommunityToolkit.Mvvm.ComponentModel;
using System.Collections.ObjectModel;

namespace BlockMind.Desktop.ViewModels;

public partial class ModelConfigViewModel : ObservableObject
{
    [ObservableProperty] private string _selectedModel = "";
    [ObservableProperty] private double _temperature = 0.7;
    [ObservableProperty] private int _maxTokens = 2048;
    [ObservableProperty] private bool _isStreaming = true;
    public ObservableCollection<string> AvailableModels { get; } = new();
}
