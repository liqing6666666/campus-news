"""HTML scraper for SCUEC 博达 CMS V2.0 news pages."""

import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from cache import cache

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

LIST_CACHE_TTL = 300
ARTICLE_CACHE_TTL = 1800


class ScraperError(Exception):
    pass


def _build_client() -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=30,
        follow_redirects=True,
    )


def _decode(html: bytes) -> str:
    for enc in ("utf-8", "gbk", "gb2312", "gb18030"):
        try:
            return html.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return html.decode("utf-8", errors="replace")


def _parse(html: bytes | str) -> BeautifulSoup:
    text = _decode(html) if isinstance(html, bytes) else html
    return BeautifulSoup(text, "lxml")


def _first_text(soup, selectors: list[str]) -> str:
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            text = el.get_text(strip=True)
            if text:
                return text
    return ""


def _resolve_url(href: str, base_url: str) -> str:
    """Resolve relative URLs against the page base URL."""
    if href.startswith("http"):
        return href
    return urljoin(base_url, href)


def _extract_date(el) -> str:
    """Try to find a date near the element."""
    text = el.get_text(strip=True) if el else ""
    m = re.search(r"(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2})", text)
    if m:
        return m.group(1)
    m = re.search(r"(\d{4}年\d{1,2}月\d{1,2}日)", text)
    if m:
        return m.group(1)
    m = re.search(r"(\d{1,2}[-/\.]\d{1,2})", text)
    if m:
        return m.group(1)
    return ""


def _clean_title(raw: str) -> str:
    """Strip leading dates and noise from title text."""
    t = raw.strip()
    # e.g. "2026-05-19 " or "2026-05-19"
    t = re.sub(r"^\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}\s*", "", t)
    # e.g. "2026年5月19日 "
    t = re.sub(r"^\d{4}年\d{1,2}月\d{1,2}日\s*", "", t)
    # e.g. "05-19 " (MM-DD)
    t = re.sub(r"^\d{1,2}[-/\.]\d{1,2}\s*", "", t)
    # e.g. "192026-05 " (DD concatenated with YYYY-MM, from garbled parsing)
    t = re.sub(r"^\d{1,2}\d{4}[-/\.]\d{1,2}\s*", "", t)
    # Strip trailing dates e.g. "...2026-05-18" at end of title
    t = re.sub(r"\s*\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}\s*$", "", t)
    return t


def _clean_date_text(raw: str) -> str:
    """Extract date from common Chinese date text patterns like '发布时间：2026年05月15日'."""
    t = raw.strip()
    m = re.search(r"(\d{4}[-/\.年]\d{1,2}[-/\.月]\d{1,2})[日]?", t)
    if m:
        return m.group(1).replace("年", "-").replace("月", "-").replace("日", "")
    m = re.search(r"(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2})", t)
    if m:
        return m.group(1)
    m = re.search(r"(\d{1,2}[-/\.]\d{1,2})", t)
    if m:
        return m.group(1)
    return t[:12] if len(t) > 12 else t


def fetch_list_page(url: str, limit: int = 10) -> list[dict]:
    """Fetch and parse a news list page."""
    cache_key = f"list:{url}:{limit}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    client = _build_client()
    try:
        resp = client.get(url)
        if resp.status_code >= 400:
            raise ScraperError(f"HTTP {resp.status_code} from {url}")
        soup = _parse(resp.content)
        items = _extract_list_items(soup, url, limit)
        cache.set(cache_key, items, LIST_CACHE_TTL)
        return items
    except httpx.RequestError as e:
        raise ScraperError(f"Request failed: {e}") from e
    finally:
        client.close()


def _extract_list_items(soup: BeautifulSoup, base_url: str, limit: int) -> list[dict]:
    """Extract news items from a list page using patterns observed on SCUEC."""
    items: list[dict] = []

    # Pattern 1: Main news (xww) — div.lists > li > a > h3
    lists_div = soup.select_one("div.lists")
    if lists_div:
        for li in lists_div.select("li"):
            if len(items) >= limit:
                break
            a = li.select_one("a[href*='info']")
            if not a:
                continue
            href = a.get("href", "")
            if not href:
                continue
            h3 = a.select_one("h3")
            title = _clean_title(h3.get_text(strip=True) if h3 else a.get_text(strip=True))
            if not title or len(title) < 2:
                continue
            date_el = li.select_one(
                "div.date4, div.date3, div.date2, div.date, "
                "span.date, span.time, span.info-right, span.fr, "
                "em, i, font"
            )
            date = _extract_date(date_el) if date_el else ""
            url = _resolve_url(href, base_url)
            if not any(d["url"] == url for d in items):
                items.append({"title": title, "date": date, "url": url})

    # Pattern 2: 教务处 (jwc) — div.news_1 > a > span (title) + span (date)
    if len(items) < limit:
        for cn in soup.select("div.news_1, div.news_2, div.news_3"):
            for a in cn.select("a[href*='info']"):
                if len(items) >= limit:
                    break
                href = a.get("href", "")
                if not href:
                    continue
                spans = a.select("span")
                title = ""
                date = ""
                if len(spans) >= 2:
                    title = _clean_title(spans[0].get_text(strip=True))
                    date = _extract_date(spans[1])
                if not title:
                    title = _clean_title(a.get("title", "") or a.get_text(strip=True))
                if not title or len(title) < 2:
                    continue
                url = _resolve_url(href, base_url)
                if not any(d["url"] == url for d in items):
                    items.append({"title": title, "date": date, "url": url})

    # Pattern 3: Generic — any a[href*=info] in list-like containers
    if len(items) < limit:
        for sel in ("ul.list", "div.list", "div.news-list", "div.right-list",
                     "div.list-right", "div.content", "div.main-con", "div.con"):
            container = soup.select_one(sel)
            if not container:
                continue
            for a in container.select("a[href*='info']"):
                if len(items) >= limit:
                    break
                href = a.get("href", "")
                if not href:
                    continue
                title = _clean_title(a.get("title", "") or a.get_text(strip=True))
                if not title or len(title) < 2:
                    continue
                parent = a.find_parent("li") or a.find_parent("div")
                date = ""
                if parent:
                    for ds in ("span.date", "span.time", "span.info", "em", "i"):
                        d = parent.select_one(ds)
                        if d:
                            date = _extract_date(d)
                            if date:
                                break
                url = _resolve_url(href, base_url)
                if not any(d["url"] == url for d in items):
                    items.append({"title": title, "date": date, "url": url})

    # Pattern 4: Loose fallback — any a[href*=info] anywhere
    if len(items) < limit:
        for a in soup.select("a[href*='info']"):
            if len(items) >= limit:
                break
            href = a.get("href", "")
            if not href:
                continue
            title = _clean_title(a.get("title", "") or a.get_text(strip=True))
            if not title or len(title) < 5:
                continue
            url = _resolve_url(href, base_url)
            if any(d["url"] == url for d in items):
                continue
            parent = a.find_parent("li") or a.find_parent("div")
            date = _extract_date(parent) if parent else ""
            items.append({"title": title, "date": date, "url": url})

    return items


def fetch_article_detail(url: str) -> dict:
    """Fetch and parse an article detail page."""
    cache_key = f"article:{url}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    client = _build_client()
    try:
        resp = client.get(url)
        if resp.status_code >= 400:
            raise ScraperError(f"HTTP {resp.status_code} from {url}")
        soup = _parse(resp.content)

        title = _first_text(soup, [
            "h1", "h2", "h3",
            "div.art-title", "div.article-title",
            "div.title", "div.content-title",
        ])

        date = _first_text(soup, [
            "p.info", "div.info",
            "span.date", "span.time", "span.pubdate",
            "div.article-info span",
            "p.time",
        ])
        if date:
            date = _clean_date_text(date)
        if not date:
            meta = soup.select_one('meta[name="pubdate"], meta[name="publishdate"]')
            if meta:
                date = meta.get("content", "")

        content = _first_text(soup, [
            "div.cont", "div.art-content", "div.article-content",
            "div.content", "div#content",
            "div.entry-content", "div.text",
            "div.article-body", "div.main-content",
        ])

        source = ""
        m = re.search(r"/([a-zA-Z]+)/info/", url)
        if m:
            source = m.group(1)

        result = {
            "title": title,
            "date": date,
            "content": content[:2000] if content else "",
            "source": source,
            "url": url,
        }
        cache.set(cache_key, result, ARTICLE_CACHE_TTL)
        return result
    except httpx.RequestError as e:
        raise ScraperError(f"Request failed: {e}") from e
    finally:
        client.close()
