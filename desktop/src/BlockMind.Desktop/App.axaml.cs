using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using BlockMind.Desktop.Services;
using BlockMind.Desktop.Views;
using BlockMind.Desktop.ViewModels;
using System;
using System.IO;

namespace BlockMind.Desktop;

public class App : Application
{
    public static AppService? Service { get; private set; }

    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
        Service = AppService.CreateSafe();
    }

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            try
            {
                var service = Service ?? AppService.CreateSafe();
                var vm = new MainWindowViewModel(service);
                desktop.MainWindow = new MainWindow { DataContext = vm };
                desktop.MainWindow.Show();
                desktop.MainWindow.Activate();
            }
            catch (Exception ex)
            {
                var logFile = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "blockmind-debug.log");
                File.AppendAllText(logFile, $"[{DateTime.Now}] Window creation failed: {ex}\n");

                var fallback = new Window
                {
                    Title = "BlockMind - Error",
                    Width = 500,
                    Height = 300,
                    WindowStartupLocation = WindowStartupLocation.CenterScreen,
                    Content = new TextBlock
                    {
                        Text = $"初始化错误：\n{ex.Message}\n\n请查看 blockmind-debug.log",
                        Margin = new Thickness(20),
                        FontSize = 14,
                        Foreground = Avalonia.Media.Brushes.White,
                    }
                };
                desktop.MainWindow = fallback;
                fallback.Show();
            }
        }
        base.OnFrameworkInitializationCompleted();
    }
}
