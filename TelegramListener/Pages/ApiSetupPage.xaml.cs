using System;
using System.Threading.Tasks;
using TelegramListener.Services;

namespace TelegramListener.Pages;

public partial class ApiSetupPage : ContentPage
{
    private readonly IConfigService _configService;
    private readonly ITelegramService _telegramService;

    public ApiSetupPage(IConfigService configService, ITelegramService telegramService)
    {
        InitializeComponent();
        _configService = configService;
        _telegramService = telegramService;
    }

    private async void OnContinueClicked(object sender, EventArgs e)
    {
        try
        {
            if (!int.TryParse(ApiIdEntry.Text, out int apiId))
            {
                ShowError("API ID geçerli bir sayı olmalıdır.");
                return;
            }

            if (string.IsNullOrWhiteSpace(ApiHashEntry.Text))
            {
                ShowError("API Hash boş olamaz.");
                return;
            }

            var config = await _configService.LoadConfigAsync();
            config.ApiId = apiId;
            config.ApiHash = ApiHashEntry.Text;
            config.SessionPath = _configService.GetSessionPath();
            config.CsvPath = _configService.GetCsvPath();
            
            await _configService.SaveConfigAsync(config);

            // Telegram servisini başlat
            await _telegramService.InitializeAsync(apiId, ApiHashEntry.Text, config.SessionPath);

            // Auth sayfasına geç
            var authPage = new AuthPage(_configService, _telegramService);
            await Navigation.PushAsync(authPage);
        }
        catch (Exception ex)
        {
            ShowError($"Hata: {ex.Message}");
        }
    }

    private void ShowError(string message)
    {
        ErrorMessage.Text = message;
        ErrorMessage.IsVisible = true;
    }
}
