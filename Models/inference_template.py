"""
EURUSD Transformer Inference Template
Multi-output forecasting for Open, High, Low, Close prices
"""
import torch
import joblib
import numpy as np
import pandas as pd
from transformers import TimeSeriesTransformerForPrediction, TimeSeriesTransformerConfig


def load_model_and_artifacts(models_dir='Models'):
    """Load model weights, scalers, and configuration."""
    
    # Load scalers and config
    scalers = joblib.load(f'{models_dir}/scalers.joblib')
    config_data = joblib.load(f'{models_dir}/config.joblib')
    
    # Initialize transformer config
    transformer_config = TimeSeriesTransformerConfig(
        context_length=config_data['CONTEXT_LENGTH'],
        prediction_length=config_data['PREDICTION_LENGTH'],
        d_model=config_data['D_MODEL'],
        encoder_layers=config_data['ENCODER_LAYERS'],
        decoder_layers=config_data['DECODER_LAYERS'],
        encoder_attention_heads=config_data['ENCODER_ATTENTION_HEADS'],
        decoder_attention_heads=config_data['DECODER_ATTENTION_HEADS'],
        encoder_ffn_dim=config_data['ENCODER_FFN_DIM'],
        decoder_ffn_dim=config_data['DECODER_FFN_DIM'],
        dropout=config_data['DROPOUT'],
        feature_size=len(config_data['FEATURE_COLUMNS']),
        lags_sequence=config_data['LAGS_SEQUENCE'],
    )
    
    # Initialize and load model
    model = TimeSeriesTransformerForPrediction.from_config(transformer_config)
    model.load_state_dict(torch.load(f'{models_dir}/best_transformer_model.pth', weights_only=True))
    model.eval()
    
    return model, scalers, config_data


def prepare_features(df, feature_columns, scalers, is_training=False):
    """
    Prepare features for inference.
    
    Args:
        df: DataFrame with raw OHLCV data
        feature_columns: List of feature column names
        scalers: Dictionary containing fitted scalers
        is_training: If True, fit the ohlv_scaler
    
    Returns:
        Scaled feature array
    """
    # Ensure all required columns exist
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0.0  # Fill missing columns with 0
    
    # Extract features
    features = df[feature_columns].values
    
    # Scale OHLCV features
    if is_training:
        features = scalers['ohlv_scaler'].fit_transform(features)
    else:
        features = scalers['ohlv_scaler'].transform(features)
    
    return features


def create_input_tensor(features, context_length, lags_sequence):
    """
    Create input tensor for the transformer model.
    
    Args:
        features: Scaled feature array
        context_length: Number of historical time steps to use
        lags_sequence: List of lag values
    
    Returns:
        Input tensor of shape (batch_size, context_length, feature_size)
    """
    max_lag = max(lags_sequence)
    history_length = context_length + max_lag
    
    if len(features) < history_length:
        raise ValueError(f"Need at least {history_length} samples, got {len(features)}")
    
    # Take the last context_length + max_lag samples
    recent_features = features[-history_length:]
    
    # Convert to tensor
    input_tensor = torch.FloatTensor(recent_features).unsqueeze(0)  # Add batch dimension
    
    return input_tensor


def predict(model, input_tensor, num_samples=100):
    """
    Generate predictions using the trained model.
    
    Args:
        model: Trained transformer model
        input_tensor: Input tensor of shape (1, context_length, feature_size)
        num_samples: Number of Monte Carlo samples for probabilistic prediction
    
    Returns:
        Predicted values for Open, High, Low, Close
    """
    with torch.no_grad():
        # Get prediction
        outputs = model(input_tensor)
        
        # For distribution output, get mean prediction
        if hasattr(outputs, 'loc'):
            predictions = outputs.loc  # Mean of the distribution
        else:
            predictions = outputs.prediction_logits
        
        # predictions shape: (batch_size, prediction_length, target_dim)
        return predictions.squeeze(0).numpy()


def inverse_transform_predictions(predictions, target_scaler, target_columns):
    """
    Convert scaled predictions back to original price scale.
    
    Args:
        predictions: Model output (scaled)
        target_scaler: Fitted StandardScaler for target variables
        target_columns: Names of target columns
    
    Returns:
        DataFrame with predictions in original scale
    """
    # Reshape if needed
    if predictions.ndim == 1:
        predictions = predictions.reshape(1, -1)
    
    # Inverse transform
    predictions_original = target_scaler.inverse_transform(predictions)
    
    # Create DataFrame
    pred_df = pd.DataFrame(
        predictions_original,
        columns=target_columns
    )
    
    return pred_df


def main():
    """Example inference workflow."""
    
    print("=" * 60)
    print("EURUSD Transformer Inference")
    print("=" * 60)
    
    # Load model and artifacts
    print("\nLoading model and artifacts...")
    model, scalers, config_data = load_model_and_artifacts()
    
    print(f"✓ Model loaded successfully")
    print(f"  - Input features: {len(config_data['FEATURE_COLUMNS'])}")
    print(f"  - Output targets: {config_data['TARGET_COLUMNS']}")
    print(f"  - Context length: {config_data['CONTEXT_LENGTH']}")
    print(f"  - Prediction length: {config_data['PREDICTION_LENGTH']}")
    
    # Example: Create sample input data
    print("\nCreating sample input data...")
    
    # You would replace this with your actual market data
    sample_data = pd.DataFrame({
        'Open': np.random.uniform(1.08, 1.10, 500),
        'High': np.random.uniform(1.08, 1.10, 500),
        'Low': np.random.uniform(1.08, 1.10, 500),
        'Close': np.random.uniform(1.08, 1.10, 500),
        'Volume': np.random.randint(100, 1000, 500),
    })
    
    # Add placeholder technical indicators
    for col in config_data['FEATURE_COLUMNS']:
        if col not in sample_data.columns:
            sample_data[col] = 0.0
    
    # Prepare features
    features = prepare_features(
        sample_data, 
        config_data['FEATURE_COLUMNS'], 
        scalers,
        is_training=False
    )
    
    # Create input tensor
    input_tensor = create_input_tensor(
        features,
        config_data['CONTEXT_LENGTH'],
        config_data['LAGS_SEQUENCE']
    )
    
    print(f"✓ Input tensor shape: {input_tensor.shape}")
    
    # Generate predictions
    print("\nGenerating predictions...")
    predictions_scaled = predict(model, input_tensor)
    
    # Inverse transform to get actual prices
    predictions = inverse_transform_predictions(
        predictions_scaled,
        scalers['target_scaler'],
        config_data['TARGET_COLUMNS']
    )
    
    print("\n" + "=" * 60)
    print("PREDICTIONS (next time step):")
    print("=" * 60)
    print(predictions.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("Inference completed successfully!")
    print("=" * 60)
    
    return predictions


if __name__ == "__main__":
    predictions = main()
