#!/usr/bin/env python3
"""
split_notebook.py - Notebook'u her hücresi ayrı bir dosyaya böler.

Kullanım:
    python split_notebook.py [notebook_yolu] [output_dizini]

Varsayılanlar:
    notebook_yolu  = TimeSeries_Transformer_EURUSD_Forecasting.ipynb
    output_dizini  = notebook_cells/
"""

import json
import os
import sys
import re


def sanitize_filename(name: str) -> str:
    """Dosya adı için güvenli bir isim oluştur."""
    # Alfanumerik olmayan karakterleri alt çizgiye çevir
    name = re.sub(r'[^\w\s-]', '_', name)
    name = re.sub(r'[-\s]+', '_', name)
    return name.strip('_')


def extract_cell_title(source: str) -> str:
    """Hücrenin ilk yorum satırından veya markdown başlığından isim çıkar."""
    lines = source.split('\n')
    for line in lines:
        line = line.strip()
        # Markdown başlığı
        if line.startswith('# ') and not line.startswith('# --'):
            return line.lstrip('# ').strip()
        # Kod yorumu başlığı
        if line.startswith('# ') or line.startswith('#'):
            title = line.lstrip('#').strip()
            if title and not title.startswith('-'):
                return title
    return None


def split_notebook(notebook_path: str, output_dir: str):
    """Notebook'u hücrelere ayırıp ayrı dosyalara yazar."""
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    cells = nb['cells']
    os.makedirs(output_dir, exist_ok=True)
    
    # Eski hücre dosyalarını temizle (sadece NNN_ ile başlayan .py ve .md dosyaları)
    # Böylece notebook'tan silinen hücrelerin dosyaları da silinmiş olur
    for fname in os.listdir(output_dir):
        if fname.startswith('_'):
            continue  # metadata dosyalarını silme
        fpath = os.path.join(output_dir, fname)
        if os.path.isfile(fpath) and (fname.endswith('.py') or fname.endswith('.md')):
            os.remove(fpath)
            print(f"  [CLEAN] Eski dosya silindi: {fname}")

    # Metadata'yı kaydet (merge için gerekli)
    metadata_path = os.path.join(output_dir, '_metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(nb.get('metadata', {}), f, indent=2, ensure_ascii=False)
    print(f"[INFO] Metadata kaydedildi: {metadata_path}")

    file_list = []
    
    for i, cell in enumerate(cells):
        cell_type = cell['cell_type']
        source = ''.join(cell['source'])
        
        # Dosya adı oluştur
        title = extract_cell_title(source) or f"cell_{i:02d}"
        safe_title = sanitize_filename(title)
        
        if cell_type == 'code':
            ext = '.py'
        else:
            ext = '.md'
        
        # Kod hücrelerinde ilk yorum satırını temizle (başlık olarak kullanıldıysa)
        if cell_type == 'code':
            filename = f"{i:02d}_{safe_title}{ext}"
        else:
            filename = f"{i:02d}_{safe_title}{ext}"
        
        filepath = os.path.join(output_dir, filename)
        
        # writelines ile yaz: orijinal satır sonu karakterlerini (\n) koru
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.writelines(cell['source'])
        
        file_list.append({
            'index': i,
            'cell_type': cell_type,
            'filename': filename,
            'title': title or '',
            'source_len': len(source)
        })
        
        print(f"  [{i:02d}] {cell_type:8s} -> {filename}  ({len(source)} chars)")

    # Dosya listesini de kaydet
    list_path = os.path.join(output_dir, '_file_list.json')
    with open(list_path, 'w', encoding='utf-8') as f:
        json.dump(file_list, f, indent=2, ensure_ascii=False)
    
    print(f"\n[INFO] Toplam {len(cells)} hücre dosyalandı.")
    print(f"[INFO] Çıktı dizini: {os.path.abspath(output_dir)}")
    print(f"[INFO] Dosya listesi: {list_path}")


if __name__ == '__main__':
    notebook_path = sys.argv[1] if len(sys.argv) > 1 else 'TimeSeries_Transformer_EURUSD_Forecasting.ipynb'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'notebook_cells'
    
    split_notebook(notebook_path, output_dir)