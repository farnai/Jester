"""Offline documentation checks; not a full Markdown linter or runtime audit.

Checks UTF-8/control characters, balanced fenced blocks, ATX heading spacing,
local inline/reference link paths and Markdown heading fragments. Code fences
and inline code are excluded from link extraction. External URLs are not fetched.
Default scope: active docs, root guides and Visual Studio guides (not experiments).
Pass repository-relative Markdown paths to check a smaller set.
"""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import subprocess
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]


def prose(text):
    lines = []
    fence = None
    errors = []
    for number, line in enumerate(text.split('\n'), 1):
        match = re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$', line)
        if match:
            marker, tail = match.groups()
            if fence is None:
                fence = (marker[0], len(marker), number)
            elif marker[0] == fence[0] and len(marker) >= fence[1] and not tail.strip():
                fence = None
            lines.append('')
            continue
        lines.append('' if fence else line)
        if not fence and re.match(r'^#{1,6}[^#\s]', line):
            errors.append((number, 'Markdown: missing space after heading marker'))
        if any(ord(c) < 32 and c not in '\t\r' for c in line):
            errors.append((number, 'Markdown: unexpected control character'))
    if fence:
        errors.append((fence[2], 'Markdown: unclosed fenced block'))
    return '\n'.join(lines), errors


def anchors(text):
    body, _ = prose(text)
    found = set(re.findall(r'<(?:a|\w+)\s+[^>]*(?:id|name)=["\']([^"\']+)', body))
    counts = {}
    for line in body.splitlines():
        match = re.match(r'^\s{0,3}#{1,6}\s+(.+?)(?:\s+#+)?\s*$', line)
        if not match:
            continue
        value = re.sub(r'<[^>]*>', '', match[1]).lower()
        value = re.sub(r'\[([^]]+)\]\([^)]*\)', r'\1', value)
        slug = ''.join(c for c in value if c in ' _-' or unicodedata.category(c)[0] in 'LN').replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        found.add(slug if count == 0 else f'{slug}-{count}')
    return found


def check(path):
    text = path.read_text(encoding='utf-8')
    body, errors = prose(text)
    # Replace code spans with spaces so line numbers remain stable.
    body = re.sub(r'(`+)(.*?)\1', lambda m: ' ' * len(m[0]), body)
    targets = []
    definitions = {}
    for match in re.finditer(r'^\s{0,3}\[([^]]+)\]:\s*(<[^>]+>|\S+)', body, re.M):
        definitions[match[1].casefold()] = match[2].strip('<>')
        targets.append((match.start(), match[2].strip('<>')))
    for match in re.finditer(r'!?\[[^]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+["\'][^\n]*["\'])?\s*\)', body):
        targets.append((match.start(), match[1].strip('<>')))
    for match in re.finditer(r'\[([^]\n]+)\]\[([^]\n]*)\]', body):
        key = (match[2] or match[1]).casefold()
        if key not in definitions:
            errors.append((body[:match.start()].count('\n') + 1, f'Link: undefined reference {key}'))
    for offset, target in targets:
        line = body[:offset].count('\n') + 1
        url = urlsplit(target)
        if url.scheme or url.netloc:
            continue
        local = unquote(url.path)
        dest = (ROOT / local.lstrip('/') if local.startswith('/') else path.parent / local) if local else path
        if not dest.exists():
            errors.append((line, f'Link: missing path {target}'))
        elif url.fragment and dest.suffix.lower() == '.md':
            fragment = unquote(url.fragment)
            if fragment not in anchors(dest.read_text(encoding='utf-8')):
                errors.append((line, f'Link: missing heading fragment {target}'))
    return errors


def main():
    if sys.argv[1:]:
        paths = [ROOT / name for name in sys.argv[1:]]
    else:
        tracked = subprocess.check_output(['git', 'ls-files', '*.md'], cwd=ROOT, text=True).splitlines()
        paths = [ROOT / name for name in tracked if (
            (name.startswith('docs/') and not name.startswith('docs/archive/'))
            or '/' not in name
            or (name.startswith('design/visual-studio/') and '/experiments/' not in name)
        )]
    findings = []
    for path in paths:
        for line, message in check(path):
            findings.append({'file': path.relative_to(ROOT).as_posix(), 'line': line, 'message': message})
    print(json.dumps({'files_checked': len(paths), 'findings': findings,
                      'scope': 'Offline structural Markdown and local links; external URLs, inline-code path references and semantic correctness require separate review.'}, ensure_ascii=False, indent=2))
    return bool(findings)


if __name__ == '__main__':
    raise SystemExit(main())
