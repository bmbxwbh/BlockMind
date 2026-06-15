using System.Net.Http.Json;
using System.Text.Json;

namespace BlockMind.Core.Api;

public class ModApiClient
{
    private readonly HttpClient _http;
    private readonly string _baseUrl;
    private readonly JsonSerializerOptions _json = new() { PropertyNameCaseInsensitive = true };

    public ModApiClient(string host = "localhost", int port = 25580)
    {
        _baseUrl = $"http://{host}:{port}";
        _http = new HttpClient { Timeout = TimeSpan.FromSeconds(10) };
    }

    public async Task<bool> IsConnectedAsync()
    {
        try { var r = await _http.GetAsync($"{_baseUrl}/health"); return r.IsSuccessStatusCode; }
        catch { return false; }
    }

    public async Task<JsonElement?> GetStatusAsync() => await GetJsonAsync("/api/status");
    public async Task<JsonElement?> GetInventoryAsync() => await GetJsonAsync("/api/inventory");
    public async Task<JsonElement?> GetEntitiesAsync(int radius = 32) => await GetJsonAsync($"/api/entities?radius={radius}");
    public async Task<JsonElement?> GetBlocksAsync(int radius = 16, string type = "any") => await GetJsonAsync($"/api/blocks?radius={radius}&type={type}");

    public async Task<JsonElement?> MoveAsync(double x, double y, double z, bool sprint = false)
        => await PostJsonAsync("/api/move", new { x, y, z, sprint });
    public async Task<JsonElement?> DigAsync(int x, int y, int z)
        => await PostJsonAsync("/api/dig", new { x, y, z });
    public async Task<JsonElement?> PlaceAsync(string item, int x, int y, int z)
        => await PostJsonAsync("/api/place", new { item, x, y, z });
    public async Task<JsonElement?> AttackAsync(int entityId)
        => await PostJsonAsync("/api/attack", new { entity_id = entityId });
    public async Task<JsonElement?> EatAsync(string item)
        => await PostJsonAsync("/api/eat", new { item });
    public async Task<JsonElement?> ChatAsync(string message)
        => await PostJsonAsync("/api/chat", new { message });

    public async Task<JsonElement?> SpawnBotAsync(string name)
        => await PostJsonAsync("/api/bot/spawn", new { name });
    public async Task<JsonElement?> DespawnBotAsync()
        => await PostJsonAsync("/api/bot/despawn", new { });

    private async Task<JsonElement?> GetJsonAsync(string path)
    {
        try { var r = await _http.GetAsync($"{_baseUrl}{path}"); return r.IsSuccessStatusCode ? await r.Content.ReadFromJsonAsync<JsonElement>() : null; }
        catch { return null; }
    }

    private async Task<JsonElement?> PostJsonAsync(string path, object body)
    {
        try { var r = await _http.PostAsJsonAsync($"{_baseUrl}{path}", body); return r.IsSuccessStatusCode ? await r.Content.ReadFromJsonAsync<JsonElement>() : null; }
        catch { return null; }
    }
}
