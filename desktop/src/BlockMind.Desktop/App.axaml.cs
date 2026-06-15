using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using BlockMind.Desktop.Services;
using BlockMind.Desktop.Views;
using BlockMind.Desktop.ViewModels;
using System;

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
            var vm = new MainWindowViewModel(Service!);
            desktop.MainWindow = new MainWindow { DataContext = vm };
        }
        base.OnFrameworkInitializationCompleted();
    }
}
