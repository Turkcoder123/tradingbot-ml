# --- Step 7: Define the Multi-Output Transformer Model ---
from transformers import TimeSeriesTransformerForPrediction
from torch import nn
import torch

# Custom wrapper for multi-output prediction
class MultiOutputTransformer(nn.Module):
    def __init__(self, base_config, num_outputs=4):
        super().__init__()
        self.base_model = TimeSeriesTransformerForPrediction(base_config)
        self.num_outputs = num_outputs
        
        # Replace the distribution output with multi-output head
        hidden_dim = base_config.d_model
        self.output_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(base_config.dropout),
            nn.Linear(hidden_dim, num_outputs * 2)  # loc and scale for each output
        )
        
    def forward(self, past_values, past_time_features, past_observed_mask=None,
                future_values=None, future_time_features=None, future_observed_mask=None):
        # Get base model outputs
        outputs = self.base_model(
            past_values=past_values,
            past_time_features=past_time_features,
            past_observed_mask=past_observed_mask,
            future_values=future_values,
            future_time_features=future_time_features,
            future_observed_mask=future_observed_mask,
        )
        
        # Get the decoder last hidden state
        decoder_output = outputs.decoder_last_hidden_state  # [batch, pred_len, d_model]
        batch_size, pred_len, _ = decoder_output.shape
        
        # Predict multi-output parameters
        output_params = self.output_head(decoder_output)  # [batch, pred_len, num_outputs*2]
        output_params = output_params.view(batch_size, pred_len, self.num_outputs, 2)
        
        return MultiOutput(outputs, output_params)

class MultiOutput:
    def __init__(self, base_outputs, params):
        self.base = base_outputs
        self.params = params  # [batch, pred_len, num_outputs, 2]
        self.loss = base_outputs.loss
        self.prediction_outputs = self
        
    @property
    def loc(self):
        return self.params[:, :, :, 0]  # [batch, pred_len, num_outputs]
    
    @property  
    def scale(self):
        return torch.nn.functional.softplus(self.params[:, :, :, 1])  # [batch, pred_len, num_outputs]
    
    def mean(self):
        return self.loc
    
# Update config for multi-feature input
config = TimeSeriesTransformerConfig(
    prediction_length=PREDICTION_LENGTH,
    context_length=CONTEXT_LENGTH,
    lags_sequence=LAGS_SEQUENCE,
    num_time_features=len(FEATURE_COLUMNS),
    num_static_categorical_features=0,
    distribution_output="student_t",
    loss="nll",
    encoder_layers=ENCODER_LAYERS,
    decoder_layers=DECODER_LAYERS,
    d_model=D_MODEL,
    encoder_attention_heads=ENCODER_ATTENTION_HEADS,
    decoder_attention_heads=DECODER_ATTENTION_HEADS,
    encoder_ffn_dim=ENCODER_FFN_DIM,
    decoder_ffn_dim=DECODER_FFN_DIM,
    dropout=DROPOUT,
)

model = MultiOutputTransformer(config, num_outputs=4)
model.to(device)

print("Multi-output TimeSeriesTransformer model created.")
print(f"Number of input features: {len(FEATURE_COLUMNS)}")
print(f"Number of outputs: 4 (Open, High, Low, Close)")
print(f"Total model parameters: {model.num_parameters():,}")