# --- Step 7: Multi-Output Transformer ---
from transformers import TimeSeriesTransformerForPrediction, TimeSeriesTransformerConfig
import torch.nn as nn, torch, copy

class MultiOutputTransformer(nn.Module):
    def __init__(self, base_config, num_outputs=4):
        super().__init__()
        self.base_model = TimeSeriesTransformerForPrediction(base_config)
        hidden_dim = base_config.d_model
        self.ohlc_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim), nn.ReLU(),
            nn.Dropout(base_config.dropout), nn.Linear(hidden_dim, num_outputs)
        )
    def forward(self, past_values, past_time_features, past_observed_mask=None,
                future_values=None, future_time_features=None, future_observed_mask=None,
                future_ohlc=None):
        outputs = self.base_model(
            past_values=past_values, past_time_features=past_time_features,
            past_observed_mask=past_observed_mask, future_values=future_values,
            future_time_features=future_time_features, future_observed_mask=future_observed_mask,
        )
        # decoder_hidden_states[-1]: [batch, pred_len, d_model] (requires output_hidden_states=True)
        dec_out = outputs.decoder_hidden_states[-1]
        ohlc_pred = self.ohlc_head(dec_out)  # [batch, pred_len, 4]
        return OHLCTransformerOutput(ohlc_pred, outputs)
    def num_params(self):
        return sum(p.numel() for p in self.parameters())

class OHLCTransformerOutput:
    def __init__(self, ohlc_pred, base_outputs):
        self.ohlc = ohlc_pred
        self.base = base_outputs
        self.loss = base_outputs.loss
    @property
    def prediction_outputs(self):
        return self.base.prediction_outputs

config = TimeSeriesTransformerConfig(
    prediction_length=PREDICTION_LENGTH, context_length=CONTEXT_LENGTH,
    lags_sequence=LAGS_SEQUENCE, num_time_features=4,
    num_static_categorical_features=0, distribution_output='student_t', loss='nll',
    encoder_layers=ENCODER_LAYERS, decoder_layers=DECODER_LAYERS,
    d_model=D_MODEL, encoder_attention_heads=ENCODER_ATTENTION_HEADS,
    decoder_attention_heads=DECODER_ATTENTION_HEADS,
    encoder_ffn_dim=ENCODER_FFN_DIM, decoder_ffn_dim=DECODER_FFN_DIM,
    dropout=DROPOUT, output_hidden_states=True,  # KRITIK: decoder hidden'larina erismek icin
)
model = MultiOutputTransformer(config, num_outputs=4)
model.to(device)
print(f'Model created. Outputs: 4 (OHLC). Params: {model.num_params():,}')
