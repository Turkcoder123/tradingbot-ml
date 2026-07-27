# --- Step 11: Save ---
import os
output_dir = 'Models'
torch.save(model.state_dict(), 'Models/model_weights.pth')
joblib.dump(scaler_close, 'Models/scaler_close.pkl')
json.dump(dict(context_length=CONTEXT_LENGTH, prediction_length=PREDICTION_LENGTH,
    lags_sequence=LAGS_SEQUENCE, d_model=D_MODEL, target_columns=TARGET_COLUMNS,
    scaler_mean=scaler_close.mean_.tolist(), scaler_std=scaler_close.scale_.tolist()),
    open('Models/config.json', 'w'), indent=2)
print('All artifacts saved to Models/')
