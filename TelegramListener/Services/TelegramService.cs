using System;
using System.IO;
using System.Threading.Tasks;
using WTelegram;

namespace TelegramListener.Services;

public interface ITelegramService
{
    Task InitializeAsync(int apiId, string apiHash, string sessionPath);
    Task<bool> ConnectAndAuthorizeAsync();
    Task SendCodeRequestAsync(string phoneNumber);
    Task LoginAsync(string code);
    void StartListening(Func<string, string, DateTime, Task> onMessageReceived);
    Task StopAsync();
}

public class TelegramService : ITelegramService
{
    private Client? _client;
    private int _apiId;
    private string _apiHash = string.Empty;
    private string _sessionPath = string.Empty;
    private bool _isRunning;
    private CancellationTokenSource? _cts;

    public async Task InitializeAsync(int apiId, string apiHash, string sessionPath)
    {
        _apiId = apiId;
        _apiHash = apiHash;
        _sessionPath = sessionPath;

        // WTelegramClient ile client oluştur
        _client = new Client(new WTelegram.Helpers.Config
        {
            api_id = apiId,
            api_hash = apiHash,
        });

        // Session dosyasını yükle
        if (File.Exists(sessionPath))
        {
            await _client.LoadSessionFromFileAsync(sessionPath);
        }
    }

    public async Task<bool> ConnectAndAuthorizeAsync()
    {
        if (_client == null)
            throw new InvalidOperationException("Client not initialized");

        await _client.ConnectAsync();
        return _client.User != null;
    }

    public async Task SendCodeRequestAsync(string phoneNumber)
    {
        if (_client == null)
            throw new InvalidOperationException("Client not initialized");

        await _client.LoginPhoneAsync(phoneNumber);
    }

    public async Task LoginAsync(string code)
    {
        if (_client == null)
            throw new InvalidOperationException("Client not initialized");

        await _client.LoginCodeAsync(code);
        
        // Session'ı kaydet
        if (!string.IsNullOrEmpty(_sessionPath))
        {
            await _client.SaveSessionToFileAsync(_sessionPath);
        }
    }

    public void StartListening(Func<string, string, DateTime, Task> onMessageReceived)
    {
        if (_client == null)
            throw new InvalidOperationException("Client not initialized");

        _isRunning = true;
        _cts = new CancellationTokenSource();

        Task.Run(async () =>
        {
            while (_isRunning && !_cts.Token.IsCancellationRequested)
            {
                try
                {
                    // Yeni mesajları kontrol et
                    var updates = await _client.GetUpdatesAsync();
                    
                    foreach (var update in updates)
                    {
                        if (update is WTelegram.Types.Message msg && !string.IsNullOrEmpty(msg.text))
                        {
                            var senderName = msg.from_id?.ToString() ?? "Unknown";
                            var content = msg.text;
                            var date = msg.date;

                            await onMessageReceived(senderName, content, date);
                        }
                    }
                    
                    await Task.Delay(1000, _cts.Token);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error: {ex.Message}");
                    await Task.Delay(5000);
                }
            }
        }, _cts.Token);
    }

    public async Task StopAsync()
    {
        _isRunning = false;
        
        if (_cts != null)
        {
            await _cts.CancelAsync();
        }
        
        if (_client != null)
        {
            await _client.DisconnectAsync();
        }
    }
}
