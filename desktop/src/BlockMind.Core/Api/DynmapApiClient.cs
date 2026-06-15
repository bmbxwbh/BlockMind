using System.Net.Http.Json;
using System.Text.Json;

namespace BlockMind.Core.Api;

public class DynmapApiClient
{
    private readonly HttpClient _http;
    private readonly string _baseUrl;

    public DynmapApiClient(string host = "localhost", int port = 8163)
    {
        _baseUrl = $"http://{host}:{port}";
        _http = new HttpClient { Timeout = TimeSpan.FromSeconds(10) };
    }

    public async Task<bool> IsConnectedAsync()
    {
        try { var r = await _http.GetAsync($"{_baseUrl}/up/"); return r.IsSuccessStatusCode; }
        catch { return false; }
    }

    public async Task<JsonElement?> GetMarkersAsync(string world = "world")
        => await GetJsonAsync($"/markers/{world}");

    public async Task<JsonElement?> GetPlayersAsync()
        => await GetJsonAsync("/api/players");

    private async Task<JsonElement?> GetJsonAsync(string path)
    {
        try { var r = await _http.GetAsync($"{_baseUrl}{path}"); return r.IsSuccessStatusCode ? await r.Content.ReadFromJsonAsync<JsonElement>() : null; }
        catch { return null; }
    }
}
