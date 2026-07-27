# --- Step 9: Final Evaluation with Multi-Output and Spread/Commission Awareness ---

def get_predictions_and_actuals(loader, target_scaler):
    """Helper function to get multi-output predictions (O,H,L,C) and true values."""

    model.eval()
    all_pred_open = []
    all_pred_high = []
    all_pred_low = []
    all_pred_close = []
    all_actual_open = []
    all_actual_high = []
    all_actual_low = []
    all_actual_close = []
    all_stds = []

    with torch.no_grad():
        for batch in tqdm(loader, desc="Evaluating"):
            past_values = batch['past_values'].to(device)
            past_time_features = batch['past_time_features'].to(device)
            future_time_features = batch['future_time_features'].to(device)
            future_values = batch['future_values'].to(device)  # Shape: [batch, pred_len, 4] for O,H,L,C

            outputs = model(
                past_values=past_values,
                past_time_features=past_time_features,
                future_time_features=future_time_features,
            )

            # Get multi-output predictions: loc is [batch, pred_len, 4]
            pred_loc = outputs.prediction_outputs.loc.cpu().numpy()  # [batch, pred_len, 4]
            pred_scale = outputs.prediction_outputs.scale.cpu().numpy()  # [batch, pred_len, 4]

            actual = future_values.cpu().numpy()  # Shape: [batch, pred_len, 4] for O,H,L,C

            all_pred_open.append(pred_loc[:, :, 0])
            all_pred_high.append(pred_loc[:, :, 1])
            all_pred_low.append(pred_loc[:, :, 2])
            all_pred_close.append(pred_loc[:, :, 3])
            
            all_actual_open.append(actual[:, :, 0])
            all_actual_high.append(actual[:, :, 1])
            all_actual_low.append(actual[:, :, 2])
            all_actual_close.append(actual[:, :, 3])
            all_stds.append(pred_scale[:, :, 3])  # Close std for uncertainty

    pred_open = np.concatenate(all_pred_open).flatten()
    pred_high = np.concatenate(all_pred_high).flatten()
    pred_low = np.concatenate(all_pred_low).flatten()
    pred_close = np.concatenate(all_pred_close).flatten()
    
    actual_open = np.concatenate(all_actual_open).flatten()
    actual_high = np.concatenate(all_actual_high).flatten()
    actual_low = np.concatenate(all_actual_low).flatten()
    actual_close = np.concatenate(all_actual_close).flatten()
    stds = np.concatenate(all_stds).flatten()

    # Inverse transform to original price scale
    pred_open_prices = target_scaler.inverse_transform(pred_open.reshape(-1, 1)).flatten()
    pred_high_prices = target_scaler.inverse_transform(pred_high.reshape(-1, 1)).flatten()
    pred_low_prices = target_scaler.inverse_transform(pred_low.reshape(-1, 1)).flatten()
    pred_close_prices = target_scaler.inverse_transform(pred_close.reshape(-1, 1)).flatten()
    
    actual_open_prices = target_scaler.inverse_transform(actual_open.reshape(-1, 1)).flatten()
    actual_high_prices = target_scaler.inverse_transform(actual_high.reshape(-1, 1)).flatten()
    actual_low_prices = target_scaler.inverse_transform(actual_low.reshape(-1, 1)).flatten()
    actual_close_prices = target_scaler.inverse_transform(actual_close.reshape(-1, 1)).flatten()

    return pred_open_prices, pred_high_prices, pred_low_prices, pred_close_prices, \
           actual_open_prices, actual_high_prices, actual_low_prices, actual_close_prices, stds


print("Getting test set predictions...")
test_pred_open, test_pred_high, test_pred_low, test_pred_close, \
test_actual_open, test_actual_high, test_actual_low, test_actual_close, test_stds = get_predictions_and_actuals(
    test_dataloader, target_scaler
)


# Calculate metrics
rmse = np.sqrt(np.mean((test_pred_close - test_actual_close)**2))
mae = np.mean(np.abs(test_pred_close - test_actual_close))
mean_pred_diff = np.mean(np.abs(np.diff(test_pred_close)))
mean_actual_diff = np.mean(np.abs(np.diff(test_actual_close)))


print(f"=== Test Set Evaluation ===")
print(f"RMSE: {rmse:.6f}")
print(f"MAE: {mae:.6f}")
print(f"Mean prediction change (5m): {mean_pred_diff:.6f}")
print(f"Mean actual change (5m): {mean_actual_diff:.6f}")


# Spread and commission analysis
SPREAD = 0.0001  # 1 pip typical EURUSD spread
COMMISSION = 0.00002  # 0.002% per side


# Calculate profitable trades using OHLC information
pred_changes = np.diff(test_pred_close)
actual_changes = np.diff(test_actual_close)


# Trading cost
trading_cost = SPREAD + COMMISSION


# Direction accuracy
direction_correct = np.sign(pred_changes) == np.sign(actual_changes)
direction_accuracy = np.mean(direction_correct) * 100


# Profitable trade accuracy (considering costs)
profitable_long = actual_changes > trading_cost
profitable_short = actual_changes < -trading_cost
predicted_up = pred_changes > 0
predicted_down = pred_changes < 0


profitable_trades = (predicted_up & profitable_long) | (predicted_down & profitable_short)
profitable_accuracy = np.mean(profitable_trades) * 100


print(f"=== Trading Performance ===")
print(f"Direction Accuracy: {direction_accuracy:.2f}%")
print(f"Profitable Trade Accuracy (after costs): {profitable_accuracy:.2f}%")
print(f"Average predicted move: {np.mean(np.abs(pred_changes)):.6f}")
print(f"Average actual move: {np.mean(np.abs(actual_changes)):.6f}")
print(f"Trading cost threshold: {trading_cost:.6f}")


# OHLC-based analysis: Check if High-Low range covers profitable moves
print(f"\n=== OHLC Analysis ===")
print(f"Avg predicted High-Low range: {np.mean(test_pred_high - test_pred_low):.6f}")
print(f"Avg actual High-Low range: {np.mean(test_actual_high - test_actual_low):.6f}")
