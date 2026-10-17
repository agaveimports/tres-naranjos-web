"""Change the WhatsApp number and/or the contact email everywhere on the site.

Usage:
  python3 tools/set_contact.py --whatsapp 17875551234     (1 + area code + number, digits only)
  python3 tools/set_contact.py --email ventas@ejemplo.com
"""
import argparse, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg_path = os.path.join(ROOT, 'tools', 'config.json'); cfg = json.load(open(cfg_path))
ap = argparse.ArgumentParser(); ap.add_argument('--whatsapp'); ap.add_argument('--email'); a = ap.parse_args()
swaps = []
if a.whatsapp: swaps.append((f"const WHATSAPP = '{cfg['whatsapp']}'", f"const WHATSAPP = '{a.whatsapp}'")); cfg['whatsapp'] = a.whatsapp
if a.email: swaps.append((cfg['email'], a.email)); cfg['email'] = a.email
n = 0
for base, _, files in os.walk(ROOT):
    if '/.git' in base:
        continue
    for f in files:
        if f.endswith(('.html', '.py')) and f != 'set_contact.py':
            p = os.path.join(base, f); s = o = open(p, encoding='utf-8').read()
            for old, new in swaps: s = s.replace(old, new)
            if s != o: open(p, 'w', encoding='utf-8').write(s); n += 1
json.dump(cfg, open(cfg_path, 'w'), indent=2)
print('updated', n, 'files')
