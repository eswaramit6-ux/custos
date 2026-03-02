import re

content = open('utils/ocr_extractor.py').read()

# Add debited from removal after the existing clean lines
old = "    # Remove long transaction IDs like T260207213420097853303\n    clean_text = re.sub(r'\\b[A-Z][A-Z0-9]{10,}\\b', '', clean_text)"

new = """    # Remove long transaction IDs like T260207213420097853303
    clean_text = re.sub(r'\\b[A-Z][A-Z0-9]{10,}\\b', '', clean_text)
    # Remove Debited from section - avoids picking account balance as amount
    debited_idx = clean_text.lower().find('debited from')
    if debited_idx != -1:
        clean_text = clean_text[:debited_idx]
    # Remove UTR lines
    utr_idx = clean_text.lower().find('utr:')
    if utr_idx != -1:
        clean_text = clean_text[:utr_idx]"""

content = content.replace(old, new)
open('utils/ocr_extractor.py', 'w').write(content)
print('Has debited fix:', 'debited from' in content.lower())
