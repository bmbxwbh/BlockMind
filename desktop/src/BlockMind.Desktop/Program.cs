using Avalonia;
using System;
using System.IO;
using System.Reflection;

namespace BlockMind.Desktop;

class Program
{
    [STAThread]
    public static void Main(string[] args)
    {
        var logFile = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "blockmind-debug.log");
        try
        {
            File.AppendAllText(logFile, $"[{DateTime.Now}] BlockMind starting...\n");
            File.AppendAllText(logFile, $"[{DateTime.Now}] Base dir: {AppDomain.CurrentDomain.BaseDirectory}\n");
            File.AppendAllText(logFile, $"[{DateTime Now}] Args: {string.Join(" ", args)}\n");
            File.AppendAllText(logFile, $"[{DateTime.Now}] OS: {Environment.OSVersion}\n");
            File.AppendAllText(logFile, $"[{DateTime.Now}] .NET: {Environment.Version}\n");

            var assemblies = Directory.GetFiles(AppDomain.CurrentDomain.BaseDirectory, "*.dll");
            File.AppendAllText(logFile, $"[{DateTime.Now}] DLLs: {assemblies.Length}\n");

            foreach (var dll in assemblies)
            {
                if (Path.GetFileName(dll).StartsWith("Avalonia"))
                    File.AppendAllText(logFile, $"[{DateTime.Now}]   Avalonia: {Path.GetFileName(dll)}\n");
            }

            File.AppendAllText(logFile, $"[{DateTime.Now}] Building Avalonia app...\n");
            var app = BuildAvaloniaApp();
            File.AppendAllText(logFile, $"[{DateTime.Now}] Avalonia app built, starting lifetime...\n");
            app.StartWithClassicDesktopLifetime(args);
        }
        catch (Exception ex)
        {
            File.AppendAllText(logFile, $"[{DateTime.Now}] FATAL: {ex.GetType().Name}: {ex.Message}\n");
            File.AppendAllText(logFile, $"[{DateTime.Now}] Stack: {ex.StackTrace}\n");
            if (ex.InnerException != null)
                File.AppendAllText(logFile, $"[{DateTime.Now}] Inner: {ex.InnerException.Message}\n");

            Console.Error.WriteLine($"[BlockMind] Fatal error: {ex.Message}");
            Console.Error.WriteLine($"[BlockMind] See log: {logFile}");
            Console.Error.WriteLine("Press any key to exit...");
            try { Console.ReadKey(); } catch { }
        }
    }

    public static AppBuilder BuildAvaloniaApp()
        => AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .LogToTrace();
}
