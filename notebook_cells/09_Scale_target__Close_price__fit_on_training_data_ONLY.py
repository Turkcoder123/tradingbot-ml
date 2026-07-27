# --- Step 5: Scale the Data (OHLCV + Features) ---
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Scale target (Close price) - fit on training data ONLY
scaler_close = StandardScaler()

# Scale OHLCV features for model input
feature_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 
                   'Range_5m', 'Range_1h', 'Range_1d']

ohlv_scaler = StandardScaler()
train_df[feature_columns] = ohlv_scaler.fit_transform(train_df[feature_columns])
val_df[feature_columns] = ohlv_scaler.transform(val_df[feature_columns])
test_df[feature_columns] = ohlv_scaler.transform(test_df[feature_columns])

print("Target and OHLCV features scaled successfully.")
print(f"Close scaler mean: {scaler_close.mean_[0]:.6f}, std: {scaler_close.scale_[0]:.6f}")

# --- Scale OHLC ---
ohlc_cols = ['Open', 'High', 'Low', 'Close']
train_df[ohlc_cols] = scaler_close.fit_transform(train_df[ohlc_cols])
val_df[ohlc_cols] = scaler_close.transform(val_df[ohlc_cols])
test_df[ohlc_cols] = scaler_close.transform(test_df[ohlc_cols])
print(f"Close scaler - mean: {scaler_close.mean_[0]:.6f}, std: {scaler_close.scale_[0]:.6f}")
