import json
from pathlib import Path
import re

# Load content_corpus.json
corpus_path = Path("backend/app/interpretation/data/content_corpus.json")
with open(corpus_path, "r", encoding="utf-8") as f:
    corpus = json.load(f)

print(f"Total assets in content_corpus.json: {len(corpus)}")

self_assets = [a for a in corpus if a.get("context") == "self"]
print(f"Total self assets in content_corpus.json: {len(self_assets)}")

# Check for any Mars mentions or Mars interpretation_id in self assets
mars_id_assets = [a for a in self_assets if "mars" in a.get("interpretation_id", "").lower()]
print(f"Self assets with 'mars' in interpretation_id: {len(mars_id_assets)}")

# Also check relationship assets for Mars
rel_assets = [a for a in corpus if a.get("context") == "relationship"]
rel_mars_assets = [a for a in rel_assets if "mars" in a.get("interpretation_id", "").lower() or any("mars" in t.lower() for t in a.get("tags", []))]
print(f"Relationship assets mentioning mars: {len(rel_mars_assets)}")

# Conceptual search in self assets for action/assertion keywords
keywords = [
    r"\bmars\b", r"მარს", r"მოქმედებ", r"ინიციატივ", r"კონფლიქტ", r"დაპირისპირებ",
    r"ბრძოლ", r"შეჯიბრ", r"კონკურენცი", r"სიჯიუტ", r"აგრესი", r"მიზანდასახულ",
    r"წინააღმდეგობ", r"დაბრკოლებ", r"ენერგი", r"სიჩქარ", r"ტემპ"
]

matching_self = []
for a in self_assets:
    txt = a.get("text", "")
    interp = a.get("interpretation_id", "")
    matches = [kw for kw in keywords if re.search(kw, txt, re.IGNORECASE)]
    if matches:
        matching_self.append((a, matches))

print(f"Self assets matching action/drive/confrontation keywords: {len(matching_self)}")

# Group matching by interpretation_id prefix
by_interp = {}
for a, m in matching_self:
    iid = a.get("interpretation_id", "unknown")
    prefix = ".".join(iid.split(".")[:2]) if "." in iid else iid
    by_interp[prefix] = by_interp.get(prefix, 0) + 1

for prefix, count in sorted(by_interp.items(), key=lambda x: -x[1]):
    print(f"  {prefix}: {count}")
