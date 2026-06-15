using Avalonia.Controls;
using Avalonia.Input;
using BlockMind.Desktop.ViewModels;

namespace BlockMind.Desktop.Views;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }

    private void NavBorder_PointerPressed(object? sender, PointerPressedEventArgs e)
    {
        if (sender is Border border && border.Tag is NavItemViewModel item)
        {
            if (DataContext is MainWindowViewModel vm)
            {
                vm.SelectedNav = item;
            }
        }
    }
}
