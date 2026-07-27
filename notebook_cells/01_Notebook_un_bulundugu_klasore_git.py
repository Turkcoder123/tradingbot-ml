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

# --- Colab Ortam Ayarı (GitHub uyumlu) ---
import sys, os
IN_COLAB = 'google.colab' in sys.modules
if IN_COLAB:
    # Colab GitHub'dan acildiginda /content/tradingbot-ml/ altinda olur
    # Ama bazen dogrudan /content/ altinda da olabilir
    if os.path.basename(os.getcwd()) != 'tradingbot-ml' and not os.path.exists('Data'):
        if os.path.exists('/content/tradingbot-ml/TimeSeries_Transformer_EURUSD_Forecasting.ipynb'):
            os.chdir('/content/tradingbot-ml')
            print('-> /content/tradingbot-ml/')
        else:
            # GitHub'dan clone et
            repo_url = 'https://github.com/Turkcoder123/tradingbot-ml.git'
            print(f'Cloning {repo_url}...')
            get_ipython().system(f'git clone {repo_url}')
            os.chdir('tradingbot-ml')
            print('-> /content/tradingbot-ml/')
    print(f'Calisma dizini: {os.getcwd()}')
    print(f'Data var: {os.path.isdir("Data")}')
else:
    print('Yerel ortam')

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