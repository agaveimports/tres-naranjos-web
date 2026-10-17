"""Point every link, share card, sitemap and canonical tag at a new domain.

Usage:  python3 tools/set_domain.py https://tresnaranjos.com
Then rebuild:  python3 tools/build_recipes.py && python3 tools/build_tragos.py
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg_path = os.path.join(ROOT, 'tools', 'config.json')
cfg = json.load(open(cfg_path))
old, new = cfg['site_url'].rstrip('/'), sys.argv[1].rstrip('/')
if old == new:
    sys.exit('Already set to ' + new)
changed = 0
for base, _, files in os.walk(ROOT):
    if '/.git' in base:
        continue
    for f in files:
        if f.endswith(('.html', '.xml', '.txt', '.py', '.json')):
            p = os.path.join(base, f)
            s = open(p, encoding='utf-8').read()
            if old in s:
                open(p, 'w', encoding='utf-8').write(s.replace(old, new)); changed += 1
cfg['site_url'] = new
json.dump(cfg, open(cfg_path, 'w'), indent=2)
print(f'{old} -> {new} in {changed} files')
