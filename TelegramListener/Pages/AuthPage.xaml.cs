using System;
using System.Threading.Tasks;
using TelegramListener.Services;

namespace TelegramListener.Pages;

public partial class AuthPage : ContentPage
{
    private readonly IConfigService _configService;
    private readonly ITelegramService _telegramService;
    private string _phoneNumber = string.Empty;

    public AuthPage(IConfigService configService, ITelegramService telegramService)
    {
        InitializeComponent();
        _configService = configService;
        _telegramService = telegramService;
    }

    private async void OnSendCodeClicked(object sender, EventArgs e)
    {
        try
        {
            _phoneNumber = PhoneEntry.Text.Trim();
            
            if (string.IsNullOrWhiteSpace(_phoneNumber))
            {
                ShowError("Telefon numarası boş olamaz.");
                return;
            }

            LoadingIndicator.IsRunning = true;
            LoadingIndicator.IsVisible = true;
            ErrorMessage.IsVisible = false;

            // Kod gönderme işlemi
            await _telegramService.SendCodeRequestAsync(_phoneNumber);
            
            LoadingIndicator.IsRunning = false;
            LoadingIndicator.IsVisible = false;
            CodeFrame.IsVisible = true;
        }
        catch (Exception ex)
        {
            LoadingIndicator.IsRunning = false;
            LoadingIndicator.IsVisible = false;
            ShowError($"Hata: {ex.Message}");
        }
    }

    private async void OnLoginClicked(object sender, EventArgs e)
    {
        try
        {
            var code = CodeEntry.Text.Trim();
            
            if (string.IsNullOrWhiteSpace(code))
            {
                ShowError("Kod boş olamaz.");
                return;
            }

            LoadingIndicator.IsRunning = true;
            LoadingIndicator.IsVisible = true;
            ErrorMessage.IsVisible = false;

            // Giriş yapma işlemi
            await _telegramService.LoginAsync(code);
            
            LoadingIndicator.IsRunning = false;
            LoadingIndicator.IsVisible = false;

            // Başarılı giriş sonrası ana sayfaya yönlendir
            await Navigation.PushAsync(new MainPage(_configService, _telegramService));
        }
        catch (Exception ex)
        {
            LoadingIndicator.IsRunning = false;
            LoadingIndicator.IsVisible = false;
            ShowError($"Hata: {ex.Message}");
        }
    }

    private void ShowError(string message)
    {
        ErrorMessage.Text = message;
        ErrorMessage.IsVisible = true;
    }
}
