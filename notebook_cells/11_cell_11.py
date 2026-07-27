# --- Step 6: Dataset ---
class TimeSeriesDataset(Dataset):
    def __init__(self, df, history_length, prediction_length, feature_columns, target_columns):
        self.history_length = history_length
        self.prediction_length = prediction_length
        self.feature_columns = feature_columns
        self.target_columns = target_columns
        self.close_idx = df.columns.get_loc('Close')
        self.target_indices = [df.columns.get_loc(c) for c in target_columns]
        data = torch.from_numpy(df.values).float()
        self.data = torch.nan_to_num(data, nan=0.0)
    def __len__(self):
        return len(self.data) - self.history_length - self.prediction_length + 1
    def __getitem__(self, idx):
        he = idx + self.history_length
        pe = he + self.prediction_length
        return {
            'past_values': self.data[idx:he, self.close_idx],         # [hist_len]
            'past_time_features': self.data[idx:he, :4],              # [hist_len, 4]
            'future_values': self.data[he:pe, self.close_idx],       # [pred_len]
            'future_ohlc': self.data[he:pe][:, self.target_indices], # [pred_len, 4]
            'future_time_features': self.data[he:pe, :4],             # [pred_len, 4]
        }

print('Feature engineering...')
train_features = create_technical_features(train_df).dropna()
val_features = create_technical_features(val_df).dropna()
test_features = create_technical_features(test_df).dropna()
print(f'Train: {len(train_features)}, Val: {len(val_features)}, Test: {len(test_features)}')
train_dataset = TimeSeriesDataset(train_features, HISTORY_LENGTH, PREDICTION_LENGTH, FEATURE_COLUMNS, TARGET_COLUMNS)
val_dataset = TimeSeriesDataset(val_features, HISTORY_LENGTH, PREDICTION_LENGTH, FEATURE_COLUMNS, TARGET_COLUMNS)
test_dataset = TimeSeriesDataset(test_features, HISTORY_LENGTH, PREDICTION_LENGTH, FEATURE_COLUMNS, TARGET_COLUMNS)
train_dataloader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
val_dataloader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
test_dataloader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
print('Datasets ready.')
print(f'Features: {len(FEATURE_COLUMNS)}, Targets: {len(TARGET_COLUMNS)} (OHLC)')
print(f'Train batches: {len(train_dataloader)}')
