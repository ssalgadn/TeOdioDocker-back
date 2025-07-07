import re
import unicodedata

def sanitize_filename(filename: str) -> str:
    filename = filename.replace('\n', ' ').replace('\r', ' ')
    filename = unicodedata.normalize('NFD', filename)
    filename = ''.join(c for c in filename if unicodedata.category(c) != 'Mn')
    
    replacements = {
        '–': '-',
        '—': '-',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '…': '...',
        '&': 'and',
        '/': '_',
        '\\': '_',
        ':': '_',
        '*': '_',
        '?': '_',
        '<': '_',
        '>': '_',
        '|': '_',
        '(': '',
        ')': '',
        '[': '',
        ']': '',
        '{': '',
        '}': '',
    }
    
    for old, new in replacements.items():
        filename = filename.replace(old, new)
    
    filename = ''.join(c for c in filename if ord(c) < 128)
    filename = re.sub(r'\s+', '_', filename.strip())
    filename = re.sub(r'_+', '_', filename)
    filename = filename.strip('_')
    filename = filename.lower()
    
    if not filename:
        filename = "unnamed_product"
    
    return filename
