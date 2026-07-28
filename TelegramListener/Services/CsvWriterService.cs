using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;

namespace TelegramListener.Services;

public interface ICsvWriterService
{
    Task InitializeAsync(string csvPath);
    Task WriteMessageAsync(string sender, string message, DateTime timestamp);
}

public class CsvWriterService : ICsvWriterService
{
    private string _csvPath = string.Empty;
    private readonly SemaphoreSlim _semaphore = new(1, 1);

    public async Task InitializeAsync(string csvPath)
    {
        _csvPath = csvPath;

        if (!File.Exists(_csvPath))
        {
            var header = "Timestamp,Sender,Message\n";
            await File.WriteAllTextAsync(_csvPath, header, Encoding.UTF8);
        }
    }

    public async Task WriteMessageAsync(string sender, string message, DateTime timestamp)
    {
        await _semaphore.WaitAsync();
        try
        {
            var escapedMessage = message.Replace("\"", "\"\"");
            var line = $"\"{timestamp:yyyy-MM-dd HH:mm:ss}\",\"{sender}\",\"{escapedMessage}\"\n";
            
            await File.AppendAllTextAsync(_csvPath, line, Encoding.UTF8);
        }
        finally
        {
            _semaphore.Release();
        }
    }
}
