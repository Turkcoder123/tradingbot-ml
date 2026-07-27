#!/usr/bin/env python3
"""
validate_notebook.py - Notebook'u GitHub'a yuklemeden once syntax ve 
degisken bagimliliklari acisindan kontrol eder.

Kullanim:
    python validate_notebook.py [notebook_yolu]
    python validate_notebook.py Fixed_TimeSeries_Transformer_EURUSD_Forecasting.ipynb
"""

import json
import sys
import ast
import re

# Hucre sirasina gore tanimlanmasi beklenen degiskenler
# (index, {tanimlanan_degiskenler})
CELL_VARIABLES = {
    1: {'pd', 'np', 'plt', 'os', 'json', 'torch', 'nn', 'Dataset', 'DataLoader',
        'AdamW', 'StandardScaler', 'mean_squared_error', 'mean_absolute_error',
        'joblib', 'mdates', 'device', 'SEED', 'tqdm', 'trange'},
    3: {'CONTEXT_LENGTH', 'PREDICTION_LENGTH', 'LAGS_SEQUENCE', 'D_MODEL',
        'ENCODER_LAYERS', 'DECODER_LAYERS', 'ENCODER_ATTENTION_HEADS',
        'DECODER_ATTENTION_HEADS', 'ENCODER_FFN_DIM', 'DECODER_FFN_DIM',
        'DROPOUT', 'EPOCHS', 'LEARNING_RATE', 'BATCH_SIZE', 'PATIENCE',
        'DISTRIBUTION_OUTPUT'},
    5: {'df_raw', 'df_5m', 'df_1h', 'df_1d', 'df', 'train_df', 'val_df', 'test_df',
        'train_size', 'val_size'},
    7: {'create_technical_features', 'FEATURE_COLUMNS', 'TARGET_COLUMNS', 'HISTORY_LENGTH'},
    9: {'scaler_close', 'ohlc_cols'},
    11: {'TimeSeriesDataset', 'train_features', 'val_features', 'test_features',
         'train_dataset', 'val_dataset', 'test_dataset',
         'train_dataloader', 'val_dataloader', 'test_dataloader'},
    13: {'MultiOutputTransformer', 'OHLCTransformerOutput', 'config', 'model'},
    15: {'SPREAD_POINTS', 'COMMISSION_RATE', 'optimizer', 'ohlc_loss_fn',
         'best_val_loss', 'patience_counter'},
    17: {'get_predictions', 'scale_back'},
    19: {'plot_subset_collapsed'},
    21: {'output_dir'},
}

# Her hucrede mevcut olmasi gereken degiskenler (onceki hucrelerden)
CELL_PREREQS = {
    3: set(),  # Cell 3 kendi kendine yeterli (LAGS_SEQUENCE, CONTEXT_LENGTH vs.)
    5: {'pd', 'np'},  # pandas ve numpy import edilmis olmali
    7: {'pd', 'np', 'CONTEXT_LENGTH', 'train_df', 'val_df', 'test_df'},
    9: {'StandardScaler', 'train_df', 'val_df', 'test_df'},
    11: {'torch', 'Dataset', 'DataLoader', 'create_technical_features',
         'FEATURE_COLUMNS', 'TARGET_COLUMNS', 'HISTORY_LENGTH',
         'BATCH_SIZE', 'train_df', 'val_df', 'test_df',
         'CONTEXT_LENGTH', 'PREDICTION_LENGTH'},
    13: {'copy', 'TimeSeriesTransformerForPrediction', 'TimeSeriesTransformerConfig',
         'nn', 'torch', 'FEATURE_COLUMNS', 'device', 'MultiOutputTransformer'},
    15: {'AdamW', 'nn', 'model', 'train_dataloader', 'val_dataloader',
         'EPOCHS', 'PATIENCE', 'device', 'LEARNING_RATE'},
    17: {'model', 'test_dataloader', 'scaler_close', 'np', 'device'},
    19: {'mdates', 'plt', 'np'},
    21: {'torch', 'joblib', 'json', 'model', 'scaler_close'},
}


def extract_variables_from_source(source: str) -> set:
    """Kaynak koddan tanimlanan degisken isimlerini cikar."""
    variables = set()
    
    # import X, import X as Y, from X import Y
    import_patterns = [
        r'^import\s+(\w+)',
        r'^import\s+\w+\s+as\s+(\w+)',
        r'^from\s+[\w.]+\s+import\s+(\w+)',
        r'^from\s+[\w.]+\s+import\s+\(([^)]+)\)',
    ]
    
    lines = source.split('\n')
    for line in lines:
        line_stripped = line.strip()
        
        # import'lari bul
        for pat in import_patterns:
            m = re.match(pat, line_stripped)
            if m:
                names = m.group(1)
                if ',' in names:
                    for n in names.split(','):
                        n = n.strip()
                        if n and not n.startswith('#'):
                            variables.add(n)
                else:
                    variables.add(names)
        
        # X = Y veya X = fonksiyon
        assign_match = re.match(r'^(\w+)\s*=', line_stripped)
        if assign_match and not line_stripped.startswith('#') and not line_stripped.startswith('!'):
            var_name = assign_match.group(1)
            if var_name not in ('super', 'self', 'return', 'elif', 'else', 'if', 'for', 'while',
                               'with', 'class', 'def', 'lambda', 'and', 'or', 'not', 'in', 'is',
                               'try', 'except', 'finally', 'raise', 'assert', 'pass', 'break',
                               'continue', 'import', 'from', 'as'):
                variables.add(var_name)
        
        # class X, def X
        class_match = re.match(r'^(?:class|def)\s+(\w+)', line_stripped)
        if class_match:
            variables.add(class_match.group(1))
    
    return variables


def extract_used_variables(source: str) -> set:
    """Kaynak kodda kullanilan ama tanimlanmayan degiskenleri bul."""
    used = set()
    # Basit regex: kelime karakterleri
    words = re.findall(r'\b[A-Z_][A-Z_0-9]+\b', source)  # BUYUK HARF degiskenler
    words += re.findall(r'\b[a-z_][a-z_0-9]+\b', source)  # kucuk harf degiskenler
    
    # Python keyword'lerini cikar
    keywords = {'if', 'else', 'elif', 'for', 'while', 'in', 'not', 'and', 'or', 'is',
                'def', 'class', 'return', 'yield', 'import', 'from', 'as', 'with',
                'try', 'except', 'finally', 'raise', 'assert', 'pass', 'break',
                'continue', 'lambda', 'True', 'False', 'None', 'range', 'len',
                'int', 'float', 'str', 'list', 'dict', 'tuple', 'set', 'bool',
                'print', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr',
                'super', 'self', 'max', 'min', 'sum', 'abs', 'all', 'any',
                'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed',
                'open', 'close', 'read', 'write', 'append', 'extend', 'keys',
                'values', 'items', 'get', 'pop', 'update', 'clear', 'copy',
                'shape', 'reshape', 'mean', 'std', 'diff', 'sign', 'abs',
                'sqrt', 'exp', 'log', 'sin', 'cos', 'tan',
                'figure', 'plot', 'show', 'legend', 'grid', 'title', 'xlabel',
                'ylabel', 'xticks', 'tight_layout',
                'describe', 'info', 'head', 'tail', 'dropna', 'fillna',
                'resample', 'agg', 'copy'}
    return {w for w in words if w not in keywords and len(w) > 1}


def check_cell(idx: int, source: str, prev_defined: set) -> list:
    """Bir hucreyi kontrol et, hata listesi don."""
    errors = []
    
    # 1. Syntax kontrolu (Jupyter magic ! veya % iceren satirlari temizle)
    clean_source = '\n'.join(
        line for line in source.split('\n')
        if not line.strip().startswith('!') and not line.strip().startswith('%')
    )
    if clean_source.strip():
        try:
            ast.parse(clean_source)
        except SyntaxError as e:
            errors.append(f"  ❌ SYNTAX HATASI (Line {e.lineno}): {e.msg}")
            errors.append(f"     Kod: {e.text.strip()[:80] if e.text else 'N/A'}")
    
    # 2. Jupyter magic komutlari (! veya %) icin ozel kontrol 
    has_magic = any(line.strip().startswith('!') or line.strip().startswith('%') 
                    for line in source.split('\n') if line.strip())
    
    # 3. Tanimlanan degiskenler
    defined = extract_variables_from_source(source)
    
    # 4. Kullanilan degiskenler
    used = extract_used_variables(source)
    
    # 5. Onceki hucrelerde tanimlanmasi gereken degiskenler
    prereqs = CELL_PREREQS.get(idx, set())
    for var in prereqs:
        if var not in prev_defined and var not in defined:
            errors.append(f"  ❌ EKSIK BAGIMLILIK: '{var}' - Onceki hucrelerden gelmeli")
    
    # 6. Bu hucrede tanimlanmasi beklenen degiskenler
    expected = CELL_VARIABLES.get(idx, set())
    missing = expected - defined
    for var in missing:
        # Import ile gelenleri kontrol et
        if var not in source:
            errors.append(f"  ⚠️ UYARI: '{var}' tanimlanmamis olabilir")
    
    # 7. Yorum satiri icinde gomulu kod (orijinal notebook hatasi)
    for line in source.split('\n'):
        if '# ---' in line and '#' in line[line.index('# ---') + 5:]:
            # Yorumdan sonra kod var mi?
            comment_part = line[:line.index('#')]
            code_part = line[line.index('#') + 1:]
            if '=' in code_part and code_part.strip().startswith('#'):
                # Muhtemelen hata
                errors.append(f"  ⚠️ YORUM ICINDE GOMULU KOD: {line.strip()[:80]}")
    
    return errors


def validate_notebook(notebook_path: str):
    """Notebook'u bastan sona dogrula."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    cells = nb['cells']
    total_errors = 0
    prev_defined = set()
    
    # İlk once import'lari ekle (built-in)
    prev_defined.update({'torch', 'nn', 'pd', 'np', 'plt', 'os', 'json', 're',
                         'Dataset', 'DataLoader', 'AdamW', 'StandardScaler',
                         'joblib', 'mdates', 'copy', 'warnings',
                         'TimeSeriesTransformerForPrediction',
                         'TimeSeriesTransformerConfig'})
    
    print('='*70)
    print(f'  NOTEBOK DOGRULAMA: {notebook_path}')
    print('='*70)
    
    for i, cell in enumerate(cells):
        cell_type = cell['cell_type']
        source = ''.join(cell['source'])
        
        if not source.strip():
            continue
        
        # Markdown hucrelerini atla (Python syntax'i degil)
        if cell_type == 'markdown':
            continue
        
        # Baslik bul
        title = ''
        for line in source.split('\n'):
            line = line.strip()
            if line.startswith('# ') and not line.startswith('# --'):
                title = line[2:].strip()[:60]
                break
            elif line.startswith('#') and 'Step' in line:
                title = line[1:].strip()[:60]
                break
        
        print(f'\n--- Cell {i:02d} [{cell_type}] {title}')
        
        errors = check_cell(i, source, prev_defined)
        
        if errors:
            total_errors += len(errors)
            for e in errors:
                print(e)
        else:
            print(f'  ✅ Basarili')
        
        # Bu hucrenin tanimladigi degiskenleri ekle
        defined = extract_variables_from_source(source)
        prev_defined.update(defined)
    
    print(f'\n{"="*70}')
    if total_errors > 0:
        print(f'  ❌ {total_errors} hata/uyari bulundu!')
        print(f'  Yukaridaki hatalari duzeltmeden GitHub\'a gondermeyin.')
    else:
        print(f'  ✅ Tum kontroller basarili!')
        print(f'  GitHub\'a yuklemeye hazir.')
    print(f'{"="*70}')
    
    return total_errors


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'Fixed_TimeSeries_Transformer_EURUSD_Forecasting.ipynb'
    notebook_path = path if path.startswith('tradingbot-ml/') else f'tradingbot-ml/{path}'
    import os
    if not os.path.exists(notebook_path):
        notebook_path = path
    sys.exit(validate_notebook(notebook_path))