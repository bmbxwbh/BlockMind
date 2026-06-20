using System.Net.Http.Json;
using System.Text.Json;

namespace BlockMind.Core.Api;

public enum AiFormat { OpenAI, Anthropic }

public class AiApiClient
{
    private readonly HttpClient _http = new() { Timeout = TimeSpan.FromSeconds(60) };

    public async Task<string?> ChatAsync(List<Dictionary<string, string>> messages, AiFormat format, string baseUrl, string apiKey, string model, float temperature = 0.7f, int maxTokens = 2000)
    {
        try
        {
            return format == AiFormat.Anthropic
                ? await CallAnthropicAsync(messages, baseUrl, apiKey, model, temperature, maxTokens)
                : await CallOpenAIAsync(messages, baseUrl, apiKey, model, temperature, maxTokens);
        }
        catch { return null; }
    }

    public async Task<bool> TestConnectionAsync(AiFormat format, string baseUrl, string apiKey, string model)
    {
        try
        {
            var messages = new List<Dictionary<string, string>>
            {
                new() { { "role", "user" }, { "content", "Hello" } }
            };
            var result = await ChatAsync(messages, format, baseUrl, apiKey, model, 0.1f, 10);
            return result != null;
        }
        catch { return false; }
    }

    private async Task<string?> CallOpenAIAsync(List<Dictionary<string, string>> messages, string baseUrl, string apiKey, string model, float temperature, int maxTokens)
    {
        var request = new
        {
            model,
            messages = messages,
            temperature,
            max_tokens = maxTokens
        };
        var req = new HttpRequestMessage(HttpMethod.Post, $"{baseUrl}/chat/completions")
        {
            Content = JsonContent.Create(request)
        };
        req.Headers.Add("Authorization", $"Bearer {apiKey}");

        var r = await _http.SendAsync(req);
        if (!r.IsSuccessStatusCode) return null;

        var json = await r.Content.ReadFromJsonAsync<JsonElement>();
        return json.GetProperty("choices")[0].GetProperty("message").GetProperty("content").GetString();
    }

    private async Task<string?> CallAnthropicAsync(List<Dictionary<string, string>> messages, string baseUrl, string apiKey, string model, float temperature, int maxTokens)
    {
        var systemMsg = messages.FirstOrDefault(m => m["role"] == "system")?["content"] ?? "";
        var userMessages = messages.Where(m => m["role"] != "system").Select(m => new { role = m["role"], content = m["content"] }).ToList();

        var request = new
        {
            model,
            max_tokens = maxTokens,
            temperature,
            system = systemMsg,
            messages = userMessages
        };
        var req = new HttpRequestMessage(HttpMethod.Post, $"{baseUrl}/messages")
        {
            Content = JsonContent.Create(request)
        };
        req.Headers.Add("x-api-key", apiKey);
        req.Headers.Add("anthropic-version", "2023-06-01");

        var r = await _http.SendAsync(req);
        if (!r.IsSuccessStatusCode) return null;

        var json = await r.Content.ReadFromJsonAsync<JsonElement>();
        return json.GetProperty("content")[0].GetProperty("text").GetString();
    }
}
