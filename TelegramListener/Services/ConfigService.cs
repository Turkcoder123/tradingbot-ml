using System;
using System.IO;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace TelegramListener.Services;

public class Config
{
    public int ApiId { get; set; }
    public string ApiHash { get; set; } = string.Empty;
    public string SessionPath { get; set; } = string.Empty;
    public string CsvPath { get; set; } = string.Empty;
    public string[] ChannelsToMonitor { get; set; } = Array.Empty<string>();
}

public interface IConfigService
{
    Task<Config> LoadConfigAsync();
    Task SaveConfigAsync(Config config);
    string GetSessionPath();
    string GetCsvPath();
    bool IsSessionExists();
}

public class ConfigService : IConfigService
{
    private readonly string _configPath;
    private readonly string _appDataPath;

    public ConfigService()
    {
        _appDataPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "TelegramListener"
        );

        if (!Directory.Exists(_appDataPath))
        {
            Directory.CreateDirectory(_appDataPath);
        }

        _configPath = Path.Combine(_appDataPath, "config.json");
    }

    public async Task<Config> LoadConfigAsync()
    {
        if (File.Exists(_configPath))
        {
            var json = await File.ReadAllTextAsync(_configPath);
            return JsonConvert.DeserializeObject<Config>(json) ?? new Config();
        }

        return new Config();
    }

    public async Task SaveConfigAsync(Config config)
    {
        var json = JsonConvert.SerializeObject(config, Formatting.Indented);
        await File.WriteAllTextAsync(_configPath, json);
    }

    public string GetSessionPath()
    {
        return Path.Combine(_appDataPath, "session.session");
    }

    public string GetCsvPath()
    {
        return Path.Combine(_appDataPath, "messages.csv");
    }

    public bool IsSessionExists()
    {
        return File.Exists(GetSessionPath());
    }
}
