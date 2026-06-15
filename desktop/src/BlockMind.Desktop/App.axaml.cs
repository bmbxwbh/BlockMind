using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using BlockMind.Desktop.Services;
using BlockMind.Desktop.Views;
using System;

namespace BlockMind.Desktop;

public class App : Application
{
    public static AppService? Service { get; private set; }

    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
        try
        {
            Service = new AppService();
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"[BlockMind] Failed to initialize AppService: {ex.Message}");
            Service = new AppService("config.json");
        }
    }

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            try
            {
                desktop.MainWindow = new MainWindow
                {
                    DataContext = new ViewModels.MainWindowViewModel(Service!)
                };
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"[BlockMind] Failed to create window: {ex.Message}");
            }
        }
        base.OnFrameworkInitializationCompleted();
    }
}
