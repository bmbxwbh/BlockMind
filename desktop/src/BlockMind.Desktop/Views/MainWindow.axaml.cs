using Avalonia.Controls;
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
}
