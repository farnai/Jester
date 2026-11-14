import os
import glob
import re

files = [f.replace('\\', '/') for f in glob.glob('frontend/src/**/*', recursive=True) if os.path.isfile(f) and f.endswith(('.tsx', '.ts', '.css'))]

dev_keywords = ['smoke_test', 'visual-lab', 'ui/VisualLab', 'inspector', 'BackendAuditDebugPage', 'DebugBar', 'shared/runtime', '__tests__']

def categorize(path):
    if any(k in path for k in dev_keywords):
        return 'B_DEV'
    if 'homeEditorial.css' in path or 'social-profile.css' in path:
        return 'C_UNUSED'
    return 'A_ACTIVE'

hex_re = re.compile(r'#(?:[0-9a-fA-F]{3,4}){1,2}\b')
rgb_re = re.compile(r'rgba?\([^\)]+\)')
hsl_re = re.compile(r'hsla?\([^\)]+\)')

results = {'A_ACTIVE': {}, 'B_DEV': {}, 'C_UNUSED': {}}

for f in files:
    if f.endswith('colors.css'):
        continue
    cat = categorize(f)
    with open(f, 'r', encoding='utf-8') as fl:
        text = fl.read()
    
    lines = text.splitlines()
    naked_hex = []
    naked_rgb = []
    fallback_colors = []
    
    for i, line in enumerate(lines, 1):
        # Find fallbacks
        var_matches = re.findall(r'var\(--[^,)]+,\s*([^)]+)\)', line)
        for fb in var_matches:
            fallback_colors.append((i, fb.strip()))
        
        # Remove var(...) calls from line to find naked colors
        stripped_line = re.sub(r'var\([^)]+\)', '', line)
        
        # Also remove comments
        stripped_line = re.sub(r'/\*.*?\*/', '', stripped_line)
        if stripped_line.strip().startswith('//') or stripped_line.strip().startswith('*'):
            continue
            
        h = hex_re.findall(stripped_line)
        r = rgb_re.findall(stripped_line)
        if h:
            naked_hex.append((i, h, line.strip()))
        if r:
            naked_rgb.append((i, r, line.strip()))
            
    if naked_hex or naked_rgb:
        results[cat][f] = {
            'naked_hex': naked_hex,
            'naked_rgb': naked_rgb,
            'fallback_count': len(fallback_colors)
        }

print('=== Category A (ACTIVE USER UI with naked colors) ===')
for f, data in results['A_ACTIVE'].items():
    print(f"{f}: hex lines={len(data['naked_hex'])}, rgb lines={len(data['naked_rgb'])}")

print('\n=== Category B (DEV/EXPERIMENTAL with naked colors) ===')
for f in results['B_DEV']:
    print(f)

print('\n=== Category C (UNUSED with naked colors) ===')
for f in results['C_UNUSED']:
    print(f)

