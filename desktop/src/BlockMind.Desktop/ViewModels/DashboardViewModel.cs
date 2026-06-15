using CommunityToolkit.Mvvm.ComponentModel;

namespace BlockMind.Desktop.ViewModels;

public partial class DashboardViewModel : ObservableObject
{
    [ObservableProperty] private double _health = 20;
    [ObservableProperty] private double _hunger = 20;
    [ObservableProperty] private string _position = "0, 64, 0";
    [ObservableProperty] private string _dimension = "主世界";
}
