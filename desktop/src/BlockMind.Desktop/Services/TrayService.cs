using Avalonia.Controls;

namespace BlockMind.Desktop.Services;

public class TrayService
{
    private readonly Window _window;

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
}
