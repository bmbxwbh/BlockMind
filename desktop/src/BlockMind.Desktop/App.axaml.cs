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
                var window = new MainWindow { DataContext = vm };
                desktop.MainWindow = window;
                Log("MainWindow assigned");
                window.Show();
                window.Activate();
                Log("MainWindow Show/Activate called");
            }
            catch (Exception ex)
            {
                Log($"Window creation failed: {ex.Message}");
                Log($"Stack: {ex.StackTrace}");
                try
                {
                    var fallback = new Window
                    {
                        Title = "BlockMind - Error",
                        Width = 600,
                        Height = 400,
                        Content = new Avalonia.Controls.TextBlock
                        {
                            Text = $"Initialization error:\n{ex.Message}\n\nSee blockmind-debug.log for details.",
                            Margin = new Avalonia.Thickness(20),
                            FontSize = 14,
                        }
                    };
                    desktop.MainWindow = fallback;
                    fallback.Show();
                    Log("Fallback window shown");
                }
                catch (Exception ex2)
                {
                    Log($"Even fallback window failed: {ex2.Message}");
                }
            }
        }
        base.OnFrameworkInitializationCompleted();
        Log("OnFrameworkInitializationCompleted done");
    }
}
