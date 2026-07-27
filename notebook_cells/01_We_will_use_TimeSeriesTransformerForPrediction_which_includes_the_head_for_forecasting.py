# --- Step 1: Install and Import Necessary Libraries ---

!pip install transformers accelerate torch scikit-learn pandas numpy matplotlib tqdm joblib -q

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from tqdm.notebook import trange, tqdm

import torch
import torch.nn as nn
# --- Transformers Library ---
# We will use TimeSeriesTransformerForPrediction which includes the head for forecasting
from transformers import TimeSeriesTransformerForPrediction, TimeSeriesTransformerConfig # <--- CORRECTED LINE

from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib
import matplotlib.dates as mdates

# --- Reproducibility ---
SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)
print("Libraries imported and seeds set.")

# --- Device Configuration ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")