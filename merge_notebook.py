#!/usr/bin/env python3
"""
merge_notebook.py - Ayrılmış hücre dosyalarını tekrar .ipynb notebook'una birleştirir.

Kullanım:
    python merge_notebook.py [input_dizini] [output_notebook_yolu]

Varsayılanlar:
    input_dizini       = notebook_cells/
    output_notebook_yolu = Merged_TimeSeries_Transformer_EURUSD_Forecasting.ipynb
"""

import json
import os
import sys
import re
from datetime import datetime


def sort_key(filename: str) -> int:
    """Dosya adındaki ilk sayıya göre sıralama anahtarı."""
    match = re.match(r'(\d+)', filename)
    return int(match.group(1)) if match else 9999


def merge_notebook(input_dir: str, output_path: str):
    """Dosyaları okuyup yeniden .ipynb formatında birleştirir."""
    
    if not os.path.isdir(input_dir):
        print(f"[HATA] Dizin bulunamadı: {input_dir}")
        sys.exit(1)

    # Metadata'yı yükle
    metadata_path = os.path.join(input_dir, '_metadata.json')
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"[INFO] Metadata yüklendi: {metadata_path}")
    else:
        metadata = {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10.0"
            }
        }
        print("[INFO] Metadata bulunamadı, varsayılan kullanılıyor.")

    # Dosya listesini yükle veya dizini tara
    file_list_path = os.path.join(input_dir, '_file_list.json')
    cell_files = []
    
    if os.path.exists(file_list_path):
        with open(file_list_path, 'r', encoding='utf-8') as f:
            file_list = json.load(f)
        cell_files = file_list
        print(f"[INFO] Dosya listesi yüklendi: {file_list_path}")
    else:
        # _ ile başlamayan tüm .py ve .md dosyalarını bul
        for fname in sorted(os.listdir(input_dir), key=sort_key):
            if fname.startswith('_'):
                continue
            if fname.endswith('.py') or fname.endswith('.md'):
                cell_type = 'code' if fname.endswith('.py') else 'markdown'
                cell_files.append({
                    'index': len(cell_files),
                    'cell_type': cell_type,
                    'filename': fname
                })
        cell_files.sort(key=lambda x: sort_key(x['filename']))
        print(f"[INFO] Dizin taranarak {len(cell_files)} dosya bulundu.")

    # Hücreleri oluştur
    cells = []
    for cf in cell_files:
        filepath = os.path.join(input_dir, cf['filename'])
        
        if not os.path.exists(filepath):
            print(f"[UYARI] Dosya bulunamadı, atlanıyor: {filepath}")
            continue
        
        # readlines() ile oku: satır sonu karakterlerini (\n) koru
        with open(filepath, 'r', encoding='utf-8') as f:
            source_lines = f.readlines()
        
        cell = {
            'cell_type': cf['cell_type'],
            'metadata': {},
            'source': source_lines
        }
        
        # Kod hücreleri için ek alanlar
        if cf['cell_type'] == 'code':
            cell['execution_count'] = None
            cell['outputs'] = []
        
        cells.append(cell)

    # Notebook'u oluştur
    notebook = {
        'nbformat': 4,
        'nbformat_minor': 5,
        'metadata': metadata,
        'cells': cells
    }

    # Çıktı dizinini kontrol et
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print(f"\n[INFO] Birleştirme tamamlandı!")
    print(f"[INFO] Toplam {len(cells)} hücre birleştirildi.")
    print(f"[INFO] Çıktı: {os.path.abspath(output_path)}")
    
    # Özet
    code_count = sum(1 for c in cells if c['cell_type'] == 'code')
    md_count = sum(1 for c in cells if c['cell_type'] == 'markdown')
    print(f"[INFO] Kod hücresi: {code_count}, Markdown hücresi: {md_count}")


if __name__ == '__main__':
    input_dir = sys.argv[1] if len(sys.argv) > 1 else 'notebook_cells'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'Merged_TimeSeries_Transformer_EURUSD_Forecasting.ipynb'
    
    merge_notebook(input_dir, output_path)