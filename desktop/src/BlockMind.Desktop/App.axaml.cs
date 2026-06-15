using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using BlockMind.Desktop.Services;
using BlockMind.Desktop.Views;

namespace BlockMind.Desktop;

public class App : Application
{
    public static AppService? Service { get; private set; }

    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
        Service = new AppService();
    }

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            desktop.MainWindow = new MainWindow
            {
                DataContext = new ViewModels.MainWindowViewModel(Service!)
            };
        }
        base.OnFrameworkInitializationCompleted();
    }
}
