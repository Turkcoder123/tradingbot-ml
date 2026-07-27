# --- Step 1: Clone Repository & Install Dependencies ---
import os, sys

# Platforma gore klon dizini (sadece burasi degisir)
# Colab -> /content, Kaggle -> /kaggle/working, Local -> . (gecerli dizin)
if os.path.exists('/content'):
    CLONE_DIR = '/content/tradingbot-ml'
elif os.path.exists('/kaggle/working'):
    CLONE_DIR = '/kaggle/working/tradingbot-ml'
else:
    CLONE_DIR = 'tradingbot-ml'  # Local: mevcut dizin altinda

REPO_URL = "https://github.com/Turkcoder123/tradingbot-ml.git"

if not os.path.exists(CLONE_DIR):
    print(f"Cloning repository from {REPO_URL}...")
    !git clone {REPO_URL} {CLONE_DIR}
else:
    print(f"Repository already cloned. Pulling latest changes...")
    %cd {CLONE_DIR}
    !git pull
    %cd ..

%cd {CLONE_DIR}
print(f"Working directory: {os.getcwd()}")

!pip install transformers accelerate torch scikit-learn pandas numpy matplotlib tqdm joblib -q

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from tqdm.notebook import trange, tqdm

import torch
import torch.nn as nn
from transformers import TimeSeriesTransformerForPrediction, TimeSeriesTransformerConfig

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