# --- Step 1: Setup Environment & Install Dependencies ---
import os, sys, subprocess

REPO_URL = "https://github.com/Turkcoder123/tradingbot-ml.git"
CLONE_DIR = "/content/tradingbot-ml"

# Once clone dene, calismazsa Kaggle/Local
if not os.path.exists(CLONE_DIR):
    result = subprocess.run(
        ["git", "clone", REPO_URL, CLONE_DIR],
        capture_output=True, text=True, timeout=30
    )
    clone_success = result.returncode == 0
else:
    clone_success = True

if clone_success:
    os.chdir(CLONE_DIR)
elif os.path.exists('/kaggle/working'):
    os.chdir('/kaggle/working')

print("Working directory:", os.getcwd())

get_ipython().system('pip install -q transformers accelerate torch scikit-learn pandas numpy matplotlib tqdm joblib')

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