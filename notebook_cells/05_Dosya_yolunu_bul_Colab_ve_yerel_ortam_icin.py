# --- Step 3: Load and Preprocess Data (OHLCV + Multi-Timeframe) ---
import os
# Dosya yolunu bul - Colab ve yerel ortam icin
file_path = 'Data/EURUSD_5m_10Yea.csv'
if not os.path.exists(file_path):
    # Colab'da farkli yollarda ara
    for p in [
        '/content/tradingbot-ml/Data/EURUSD_5m_10Yea.csv',
        '../Data/EURUSD_5m_10Yea.csv',
    ]:
        if os.path.exists(p):
            file_path = p
            break
print(f'Veri: {file_path}')
df_raw = pd.read_csv(file_path)

# Parse timestamp
df_raw['Timestamp'] = pd.to_datetime(
    df_raw['Date'].astype(str) + ' ' + df_raw['Time'].astype(str),
    format='%Y%m%d %H:%M:%S'
)

# Keep all OHLCV columns
df_5m = df_raw[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
df_5m.set_index('Timestamp', inplace=True)

# --- Create Higher Timeframes from 5m data ---
# 1 Hour (12 x 5min bars)
df_1h = df_5m.resample('1H').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}).dropna()

# 1 Day (288 x 5min bars)
df_1d = df_5m.resample('1D').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}).dropna()

print(f"5m data: {len(df_5m)} rows")
print(f"1h data: {len(df_1h)} rows")
print(f"1d data: {len(df_1d)} rows")

# Merge higher timeframe data into 5m for feature enrichment
df = df_5m.copy()
df['Close_1h'] = df['Close'].resample('1H').last().reindex(df.index, method='ffill')
df['Close_1d'] = df['Close'].resample('1D').last().reindex(df.index, method='ffill')
df['Volume_1h'] = df['Volume'].resample('1H').sum().reindex(df.index, method='ffill')
df['Volume_1d'] = df['Volume'].resample('1D').sum().reindex(df.index, method='ffill')
df['High_1h'] = df['High'].resample('1H').max().reindex(df.index, method='ffill')
df['Low_1h'] = df['Low'].resample('1H').min().reindex(df.index, method='ffill')
df['High_1d'] = df['High'].resample('1D').max().reindex(df.index, method='ffill')
df['Low_1d'] = df['Low'].resample('1D').min().reindex(df.index, method='ffill')

# Price range features (intrinsic volatility)
df['Range_5m'] = df['High'] - df['Low']
df['Range_1h'] = df['High_1h'] - df['Low_1h']
df['Range_1d'] = df['High_1d'] - df['Low_1d']

# Chronological split
train_size = int(len(df) * 0.60)
val_size = int(len(df) * 0.20)

train_df = df.iloc[:train_size].copy()
val_df = df.iloc[train_size:train_size + val_size].copy()
test_df = df.iloc[train_size + val_size:].copy()

print(f"\nTraining set size: {len(train_df)}")
print(f"Validation set size: {len(val_df)}")
print(f"Test set size: {len(test_df)}")