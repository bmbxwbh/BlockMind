namespace BlockMind.Core.Config;

public class AppConfig
{
    public GameConfig Game { get; set; } = new();
    public AiConfig Ai { get; set; } = new();
    public WebUIConfig WebUI { get; set; } = new();
    public DynmapConfig Dynmap { get; set; } = new();
    public MemoryConfig Memory { get; set; } = new();
    public SkillsConfig Skills { get; set; } = new();
}

public class GameConfig
{
    public string ServerIp { get; set; } = "localhost";
    public int ServerPort { get; set; } = 25580;
    public string Username { get; set; } = "BlockMind";
    public string Version { get; set; } = "1.20.4";
    public string ApiToken { get; set; } = "";
}

public class AiConfig
{
    public AiAgentConfig MainAgent { get; set; } = new();
    public AiAgentConfig OperationAgent { get; set; } = new();
}

public class AiAgentConfig
{
    public string Format { get; set; } = "openai"; // openai | anthropic
    public string Provider { get; set; } = "openai";
    public string ApiKey { get; set; } = "";
    public string Model { get; set; } = "gpt-4o";
    public string BaseUrl { get; set; } = "https://api.openai.com/v1";
    public float Temperature { get; set; } = 0.7f;
    public int MaxTokens { get; set; } = 2000;
}

public class WebUIConfig
{
    public bool Enabled { get; set; } = true;
    public int Port { get; set; } = 19951;
    public string Password { get; set; } = "";
}

public class DynmapConfig
{
    public bool Enabled { get; set; } = false;
    public string Host { get; set; } = "localhost";
    public int Port { get; set; } = 8163;
    public string ApiKey { get; set; } = "";
}

public class MemoryConfig
{
    public bool Enabled { get; set; } = true;
    public string StoragePath { get; set; } = "data/memory";
}

public class SkillsConfig
{
    public string StoragePath { get; set; } = "./skills";
}
