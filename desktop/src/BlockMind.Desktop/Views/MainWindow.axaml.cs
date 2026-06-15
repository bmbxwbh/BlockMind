using Avalonia.Controls;
using Avalonia.Interactivity;
using BlockMind.Desktop.ViewModels;
using System;
using System.IO;

namespace BlockMind.Desktop.Views;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        try
        {
            InitializeComponent();
        }
        catch (Exception ex)
        {
            var logFile = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "blockmind-debug.log");
            File.AppendAllText(logFile, $"[{DateTime.Now}] [MainWindow] ERROR: {ex}\n");
        }
    }

    private void NavBorder_Tapped(object? sender, TappedEventArgs e)
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
