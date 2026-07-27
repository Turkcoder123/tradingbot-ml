# --- Step 5: Scale the Data (OHLCV + Features) ---
from sklearn.preprocessing import StandardScaler

# === OHLC Scaler (Close'a fit edilir, OHLC'nin 4 kanalina uygulanir) ===
ohlc_cols = ['Open', 'High', 'Low', 'Close']
scaler_close = StandardScaler()

# Train: fit + transform
train_df[ohlc_cols] = scaler_close.fit_transform(train_df[ohlc_cols])

# Val/Test: sadece transform
val_df[ohlc_cols] = scaler_close.transform(val_df[ohlc_cols])
test_df[ohlc_cols] = scaler_close.transform(test_df[ohlc_cols])

# Print (fit'ten SONRA!)
print(f'Close scaler - mean: {scaler_close.mean_[0]:.6f}, std: {scaler_close.scale_[0]:.6f}')

# === Feature Scaler (Volume, Range gibi ek ozellikler icin) ===
feature_scaler_cols = ['Volume', 'Range_5m', 'Range_1h', 'Range_1d']
available_feature_cols = [c for c in feature_scaler_cols if c in train_df.columns]
if available_feature_cols:
    scaler_features = StandardScaler()
    train_df[available_feature_cols] = scaler_features.fit_transform(train_df[available_feature_cols])
    val_df[available_feature_cols] = scaler_features.transform(val_df[available_feature_cols])
    test_df[available_feature_cols] = scaler_features.transform(test_df[available_feature_cols])
    print(f'Feature scaler - features: {available_feature_cols}')
