#!/usr/bin/env python3
"""
RP News - Excel to JSON Converter
Reads the news Excel file and produces a normalized JSON for the frontend.
Usage: python convert.py [path_to_excel]
Default: looks for Sample.xlsx in the same directory.
"""

import pandas as pd
import json
import sys
import re
import os
from urllib.parse import urlparse
from datetime import datetime

def extract_source(title, url):
    """Extract source from title parentheses, then URL domain, then fallback."""
    match = re.search(r'\(([^)]+)\)\s*$', title or '')
    if match:
        return match.group(1).strip()
    if url and isinstance(url, str):
        try:
            domain = urlparse(url).netloc.replace('www.', '')
            parts = domain.split('.')
            if len(parts) >= 2:
                return parts[0].capitalize()
        except:
            pass
    return "Fuente no identificada"

def clean_title(title):
    """Remove source parenthetical from end of title and strip whitespace."""
    if not title:
        return "Sin título"
    title = title.strip().replace('\n', ' ').replace('\r', '')
    title = re.sub(r'\s*\([^)]+\)\s*$', '', title)
    return title.strip()

def infer_category(title, keywords, existing):
    """Use classification if exists, else infer from keywords/title."""
    if existing and isinstance(existing, str) and existing.strip():
        cat = existing.strip()
        mapping = {
            'Banking': 'Banca',
            'Pagos': 'Pagos',
            'Préstamos': 'Préstamos',
            'Regulación': 'Regulación',
            'Inversiones': 'Inversiones',
            'Fintech': 'Fintech',
            'Criptoactivos': 'Criptoactivos',
            'IA / tecnología': 'IA / Tecnología',
            'Inclusión financiera': 'Inclusión Financiera',
        }
        return mapping.get(cat, cat)
    
    text = f"{title} {keywords}".lower()
    if any(w in text for w in ['regulación', 'sbs', 'indecopi', 'normativa', 'ley', 'regulador']):
        return 'Regulación'
    if any(w in text for w in ['pago', 'pagos', 'transferencia', 'pasarela']):
        return 'Pagos'
    if any(w in text for w in ['préstamo', 'crédito', 'bnpl', 'deuda', 'financiamiento']):
        return 'Préstamos'
    if any(w in text for w in ['banco', 'bancario', 'banca', 'banking']):
        return 'Banca'
    if any(w in text for w in ['inversión', 'bolsa', 'acciones', 'valores']):
        return 'Inversiones'
    if any(w in text for w in ['fintech', 'startup', 'neobank']):
        return 'Fintech'
    if any(w in text for w in ['cripto', 'bitcoin', 'blockchain', 'token']):
        return 'Criptoactivos'
    if any(w in text for w in ['inteligencia artificial', ' ia ', 'machine learning', 'tecnología']):
        return 'IA / Tecnología'
    if any(w in text for w in ['inclusión', 'acceso', 'bancarización']):
        return 'Inclusión Financiera'
    return 'Otros'

def parse_keywords(kw_str):
    """Parse keywords string into a clean list."""
    if not kw_str or not isinstance(kw_str, str):
        return []
    keywords = [k.strip().rstrip('.') for k in kw_str.split(',')]
    return [k for k in keywords if k and len(k) > 1]

def convert(excel_path):
    df = pd.read_excel(excel_path)
    articles = []
    
    for i, row in df.iterrows():
        fecha = row.get('Fecha')
        if pd.isna(fecha):
            fecha_str = "Fecha no disponible"
            fecha_sort = "1900-01-01"
        else:
            if isinstance(fecha, datetime):
                fecha_str = fecha.strftime('%d %b %Y')
                fecha_sort = fecha.strftime('%Y-%m-%d')
            else:
                fecha_str = str(fecha)
                fecha_sort = str(fecha)
        
        raw_title = str(row.get('Titulo', '')).strip()
        source = extract_source(raw_title, row.get('URL'))
        title = clean_title(raw_title)
        
        url = row.get('URL')
        url = str(url).strip() if pd.notna(url) else None
        
        resumen = row.get('Resumen')
        if pd.notna(resumen):
            resumen = str(resumen).strip().replace('\n', ' ').replace('\r', '')
            # Truncate very long summaries for the card view
            resumen_short = resumen[:280] + '...' if len(resumen) > 280 else resumen
        else:
            resumen = None
            resumen_short = None
        
        img_url = row.get('URL imagen')
        img_url = str(img_url).strip() if pd.notna(img_url) else None
        
        keywords_raw = row.get('Palabras claves')
        keywords = parse_keywords(str(keywords_raw) if pd.notna(keywords_raw) else '')
        
        category = infer_category(
            raw_title,
            str(keywords_raw) if pd.notna(keywords_raw) else '',
            row.get('Clasificación')
        )
        
        articles.append({
            'id': i,
            'title': title,
            'source': source,
            'date': fecha_str,
            'date_sort': fecha_sort,
            'url': url,
            'summary': resumen,
            'summary_short': resumen_short,
            'image_url': img_url,
            'category': category,
            'keywords': keywords,
        })
    
    # Sort by date descending
    articles.sort(key=lambda x: x['date_sort'], reverse=True)
    
    # Extract unique categories and sources
    categories = sorted(set(a['category'] for a in articles))
    sources = sorted(set(a['source'] for a in articles))
    
    output = {
        'generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total': len(articles),
        'categories': categories,
        'sources': sources,
        'articles': articles,
    }
    
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'news.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Converted {len(articles)} articles → {out_path}")
    print(f"  Categories: {', '.join(categories)}")
    print(f"  Sources: {', '.join(sources)}")
    return output

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Sample.xlsx')
    if not os.path.exists(path):
        print(f"Error: File not found: {path}")
        sys.exit(1)
    convert(path)
