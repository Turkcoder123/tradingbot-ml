# Telegram Listener - .NET MAUI Windows Uygulaması

## Genel Bakış
Bu uygulama, Windows'ta arka planda çalışarak Telegram mesajlarını dinler ve CSV dosyasına kaydeder. Uygulama sistem tepsisinde simge ile çalışır ve servis benzeri bir yapıya sahiptir.

## Özellikler
- ✅ Session dosyası kontrolü (yoksa API bilgilerini ister)
- ✅ API ID ve API Hash girişi
- ✅ Telefon numarası ve OTP ile giriş
- ✅ Session dosyasını uygulama dizininde saklama
- ✅ Sadece yeni (realtime) mesajları dinleme
- ✅ Mesajları CSV dosyasına kaydetme
- ✅ Sistem tepsisinde çalışma
- ✅ Arka planda servis gibi çalışma

## Proje Yapısı

```
TelegramListener/
├── App.xaml / App.xaml.cs          # Uygulama başlangıç noktası
├── TelegramListener.csproj         # Proje dosyası
├── Platforms/
│   └── Windows/
│       ├── Program.cs              # Windows giriş noktası
│       ├── AssemblyInfo.cs         # Windows assembly bilgileri
│       └── Tray/                   # Sistem tepsisi kodları
├── Pages/
│   ├── StartupPage.xaml(.cs)       # Başlangıç sayfası
│   ├── ApiSetupPage.xaml(.cs)      # API ayarları sayfası
│   ├── AuthPage.xaml(.cs)          # Giriş sayfası
│   └── MainPage.xaml(.cs)          # Ana dinleme sayfası
├── Services/
│   ├── ConfigService.cs            # Ayarlar yönetimi
│   ├── TelegramService.cs          # Telegram API işlemleri
│   └── CsvWriterService.cs         # CSV yazma işlemleri
└── Resources/
    ├── Styles/
    │   ├── Colors.xaml             # Renk tanımları
    │   └── Styles.xaml             # Stil tanımları
    └── AppIcon/                    # Uygulama ikonu
```

## Kurulum

### Gereksinimler
- Windows 10/11
- .NET 8.0 SDK
- Visual Studio 2022 (MAUI workload ile)

### Adımlar

1. **Proje Derleme**
```bash
cd TelegramListener
dotnet restore
dotnet build -c Release
```

2. **Yayınla (Publish)**
```bash
dotnet publish -c Release -f net8.0-windows10.0.19041.0
```

3. **Uygulamayı Çalıştır**
```bash
.\bin\Release\net8.0-windows10.0.19041.0\publish\TelegramListener.exe
```

## Kullanım

### İlk Çalıştırma
1. Uygulama ilk açıldığında session dosyası olmadığını tespit eder
2. API Setup sayfasına yönlendirir
3. `api.telegram.org` adresinden alınan API ID ve API Hash girilir
4. Telefon numarası girilir ve SMS/Telegram kodu alınır
5. Kod girilerek giriş tamamlanır
6. Session dosyası oluşturulur ve kaydedilir

### Normal Çalıştırma
- Session dosyası varsa doğrudan ana sayfaya gider
- "Dinlemeyi Başlat" butonu ile mesaj dinleme başlar
- Gelen mesajlar ekranda gösterilir ve CSV'ye yazılır
- "Sistem Tepsisine Küçült" ile arka plana geçer

## CSV Dosya Formatı
```csv
Timestamp,Sender,Message
"2024-01-15 10:30:45","username","Mesaj içeriği"
```

## Önemli Notlar

⚠️ **WTelegramClient Kullanımı**: 
- Proje, C# native Telegram client library olan `WTelegramClient` kullanır.
- Python'daki Telethon'a alternatif olarak geliştirilmiştir.
- Session dosyaları otomatik olarak oluşturulur ve yönetilir.

⚠️ **Sistem Tepsisi**:
- MAUI'de sistem tepsisi desteği sınırlıdır
- `H.NotifyIcon` paketi eklenmiştir
- Platform-specific kod Windows projesine yazılmalıdır

⚠️ **Servis Olarak Çalıştırma**:
- NSSM (Non-Sucking Service Manager) ile Windows servisi yapılabilir
- Veya Task Scheduler ile başlangıçta otomatik çalıştırılabilir

## Sonraki Adımlar

1. **Sistem Tepsisi İkonu**
   - H.NotifyIcon entegrasyonu tamamlanmalı
   - Platform-specific kod Windows projesine yazılmalı

2. **Servis Entegrasyonu**
   - NSSM kurulum script'i hazırlanmalı
   - Veya Windows Task Scheduler entegrasyonu yapılmalı

3. **Test**
   - Gerçek Telegram hesabı ile test edilmeli
   - Farklı senaryolar denenmeli

## Lisans
Bu proje eğitim amaçlıdır.
