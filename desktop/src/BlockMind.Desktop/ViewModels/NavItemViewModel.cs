using CommunityToolkit.Mvvm.ComponentModel;

namespace BlockMind.Desktop.ViewModels;

public partial class NavItemViewModel : ObservableObject
{
    public string IconName { get; }
    public string Label { get; }
    public string Page { get; }
    [ObservableProperty] private bool _isSelected;

    public NavItemViewModel(string icon, string label, string page)
    {
        IconName = icon;
        Label = label;
        Page = page;
    }
}
