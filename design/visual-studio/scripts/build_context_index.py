#!/usr/bin/env python3
"""Build a *manifest*, not a hallucinated design brief, for this repository.

Safe by default: scans local filenames and Markdown headings only; does not upload files.
Run from any cwd: python design/visual-studio/scripts/build_context_index.py
"""
from pathlib import Path
import hashlib
import re
import os

SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[3]
OUT = ROOT / 'design/visual-studio/CONTEXT_INDEX.md'
EXCLUDE = {'.git', 'node_modules', '.next', 'dist', 'build', '.venv', '__pycache__', '.turbo', 'coverage', 'vendor'}
DOC_HINTS = re.compile(r'jester|product|strateg|market|brand|design|visual|typograph|color|palette|token|foundation|explor|ux|ui|architecture|agents|readme|gemini', re.I)
UI_HINTS = re.compile(r'token|theme|color|typograph|global\.css|tailwind\.config', re.I)
records=[]
for dirpath, dirs, names in os.walk(ROOT):
    directory=Path(dirpath)
    dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.startswith('.') or d in {'.agents', '.gemini'}]
    # Don't recursively index this kit's own generated artifacts.
    if directory == ROOT / 'design/visual-studio':
        dirs[:] = []
        continue
    for name in names:
        path=directory/name
        try:
            rel=path.relative_to(ROOT)
        except ValueError:
            continue
        if any(part.startswith('.') and part not in {'.agents','.gemini'} for part in rel.parts[:-1]):
            continue
        is_md=path.suffix.lower() in {'.md', '.mdx'}
        include=(is_md and (len(rel.parts)<=2 or DOC_HINTS.search(str(rel)))) or (path.suffix.lower() in {'.css','.scss','.ts','.tsx','.json'} and UI_HINTS.search(name))
        if not include or path.stat().st_size > 1_500_000:
            continue
        blob=path.read_bytes()
        headings=[]
        if is_md:
            content=blob.decode('utf-8',errors='replace')
            headings=[re.sub(r'[|`]', ' ', line.strip())[:110] for line in content.splitlines() if line.lstrip().startswith('#')][:8]
        records.append((rel.as_posix(), len(blob), hashlib.sha256(blob).hexdigest()[:12], headings))
records.sort(key=lambda x:x[0].lower())
lines=[
    '# Jester local context index',
    '',
    'Auto-generated: paths, sizes, content fingerprints and up to eight headings only. This is NOT a source summary.',
    'Read each relevant original file before drawing conclusions or changing design. Refresh if source changes.',
    '',
    f'Found {len(records)} candidate files in this repo.',
    '',
    '| File | Bytes | SHA-256 prefix |', '|---|---:|---|'
]
for rel,size,sha,headings in records[:250]:
    lines.append(f'| `{rel}` | {size} | `{sha}` |')
    for h in headings:
        lines.append(f'  - {h}')
if len(records)>250:
    lines.append(f'\nOnly first 250 of {len(records)} candidates are listed. Narrow selection manually.')
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'Wrote {OUT} with {min(len(records),250)} candidate paths.')
