using Avalonia;
using Avalonia.Controls;
using Avalonia.Platform;
using System.Runtime.InteropServices;

namespace BlockMind.Desktop.Services;

public class TrayService : IDisposable
{
    private readonly Window _window;
    private bool _disposed;

    public TrayService(Window window)
    {
        _window = window;
    }

    public void MinimizeToTray()
    {
        _window.Hide();
    }

    public void RestoreFromTray()
    {
        _window.Show();
        _window.WindowState = WindowState.Normal;
        _window.Activate();
    }

    public void ToggleVisibility()
    {
        if (_window.IsVisible) MinimizeToTray();
        else RestoreFromTray();
    }

    public void Dispose()
    {
        _disposed = true;
    }
}
