using System.Diagnostics;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;

namespace BlockMind.Core.Api;

public class PythonBridge : IDisposable
{
    private Process? _process;
    private readonly HttpClient _http = new() { Timeout = TimeSpan.FromSeconds(5) };
    private readonly string _pythonPath;
    private readonly string _workingDir;
    private readonly int _port;
    private bool _running;

    public bool IsRunning => _running;
    public string BaseUrl => $"http://localhost:{_port}";

    public PythonBridge(string pythonPath = "python", string workingDir = ".", int port = 19951)
    {
        _pythonPath = pythonPath;
        _workingDir = workingDir;
        _port = port;
    }

    public async Task<bool> StartAsync()
    {
        try
        {
            _process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = _pythonPath,
                    Arguments = "-m src.main",
                    WorkingDirectory = _workingDir,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                }
            };
            _process.Start();
            _running = true;

            // Wait for startup
            for (int i = 0; i < 20; i++)
            {
                await Task.Delay(500);
                if (await IsHealthyAsync()) return true;
            }
            return false;
        }
        catch { return false; }
    }

    public async Task StopAsync()
    {
        if (_process != null && !_process.HasExited)
        {
            _process.Kill();
            _process.Dispose();
        }
        _running = false;
    }

    public async Task<bool> IsHealthyAsync()
    {
        try { var r = await _http.GetAsync($"{BaseUrl}/api/system/health"); return r.IsSuccessStatusCode; }
        catch { return false; }
    }

    public async Task<JsonElement?> GetAsync(string path)
    {
        try { return await _http.GetFromJsonAsync<JsonElement>($"{BaseUrl}{path}"); }
        catch { return null; }
    }

    public async Task<JsonElement?> PostAsync(string path, object body)
    {
        try
        {
            var r = await _http.PostAsJsonAsync($"{BaseUrl}{path}", body);
            if (r.IsSuccessStatusCode)
                return await r.Content.ReadFromJsonAsync<JsonElement>();
            return null;
        }
        catch { return null; }
    }

    public void Dispose() { _process?.Dispose(); _http.Dispose(); }
}
