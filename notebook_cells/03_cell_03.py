# --- Step 2: Hyperparameter Configuration ---

# --- Data and Model Architecture ---
CONTEXT_LENGTH = 288        # Covers 50-period SMA + multi-timeframe (1 day of 5m bars)
PREDICTION_LENGTH = 6       # Dynamic: 6 steps ahead (30 min), can be adjusted by confidence
# --- Lags Sequence Configuration ---LAGS_SEQUENCE = [1, 2, 3, 4, 5, 6, 7] # This is a strong, standard default.

# --- Model Size & Regularization ---D_MODEL = 64                # Increased to handle 37 input features
ENCODER_LAYERS = 2
DECODER_LAYERS = 2
ENCODER_ATTENTION_HEADS = 4
DECODER_ATTENTION_HEADS = 4
ENCODER_FFN_DIM = 128
DECODER_FFN_DIM = 128
DROPOUT = 0.2               # Increased for better regularization

# --- Training Schedule & Objective ---
EPOCHS = 50
LEARNING_RATE = 1e-4
BATCH_SIZE = 64
PATIENCE = 10
DISTRIBUTION_OUTPUT = "student_t" 