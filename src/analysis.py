import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup

SEC_BASE = "https://www.sec.gov"
USER_AGENT = "Mozilla/5.0 (compatible; EarningsAgent/1.0; +https://github.com/ZachG303/my_second_agent)"

DEFAULT_FILINGS = ["8-K", "10-Q", "10-K"]
DEFAULT_THEMES = {
    "AI": ["ai", "artificial intelligence", "machine learning", "edge ai", "datacenter", "xpu"],
    "Telecom": ["telecom", "ethernet", "network", "5g", "fiber"],
    "Security": ["fraud", "security", "cyber", "identity", "threat"],
    "Semiconductor": ["silicon", "chip", "semiconductor", "fab", "wafer"],
    "Defense": ["defense", "defence", "military", "aerospace"],
    "Reshoring": ["reshoring", "onshoring", "supply chain", "domestic manufacturing"],
    "Cloud": ["cloud", "hyperscale", "gpu", "accelerator"],
}
PARTNER_TERMS = [
    "broadcom", "avgo", "openai", "chips act", "intel", "nvidia", "meta", "aws", "microsoft",
]
NARRATIVE_KEYWORDS = [
    "ai", "datacenter", "edge", "platform", "ecosystem", "reshoring", "chips act", "fraud", "telecom",
]


def _fetch_url(url: str, timeout: int = 15) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="ignore")
    except (HTTPError, URLError) as exc:
        raise ConnectionError(f"Failed to fetch {url}: {exc}")


def _get_cik_for_ticker(ticker: str) -> str:
    search_url = f"{SEC_BASE}/cgi-bin/browse-edgar?CIK={ticker}&owner=exclude&count=40&action=getcompany"
    html = _fetch_url(search_url)
    soup = BeautifulSoup(html, "html.parser")
    company_span = soup.select_one("span.companyName")
    if company_span:
        match = re.search(r"CIK#:\s*0*([0-9]+)", company_span.text)
        if match:
            return match.group(1)
    match = re.search(r"CIK=(\d+)", html)
    if match:
        return match.group(1).lstrip("0")
    return ticker


def _extract_text_from_filing(url: str) -> str:
    html = _fetch_url(url)
    soup = BeautifulSoup(html, "html.parser")
    candidates = []
    for link in soup.select("table.tableFile td a"):
        href = link.get("href")
        if not href:
            continue
        if href.endswith(".txt") or href.endswith(".htm") or href.endswith(".html"):
            candidates.append(urljoin(SEC_BASE, href))
    if not candidates:
        return soup.get_text(separator=" ").strip()
    document_url = candidates[0]
    text = _fetch_url(document_url)
    if text.lstrip().startswith("<"):
        return BeautifulSoup(text, "html.parser").get_text(separator=" ").strip()
    return text.strip()


def scrape_sec_filings(ticker: str, filing_types: Optional[List[str]] = None, limit: int = 4) -> List[Dict[str, Any]]:
    filing_types = filing_types or DEFAULT_FILINGS
    cik = _get_cik_for_ticker(ticker)
    page_url = f"{SEC_BASE}/cgi-bin/browse-edgar?CIK={cik}&owner=exclude&count=100&action=getcompany"
    html = _fetch_url(page_url)
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="tableFile2")
    filings = []

    if not table:
        return filings

    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) < 5:
            continue

        filing_type = cols[0].get_text(strip=True)
        if filing_type not in filing_types:
            continue

        filing_date = cols[3].get_text(strip=True)
        filing_link = cols[1].find("a")
        if not filing_link:
            continue

        filing_detail_url = urljoin(SEC_BASE, filing_link["href"])
        try:
            filing_text = _extract_text_from_filing(filing_detail_url)
        except ConnectionError:
            filing_text = ""

        filings.append({
            "type": filing_type,
            "date": filing_date,
            "url": filing_detail_url,
            "text": filing_text,
        })

        if len(filings) >= limit:
            break

        time.sleep(0.8)

    return filings


def _match_themes(text: str) -> List[str]:
    lower = text.lower()
    tags = []
    for theme, keywords in DEFAULT_THEMES.items():
        if any(keyword in lower for keyword in keywords):
            tags.append(theme)
    return tags


def _has_narrative_shift(filings: List[Dict[str, Any]]) -> bool:
    if len(filings) < 2:
        return False
    latest = filings[0]["text"].lower()
    earlier = " ".join([f["text"].lower() for f in filings[1:]])
    latest_matches = [kw for kw in NARRATIVE_KEYWORDS if kw in latest]
    earlier_matches = [kw for kw in NARRATIVE_KEYWORDS if kw in earlier]
    return bool(set(latest_matches) - set(earlier_matches))


def _compute_technical_signals(ticker: str) -> Dict[str, Any]:
    output = {"technical_confirmed": False, "technical_snippet": ""}
    try:
        stock = yf.Ticker(ticker)
        weekly = stock.history(period="5y", interval="1wk")
        if weekly.empty:
            return output
        weekly = weekly.dropna(subset=["Close"])
        weekly["ma_200_week"] = weekly["Close"].rolling(200).mean()
        weekly["sma_20_month"] = weekly["Close"].rolling(80).mean()
        latest_close = float(weekly["Close"].iloc[-1])
        ma_200 = float(weekly["ma_200_week"].iloc[-1]) if not pd.isna(weekly["ma_200_week"].iloc[-1]) else None
        sma_20m = float(weekly["sma_20_month"].iloc[-1]) if not pd.isna(weekly["sma_20_month"].iloc[-1]) else None
        if ma_200 and sma_20m:
            output["technical_confirmed"] = latest_close >= ma_200 or latest_close >= sma_20m
            output["technical_snippet"] = (
                f"Price ${latest_close:.2f} vs 200-week MA ${ma_200:.2f}, 20-month SMA ${sma_20m:.2f}."
            )
    except Exception:
        output["technical_confirmed"] = False
    return output


def analyze_inflection(ticker: str, filing_limit: int = 4) -> Dict[str, Any]:
    ticker = ticker.upper()
    stock = yf.Ticker(ticker)
    info = getattr(stock, "info", {}) or {}
    history = stock.history(period="1mo")

    price = float(history["Close"].iloc[-1]) if not history.empty else 0.0
    revenue = float(info.get("totalRevenue") or 0.0)
    market_cap = float(info.get("marketCap") or 0.0)
    ps_ratio = float(info.get("priceToSalesTrailing12Months") or 0.0)
    peg_metric = float(info.get("pegRatio") or info.get("forwardPEG") or 0.0)

    filings = scrape_sec_filings(ticker, limit=filing_limit)
    filing_descriptions = [f"{f['type']} {f['date']}" for f in filings]
    combined_text = " ".join([f["text"] for f in filings])
    theme_tags = _match_themes(combined_text)

    narrative_shift = _has_narrative_shift(filings)
    cheap_on_sales = 1.0 <= ps_ratio <= 1.6
    multi_theme_exposure = len(theme_tags) >= 2
    ecosystem_halo = any(partner in combined_text.lower() for partner in PARTNER_TERMS)
    peg_value_flag = peg_metric > 0 and peg_metric < 1
    technical = _compute_technical_signals(ticker)

    score = sum([
        int(narrative_shift),
        int(cheap_on_sales),
        int(multi_theme_exposure),
        int(ecosystem_halo),
        int(peg_value_flag),
        int(technical["technical_confirmed"]),
    ])

    highlights = []
    if narrative_shift:
        highlights.append("Narrative shift detected in recent filings/transcripts.")
    if cheap_on_sales:
        highlights.append(f"Attractive P/S ratio of {ps_ratio:.2f}.")
    if multi_theme_exposure:
        highlights.append(f"Multi-theme exposure through {', '.join(theme_tags)}.")
    if ecosystem_halo:
        highlights.append("Ecosystem halo is present in filings or commentary.")
    if peg_value_flag:
        highlights.append(f"PEG below 1 at {peg_metric:.2f} indicates growth-at-value potential.")
    if technical["technical_confirmed"]:
        highlights.append("Technical structure supports the thesis.")

    summary = (
        f"{ticker} has a score of {score}/6. "
        f"Latest filings: {', '.join(filing_descriptions) or 'none'}.")

    return {
        "company_ticker": ticker,
        "latest_filing_date": filings[0]["date"] if filings else None,
        "price": price,
        "sales_multiple": ps_ratio if ps_ratio > 0 else None,
        "peg": peg_metric if peg_metric > 0 else None,
        "narrative_shift": narrative_shift,
        "cheap_on_sales": cheap_on_sales,
        "multi_theme_exposure": multi_theme_exposure,
        "ecosystem_halo": ecosystem_halo,
        "peg_value": peg_value_flag,
        "technical_confirmed": technical["technical_confirmed"],
        "score": score,
        "theme_tags": theme_tags,
        "highlights": highlights,
        "latest_filings": filing_descriptions,
        "summary": summary,
    }


def get_recent_inflection_insights(ticker: str, limit: int = 4) -> Dict[str, Any]:
    return analyze_inflection(ticker, filing_limit=limit)
