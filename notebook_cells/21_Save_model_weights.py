# --- Step 11: Save Final Artifacts for Deployment (Complete Package with Multi-Output Support) ---
import joblib
import os

output_dir = 'Models'
os.makedirs(output_dir, exist_ok=True)

# Save model weights
torch.save(model.state_dict(), os.path.join(output_dir, 'model_weights.pth'))

# Save all scalers including multi-output support
scalers = {
    'target_scaler': target_scaler,  # For Close prices
    'ohlv_scaler': ohlv_scaler,      # For OHLCV features
    'feature_columns': FEATURE_COLUMNS,
    'target_columns': TARGET_COLUMNS,  # New: Multi-output targets
}
joblib.dump(scalers, os.path.join(output_dir, 'scalers.joblib'))

# Save configuration with multi-output info
config_data = {
    'CONTEXT_LENGTH': CONTEXT_LENGTH,
    'PREDICTION_LENGTH': PREDICTION_LENGTH,
    'LAGS_SEQUENCE': LAGS_SEQUENCE,
    'FEATURE_COLUMNS': FEATURE_COLUMNS,
    'TARGET_COLUMNS': TARGET_COLUMNS,  # New: Multi-output targets
    'BATCH_SIZE': BATCH_SIZE,
    'LEARNING_RATE': LEARNING_RATE,
    'D_MODEL': D_MODEL,
    'ENCODER_LAYERS': ENCODER_LAYERS,
    'DECODER_LAYERS': DECODER_LAYERS,
    'ENCODER_ATTENTION_HEADS': ENCODER_ATTENTION_HEADS,
    'DECODER_ATTENTION_HEADS': DECODER_ATTENTION_HEADS,
    'ENCODER_FFN_DIM': ENCODER_FFN_DIM,
    'DECODER_FFN_DIM': DECODER_FFN_DIM,
    'DROPOUT': DROPOUT,
    'DISTRIBUTION_OUTPUT': DISTRIBUTION_OUTPUT,
    'EPOCHS': EPOCHS,
    'PATIENCE': PATIENCE,
    'SPREAD_POINTS': SPREAD_POINTS,
    'COMMISSION_RATE': COMMISSION_RATE,
}
joblib.dump(config_data, os.path.join(output_dir, 'config.joblib'))

# Create a simple inference script template
inference_script = """
import torch
import joblib
import numpy as np
from transformers import TimeSeriesTransformerForPrediction, TimeSeriesTransformerConfig

# Load artifacts
scalers = joblib.load('Models/scalers.joblib')
config_data = joblib.load('Models/config.joblib')

# Initialize model
config = TimeSeriesTransformerConfig(**config_data)
model = TimeSeriesTransformerForPrediction.from_config(config)
model.load_state_dict(torch.load('Models/model_weights.pth'))
model.eval()

# Use scalers and config for inference
print("Model loaded successfully with multi-output support!")
print(f"Input features: {len(config_data['FEATURE_COLUMNS'])}")
print(f"Output targets: {config_data['TARGET_COLUMNS']}")
"""

with open(os.path.join(output_dir, 'inference_template.py'), 'w') as f:
    f.write(inference_script)

print(f"\=== All artifacts saved to '{output_dir}' directory ===")
print(f"- model_weights.pth: Model parameters")
print(f"- scalers.joblib: Scalers and column names (including multi-output)")
print(f"- config.joblib: Full configuration")
print(f"- inference_template.py: Template for deployment")
print(f"\Multi-output support: {TARGET_COLUMNS}")