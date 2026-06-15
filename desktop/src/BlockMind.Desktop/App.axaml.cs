using Avalonia;
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
    private static readonly string LogFile = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "blockmind-debug.log");

    private static void Log(string msg)
    {
        try { File.AppendAllText(LogFile, $"[{DateTime.Now}] [App] {msg}\n"); } catch { }
    }

    public override void Initialize()
    {
        Log("Initialize start");
        try
        {
            AvaloniaXamlLoader.Load(this);
            Log("XAML loaded");
        }
        catch (Exception ex)
        {
            Log($"XAML load failed: {ex.Message}");
            throw;
        }

        try
        {
            Service = AppService.CreateSafe();
            Log("AppService created");
        }
        catch (Exception ex)
        {
            Log($"AppService failed: {ex.Message}");
            Service = null;
        }
    }

    public override void OnFrameworkInitializationCompleted()
    {
        Log("OnFrameworkInitializationCompleted start");
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            try
            {
                var service = Service ?? AppService.CreateSafe();
                var vm = new MainWindowViewModel(service);
                Log("ViewModel created");
                desktop.MainWindow = new MainWindow { DataContext = vm };
                Log("MainWindow created and assigned");
            }
            catch (Exception ex)
            {
                Log($"Window creation failed: {ex.Message}");
                Log($"Stack: {ex.StackTrace}");
                // Create a minimal window so the app doesn't silently exit
                desktop.MainWindow = new MainWindow { DataContext = null };
                Log("Created minimal fallback window");
            }
        }
        else
        {
            Log($"ApplicationLifetime type: {ApplicationLifetime?.GetType().Name ?? "null"}");
        }
        base.OnFrameworkInitializationCompleted();
        Log("OnFrameworkInitializationCompleted done");
    }
}
