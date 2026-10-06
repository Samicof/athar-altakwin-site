from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1] / "site"

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.meta = {}
        self.named_meta = {}
        self.html = {}
        self.jsonld = []
        self.in_jsonld = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.html = a
        if tag == "meta" and a.get("property"):
            self.meta[a["property"]] = a.get("content")
        if tag == "meta" and a.get("name"):
            self.named_meta[a["name"]] = a.get("content")
        if tag in ("a", "img", "link"):
            ref = a.get("href") or a.get("src")
            if ref:
                self.refs.append(ref)
        if tag == "script" and a.get("type") == "application/ld+json":
            self.in_jsonld = True

    def handle_data(self, data):
        if self.in_jsonld:
            self.jsonld.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_jsonld = False

for relative, lang, direction in (("index.html", "ar", "rtl"), ("en/index.html", "en", "ltr")):
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    page = Page()
    page.feed(text)
    assert page.html.get("lang") == lang and page.html.get("dir") == direction, relative
    assert page.meta.get("og:site_name") == ("أثر التكوين" if lang == "ar" else "Athar Altakwin"), relative
    assert page.named_meta.get("description"), relative
    assert "تطوير وتجربة" in text if lang == "ar" else "Development &amp; testing" in text
    assert "ATHR" in text, relative
    assert "info@athrtk.com" in text, relative
    assert ("جميع الحقوق محفوظة" if lang == "ar" else "All rights reserved") in text, relative
    organization = json.loads("".join(page.jsonld))
    assert organization["name"] == "Athar Altakwin", relative
    assert organization["address"]["addressLocality"] == "Riyadh", relative
    assert "telephone" not in organization, relative
    for ref in page.refs:
        if ref.startswith(("http:", "https:", "mailto:", "#")):
            continue
        url = urlsplit(ref)
        if not url.path:
            continue
        local = ROOT / url.path.lstrip("/") if url.path.startswith("/") else path.parent / url.path
        if local.is_dir():
            local /= "index.html"
        assert local.is_file(), f"Broken local reference: {relative} -> {ref}"

for relative, lang, direction in (("404.html", "ar", "rtl"), ("en/404.html", "en", "ltr")):
    path = ROOT / relative
    content = path.read_text(encoding="utf-8")
    page = Page()
    page.feed(content)
    assert page.html.get("lang") == lang and page.html.get("dir") == direction, relative
    assert page.named_meta.get("robots") == "noindex", relative
    assert page.named_meta.get("description"), relative
    assert ("جميع الحقوق محفوظة" if lang == "ar" else "All rights reserved") in content
    for ref in page.refs:
        if ref.startswith(("http:", "https:", "mailto:", "#")):
            continue
        url = urlsplit(ref)
        if not url.path:
            continue
        local = ROOT / url.path.lstrip("/") if url.path.startswith("/") else path.parent / url.path
        if local.is_dir():
            local /= "index.html"
        assert local.is_file(), f"Broken local reference: {relative} -> {ref}"

for relative, lang, direction in (("privacy/index.html", "ar", "rtl"), ("en/privacy/index.html", "en", "ltr")):
    path = ROOT / relative
    content = path.read_text(encoding="utf-8")
    page = Page()
    page.feed(content)
    assert page.html.get("lang") == lang and page.html.get("dir") == direction, relative
    assert page.named_meta.get("description") and "Cloudflare" in content
    assert "info@athrtk.com" in content
    for ref in page.refs:
        if ref.startswith(("http:", "https:", "mailto:", "#")):
            continue
        url = urlsplit(ref)
        if not url.path:
            continue
        local = ROOT / url.path.lstrip("/") if url.path.startswith("/") else path.parent / url.path
        if local.is_dir():
            local /= "index.html"
        assert local.is_file(), f"Broken local reference: {relative} -> {ref}"

for filename in ("robots.txt", "sitemap.xml", "assets/athar-icon.svg", "assets/og.png", "assets/athar-pattern-chevron-clean.svg", "assets/athar-pattern-strata-light.svg", "assets/cairo-arabic.woff2", "assets/cairo-latin.woff2", "assets/Cairo-OFL.txt"):
    assert (ROOT / filename).is_file(), filename
assert not (ROOT / "assets" / "athar-pattern-primary-light.svg").exists(), "Flawed source pattern copied to site"
assert not list((ROOT / "assets").glob("plex-*.woff2")), "Outdated font in site"
ET.parse(ROOT / "sitemap.xml")
for private_suffix in (".docx", ".pdf", ".env"):
    assert not list(ROOT.rglob("*" + private_suffix)), private_suffix
public_text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in ROOT.rglob("*") if p.suffix in (".html", ".xml", ".txt", ".css"))
for disallowed_field in ("tel:", '"telephone"', '"streetAddress"', '"postalCode"', '"legalName"'):
    assert disallowed_field not in public_text, disallowed_field
assert not re.search(r"\+966[\s\d-]{7,}", public_text), "Public phone number found"
print("Arabic and English pages, identity, metadata, and local links verified")
