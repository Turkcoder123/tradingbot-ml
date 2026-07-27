# --- Step 4: Feature Engineering with Technical Indicators & Multi-Timeframe Features ---

def create_technical_features(df):
    """Creates comprehensive technical indicators and time features."""
    df_feat = df.copy()
    
    # --- Time-based features (scaled to [-0.5, 0.5]) ---
    df_feat['hour'] = df_feat.index.hour / 23.0 - 0.5
    df_feat['day_of_week'] = df_feat.index.dayofweek / 6.0 - 0.5
    df_feat['day_of_month'] = (df_feat.index.day - 1) / 30.0 - 0.5
    df_feat['month'] = (df_feat.index.month - 1) / 11.0 - 0.5
    
    # --- Price-based features (5m) ---
    df_feat['returns_5m'] = df_feat['Close'].pct_change()
    df_feat['log_returns_5m'] = np.log(df_feat['Close'] / df_feat['Close'].shift(1))
    
    # OHLC relationships
    df_feat['hl_ratio'] = (df_feat['High'] - df_feat['Low']) / df_feat['Close']  # Normalized range
    df_feat['oc_ratio'] = (df_feat['Close'] - df_feat['Open']) / df_feat['Close']  # Body ratio
    df_feat['upper_shadow'] = (df_feat['High'] - df_feat[['Open', 'Close']].max(axis=1)) / df_feat['Close']
    df_feat['lower_shadow'] = (df_feat[['Open', 'Close']].min(axis=1) - df_feat['Low']) / df_feat['Close']
    
    # --- Moving Averages (5m) ---
    for window in [5, 10, 20, 50]:
        df_feat[f'sma_{window}'] = df_feat['Close'].rolling(window=window).mean()
        df_feat[f'sma_{window}_ratio'] = df_feat['Close'] / df_feat[f'sma_{window}'] - 1
    
    # --- Momentum Indicators ---
    # RSI (14 period)
    delta = df_feat['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df_feat['rsi_14'] = 100 - (100 / (1 + rs))
    df_feat['rsi_14_norm'] = df_feat['rsi_14'] / 100.0 - 0.5  # Normalize to [-0.5, 0.5]
    
    # MACD
    exp1 = df_feat['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df_feat['Close'].ewm(span=26, adjust=False).mean()
    df_feat['macd'] = exp1 - exp2
    df_feat['macd_signal'] = df_feat['macd'].ewm(span=9, adjust=False).mean()
    df_feat['macd_hist'] = df_feat['macd'] - df_feat['macd_signal']
    df_feat['macd_norm'] = df_feat['macd'] / df_feat['Close']  # Normalize
    
    # --- Volatility Indicators ---
    df_feat['volatility_20'] = df_feat['log_returns_5m'].rolling(window=20).std()
    df_feat['volatility_50'] = df_feat['log_returns_5m'].rolling(window=50).std()
    
    # ATR (Average True Range)
    high_low = df_feat['High'] - df_feat['Low']
    high_close_prev = (df_feat['High'] - df_feat['Close'].shift(1)).abs()
    low_close_prev = (df_feat['Low'] - df_feat['Close'].shift(1)).abs()
    tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    df_feat['atr_14'] = tr.rolling(window=14).mean()
    df_feat['atr_14_norm'] = df_feat['atr_14'] / df_feat['Close']  # Normalize
    
    # --- Volume Features ---
    df_feat['volume_sma_20'] = df_feat['Volume'].rolling(window=20).mean()
    df_feat['volume_ratio'] = df_feat['Volume'] / df_feat['volume_sma_20']
    
    # --- Multi-Timeframe Features ---
    # Relative position within higher timeframe ranges
    df_feat['price_vs_1h_range'] = (df_feat['Close'] - df_feat['Low_1h']) / (df_feat['High_1h'] - df_feat['Low_1h'] + 1e-8) - 0.5
    df_feat['price_vs_1d_range'] = (df_feat['Close'] - df_feat['Low_1d']) / (df_feat['High_1d'] - df_feat['Low_1d'] + 1e-8) - 0.5
    
    # Higher timeframe returns
    df_feat['return_1h'] = df_feat['Close_1h'].pct_change()
    df_feat['return_1d'] = df_feat['Close_1d'].pct_change()
    
    # Volume ratios across timeframes
    df_feat['volume_5m_vs_1h'] = df_feat['Volume'] / (df_feat['Volume_1h'] / 12 + 1e-8) - 1
    df_feat['volume_5m_vs_1d'] = df_feat['Volume'] / (df_feat['Volume_1d'] / 288 + 1e-8) - 1
    
    # Range expansion/contraction
    df_feat['range_ratio_5m_vs_1h'] = df_feat['Range_5m'] / (df_feat['Range_1h'] / 12 + 1e-8) - 1
    df_feat['range_ratio_5m_vs_1d'] = df_feat['Range_5m'] / (df_feat['Range_1d'] / 288 + 1e-8) - 1
    
    return df_feat

# --- Feature and Target Column Definitions ---
FEATURE_COLUMNS = [
    'hour', 'day_of_week', 'day_of_month', 'month',
    'Open', 'High', 'Low', 'Close', 'Volume',
    'Range_5m', 'Range_1h', 'Range_1d',
    'returns_5m', 'log_returns_5m',
    'hl_ratio', 'oc_ratio', 'upper_shadow', 'lower_shadow',
    'sma_5_ratio', 'sma_10_ratio', 'sma_20_ratio', 'sma_50_ratio',
    'rsi_14_norm', 'macd_norm', 'macd_hist',
    'volatility_20', 'volatility_50', 'atr_14_norm',
    'volume_ratio',
    'price_vs_1h_range', 'price_vs_1d_range',
    'return_1h', 'return_1d',
    'volume_5m_vs_1h', 'volume_5m_vs_1d',
    'range_ratio_5m_vs_1h', 'range_ratio_5m_vs_1d'
]
TARGET_COLUMNS = ['Open', 'High', 'Low', 'Close']
HISTORY_LENGTH = 295  # 288 (context) + 7 (max lag)
print(f'Features: {len(FEATURE_COLUMNS)}, Targets: {len(TARGET_COLUMNS)} (OHLC)')
print(f'HISTORY_LENGTH: {HISTORY_LENGTH}')

print("Feature engineering function defined.")