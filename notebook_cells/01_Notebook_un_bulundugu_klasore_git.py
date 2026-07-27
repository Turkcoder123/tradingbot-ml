# --- Step 1: Install and Import Necessary Libraries ---

# --- Google Drive Mount (Colab icin) ---
import sys
IN_COLAB = 'google.colab' in sys.modules
if IN_COLAB:
    from google.colab import drive
    drive.mount('/content/drive')
    import os
    # Notebook'un bulundugu klasore git
    import os.path
    # Dosyayi proje kokunde ara
    if not os.path.exists('Data'):
        # Drive'da ara
        possible = [
            '/content/drive/MyDrive/tradingbot-ml',
            '/content/drive/MyDrive/Colab Notebooks/tradingbot-ml',
        ]
        for p in possible:
            if os.path.exists(os.path.join(p, 'Data')):
                os.chdir(p)
                print(f'Calisma dizini: {p}')
                break
    print(f'Mevcut dizin: {os.getcwd()}')
    print(f'Data klasoru var: {os.path.isdir("Data")}')
else:
    print('Yerel ortamda calisiyor')

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