using Avalonia.Controls;
using Avalonia.Input;
using BlockMind.Desktop.ViewModels;
using System;
using System.IO;

namespace BlockMind.Desktop.Views;

public partial class MainWindow : Window
{
    private static readonly string LogFile = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "blockmind-debug.log");

    private static void Log(string msg)
    {
        try { File.AppendAllText(LogFile, $"[{DateTime.Now}] [MainWindow] {msg}\n"); } catch { }
    }

    public MainWindow()
    {
        Log("MainWindow constructor start");
        try
        {
            InitializeComponent();
            Log("InitializeComponent done");
        }
        catch (Exception ex)
        {
            Log($"InitializeComponent failed: {ex.Message}");
            Log($"Stack: {ex.StackTrace}");
            throw;
        }
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
