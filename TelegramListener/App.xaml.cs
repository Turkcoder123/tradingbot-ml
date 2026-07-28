using TelegramListener.Services;
using TelegramListener.Pages;

namespace TelegramListener;

public partial class App : Application
{
    private readonly IConfigService _configService;
    private readonly ITelegramService _telegramService;

    public App()
    {
        InitializeComponent();

        _configService = new ConfigService();
        _telegramService = new TelegramService();

        MainPage = new NavigationPage(new StartupPage(_configService, _telegramService));
    }
}
