#!/usr/bin/env python3
"""Collecte les flux RSS/Atom définis dans sources.json et publie data/veille.json."""
import hashlib, json, re, html
from datetime import datetime, timezone
from pathlib import Path
from email.utils import parsedate_to_datetime
import feedparser
import requests

ROOT = Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT / "sources.json"
OUTPUT_FILE = ROOT / "data" / "veille.json"
MAX_PER_FEED = 80
TIMEOUT = 20
HEADERS = {"User-Agent": "CyberPulseVeille/2.0 (+GitHub Actions RSS aggregator)"}

def clean(value):
    value = html.unescape(re.sub(r"<[^>]+>", " ", str(value or "")))
    return re.sub(r"\s+", " ", value).strip()

def parse_date(entry):
    for key in ("published", "updated", "created"):
        value = entry.get(key)
        if value:
            try:
                dt = parsedate_to_datetime(value)
                if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc).isoformat()
            except Exception:
                pass
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if value:
            try: return datetime(*value[:6], tzinfo=timezone.utc).isoformat()
            except Exception: pass
    return datetime.now(timezone.utc).date().isoformat()

def classify(title, summary, default):
    text = (title + " " + summary).lower()
    if re.search(r"data breach|data leak|fuite de données|données exposées|exfiltration|leaked database|ransomware.*data", text): return "fuite"
    if re.search(r"\bcve-\d{4}-\d+|vulnerability|vulnérabilit|security advisory|zero.day|known exploited", text): return "cve"
    if re.search(r"phishing|hameçonnage|smishing|fraud campaign|fraude", text): return "phishing"
    if re.search(r"cyberattack|cyberattaque|incident|ransomware|rançongiciel|compromise|compromission|alert", text): return "alerte"
    return default or "actualite"

def severity(title, summary):
    text = (title + " " + summary).lower()
    if re.search(r"critical|critique|actively exploited|exploitation active|zero.day|urgent", text): return "Critique"
    if re.search(r"high severity|important|ransomware|massive leak|fuite massive", text): return "Haute"
    if re.search(r"medium|moderate|moyenne|modéré", text): return "Moyenne"
    return "Faible"

def main():
    sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    results, failures, ok = [], [], 0
    for source in sources:
        if not source.get("enabled", True): continue
        name, url = source.get("name", "Flux RSS"), source.get("url", "")
        if not url.startswith(("https://", "http://")):
            failures.append({"source": name, "error": "URL HTTP(S) invalide"}); continue
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            parsed = feedparser.parse(response.content)
            if parsed.bozo and not parsed.entries:
                raise ValueError(str(getattr(parsed, "bozo_exception", "Flux RSS illisible")))
            ok += 1
            for entry in parsed.entries[:MAX_PER_FEED]:
                title = clean(entry.get("title"))
                link = entry.get("link", "")
                if not title or not link.startswith(("https://", "http://")): continue
                summary = clean(entry.get("summary", entry.get("description", "")))[:1800]
                published = parse_date(entry)
                key = hashlib.sha256((link or title).encode("utf-8")).hexdigest()[:20]
                results.append({"id": key, "title": title, "url": link, "source": name,
                    "date": published[:10], "published": published, "desc": summary,
                    "type": classify(title, summary, source.get("category", "actualite")),
                    "sev": severity(title, summary), "category": source.get("category", "actualite")})
        except Exception as exc:
            failures.append({"source": name, "error": str(exc)[:250]})
            print(f"[ERREUR] {name}: {exc}")
    # Deduplication by canonical URL/id and sort by date descending.
    unique = {}
    for item in results: unique[item["id"]] = item
    items = sorted(unique.values(), key=lambda x: x.get("published", ""), reverse=True)[:1200]
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "sources_total": sum(1 for s in sources if s.get("enabled", True)),
               "sources_ok": ok, "sources_failed": len(failures), "errors": failures, "items": items}
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"CyberPulse : {len(items)} articles ; {ok} flux récupérés ; {len(failures)} erreur(s).")
    if not items and ok == 0: raise SystemExit("Aucun flux n'a pu être récupéré : le workflow échoue pour rendre l'incident visible.")

if __name__ == "__main__": main()
