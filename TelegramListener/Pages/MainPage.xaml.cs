using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using TelegramListener.Services;

namespace TelegramListener.Pages;

public partial class MainPage : ContentPage
{
    private readonly IConfigService _configService;
    private readonly ITelegramService _telegramService;
    private readonly ICsvWriterService _csvWriterService;
    private bool _isListening;
    private ObservableCollection<MessageItem> _messages = new();

    public MainPage(IConfigService configService, ITelegramService telegramService)
    {
        InitializeComponent();
        _configService = configService;
        _telegramService = telegramService;
        _csvWriterService = new CsvWriterService();
        
        MessagesCollection.ItemsSource = _messages;
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        
        var config = await _configService.LoadConfigAsync();
        await _csvWriterService.InitializeAsync(config.CsvPath);
    }

    private async void OnStartStopClicked(object sender, EventArgs e)
    {
        try
        {
            if (!_isListening)
            {
                // Dinlemeyi başlat
                var config = await _configService.LoadConfigAsync();
                
                await _telegramService.InitializeAsync(
                    config.ApiId, 
                    config.ApiHash, 
                    config.SessionPath
                );

                _telegramService.StartListening(OnMessageReceived);

                StatusText.Text = "Durum: Dinleniyor";
                StartStopButton.Text = "Dinlemeyi Durdur";
                _isListening = true;
            }
            else
            {
                // Dinlemeyi durdur
                await _telegramService.StopAsync();

                StatusText.Text = "Durum: Durduruldu";
                StartStopButton.Text = "Dinlemeyi Başlat";
                _isListening = false;
            }
        }
        catch (Exception ex)
        {
            await DisplayAlert("Hata", $"İşlem başarısız: {ex.Message}", "Tamam");
        }
    }

    private async Task OnMessageReceived(string sender, string message, DateTime timestamp)
    {
        // UI thread'de güncelleme yap
        MainThread.BeginInvokeOnMainThread(() =>
        {
            _messages.Insert(0, new MessageItem
            {
                Sender = sender,
                Content = message,
                Timestamp = timestamp
            });

            LastMessageText.Text = $"Son mesaj: {message.Substring(0, Math.Min(50, message.Length))}...";
        });

        // CSV'ye yaz
        await _csvWriterService.WriteMessageAsync(sender, message, timestamp);
    }

    private void OnMinimizeToTrayClicked(object sender, EventArgs e)
    {
        // Windows'ta sistem tepsisine küçültme işlemi
        // Bu özellik MAUI'de platform-specific kod gerektirir
        Application.Current?.Quit();
    }
}

public class MessageItem
{
    public string Sender { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; }
}
