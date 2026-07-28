using System;
using System.Threading.Tasks;
using TelegramListener.Services;

namespace TelegramListener.Pages;

public partial class StartupPage : ContentPage
{
    private readonly IConfigService _configService;
    private readonly ITelegramService _telegramService;

    public StartupPage(IConfigService configService, ITelegramService telegramService)
    {
        InitializeComponent();
        _configService = configService;
        _telegramService = telegramService;
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        await InitializeAppAsync();
    }

    private async Task InitializeAppAsync()
    {
        try
        {
            StatusMessage.Text = "Ayarlar kontrol ediliyor...";
            await Task.Delay(500);

            var config = await _configService.LoadConfigAsync();

            // API bilgileri var mı kontrol et
            if (config.ApiId == 0 || string.IsNullOrWhiteSpace(config.ApiHash))
            {
                StatusMessage.Text = "API ayarları bulunamadı.";
                await NavigateToApiSetup();
                return;
            }

            StatusMessage.Text = "Oturum kontrol ediliyor...";
            await Task.Delay(500);

            // Session dosyası var mı kontrol et
            if (!_configService.IsSessionExists())
            {
                StatusMessage.Text = "Oturum bulunamadı, giriş yapılıyor...";
                await NavigateToApiSetup();
                return;
            }

            StatusMessage.Text = "Uygulama başlatılıyor...";
            await Task.Delay(500);

            // Ana sayfaya geç
            await NavigateToMain();
        }
        catch (Exception ex)
        {
            StatusMessage.Text = $"Hata: {ex.Message}";
            await DisplayAlert("Hata", $"Uygulama başlatılamadı: {ex.Message}", "Tamam");
        }
    }

    private async Task NavigateToApiSetup()
    {
        await Navigation.PushAsync(new ApiSetupPage(_configService, _telegramService));
    }

    private async Task NavigateToMain()
    {
        await Navigation.PushAsync(new MainPage(_configService, _telegramService));
    }
}
