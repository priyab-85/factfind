#!/usr/bin/env python3
"""Parse Instacart receipt emails into a per-item purchase history.

Input:  the JSON blobs the Gmail MCP tool spills to disk when a thread's
        FULL_CONTENT response is too large to return inline.
Output: aggregate.json — one record per normalized item, with order count,
        quantities, prices, stores and dates.

The item detail exists ONLY in the HTML part of these emails; the plain-text
part carries just a total and a receipt link. So we strip tags off html_body
and read the "Items found (<Store>)" block.
"""

import glob
import html
import json
import os
import re
import sys
from collections import Counter, defaultdict

TOOL_RESULTS = os.path.expanduser(
    "~/.claude/projects/-home-user/cc34d67f-239d-5b32-b2aa-b987ecb636f3/tool-results"
)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aggregate.json")

# "Banza Chickpea Rotini (8 oz) 1 x $4.39"  ->  name, size, qty, unit price
ITEM_RE = re.compile(
    r"(?P<name>[^$]{3,160}?)\s*\((?P<size>[^)]{1,40})\)\s*"
    # Weight-priced goods read "1.58 lb x $0.79"; unit-priced ones "1 x $4.39".
    r"(?P<qty>\d+(?:\.\d+)?)\s*(?P<unit>lb|oz|kg|g|ct|each)?\s*x\s*"
    r"\$(?P<price>\d+(?:\.\d+)?)"
)
# Each item block is terminated by this; splitting on it stops the previous
# item's total from bleeding into the next item's name.
ITEM_SPLIT_RE = re.compile(r"Final item price:\s*\$\d+(?:\.\d+)?")
STORE_RE = re.compile(r"Items found \(([^)]+)\)")
ORDER_DATE_RE = re.compile(
    r"placed on ([A-Z][a-z]+ \d{1,2}(?:st|nd|rd|th)?,? \d{4})"
)

# Aisle headers Instacart injects between items; never products themselves.
# Stripped from the FRONT of a name (that is where they appear).
CATEGORY_WORDS = {
    "special request", "dry goods & pasta", "produce", "dairy & eggs",
    "beverages", "frozen", "meat & seafood", "bakery", "pantry",
    "snacks", "household", "personal care", "canned goods & soups",
    "breakfast", "cleaning products", "baby", "health & medicine",
    "alcohol", "deli", "condiments", "items found", "adjustments",
    "bread", "cheese", "yogurt", "eggs", "milk", "juice", "coffee & tea",
    "paper goods", "laundry", "cleaning supplies", "spices & seasonings",
    "baking", "oils & vinegars", "rice & grains", "cereal", "soup",
    "candy & chocolate", "chips & pretzels", "crackers", "nuts & seeds",
    "dried fruit", "seafood", "poultry", "beef", "pork", "prepared foods",
    "flowers", "thanksgiving", "holiday", "sauces", "pasta & rice",
    "beverages & water", "water", "soda", "kitchen supplies", "pet care",
    "vitamins & supplements", "beauty", "oral care", "hair care",
    "international foods", "organic", "gluten free", "vegan",
    "fruits", "vegetables", "herbs", "salad", "refrigerated",
    "canned & packaged", "condiments & sauces", "breakfast & cereal",
    "snacks & candy", "meat", "wine", "beer", "baby food", "diapers",
}

# Boilerplate that can look like a product line but isn't.
NOISE = re.compile(
    r"final item price|order total|subtotal|service fee|bag fee|"
    r"delivery|tip|tax|total charged|original charge|instacart|"
    r"regulatory|authorized|refund|credit|promotion|discount",
    re.I,
)


def strip_html(raw: str) -> str:
    txt = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    txt = txt.replace(" ", " ")
    # Instacart pads some product names with zero-width spaces.
    txt = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", txt)
    return re.sub(r"\s+", " ", txt)


def strip_category_prefix(n: str) -> str:
    """Aisle headers run into the product name: 'Produce Blueberries'."""
    changed = True
    while changed:
        changed = False
        low = n.lower()
        for cat in sorted(CATEGORY_WORDS, key=len, reverse=True):
            if low.startswith(cat + " "):
                n = n[len(cat) :].strip(" -·•,")
                changed = True
                break
    return n


def normalize(name: str) -> str:
    """Collapse trivial variants so the same product aggregates together."""
    n = name.strip().strip("-·•,").strip()
    # Leading money/qty fragments left over from the previous item block.
    n = re.sub(r"^\$?\d+(?:\.\d+)?\s*", "", n)
    n = re.sub(r"^(?:\d+\s*x\s*)", "", n, flags=re.I)
    n = strip_category_prefix(n)
    n = re.sub(r"\s+", " ", n)
    return n.strip(" -·•,")


def dedup_key(name: str) -> str:
    """Word-order- and punctuation-insensitive key.

    'Chobani Nonfat Plain Greek Yogurt' and 'Chobani Plain Nonfat Greek
    Yogurt' are the same product typed two ways; sorted tokens merge them.
    """
    toks = re.findall(r"[a-z0-9]+", name.lower())
    return " ".join(sorted(toks))


def clean_name(name: str) -> str | None:
    n = normalize(name)
    if len(n) < 3 or NOISE.search(n):
        return None
    if n.lower() in CATEGORY_WORDS:
        return None
    if not re.search(r"[A-Za-z]{3}", n):
        return None
    return n


def parse_file(path: str):
    """Yield (message_id, date, store, order_date, [items]) per message."""
    try:
        with open(path) as fh:
            data = json.load(fh)
    except (ValueError, OSError):
        return

    for msg in data.get("messages", []):
        raw = msg.get("htmlBody") or ""
        if "Items found" not in raw and "Items found" not in (
            msg.get("plaintextBody") or ""
        ):
            continue
        text = strip_html(raw)
        if "Items found" not in text:
            continue

        store_m = STORE_RE.search(text)
        store = store_m.group(1).strip() if store_m else "Unknown"

        date_m = ORDER_DATE_RE.search(text)
        order_date = date_m.group(1) if date_m else msg.get("date", "")[:10]

        # Only the items region: from "Items found" up to the totals block.
        start = text.find("Items found")
        end = text.find("Order Totals", start)
        region = text[start : end if end > start else start + 6000]
        # Drop the "Items found (Wegmans) 10" header so it doesn't run into
        # the first product's name.
        region = re.sub(r"^Items found \([^)]+\)\s*\d+\s*", "", region)

        items = []
        for block in ITEM_SPLIT_RE.split(region):
            # One item per block. Take the FIRST match — a later one starts
            # mid-name and truncates it ("Growing Years" -> "wing Years").
            # Leading prices and aisle headers are stripped in normalize().
            m = ITEM_RE.search(block)
            if not m:
                continue
            name = clean_name(m.group("name"))
            if not name:
                continue
            items.append(
                {
                    "name": name,
                    "size": m.group("size").strip(),
                    "qty": float(m.group("qty")),
                    "price": float(m.group("price")),
                }
            )

        yield msg.get("id"), msg.get("date", ""), store, order_date, items


def main():
    files = sorted(glob.glob(os.path.join(TOOL_RESULTS, "*get_thread*.txt")))
    if not files:
        sys.exit(f"no tool-result files under {TOOL_RESULTS}")

    seen_msgs = set()
    agg = defaultdict(
        lambda: {
            "name_votes": Counter(),
            "sizes": set(),
            "orders": 0,
            "total_qty": 0.0,
            "prices": [],
            "stores": set(),
            "dates": [],
        }
    )
    receipts = 0

    for path in files:
        for msg_id, date, store, order_date, items in parse_file(path):
            if not items or msg_id in seen_msgs:
                continue
            seen_msgs.add(msg_id)
            receipts += 1
            for it in items:
                key = dedup_key(it["name"])
                rec = agg[key]
                rec["name_votes"][it["name"]] += 1
                rec["sizes"].add(it["size"])
                rec["orders"] += 1
                rec["total_qty"] += it["qty"]
                rec["prices"].append(it["price"])
                rec["stores"].add(store)
                rec["dates"].append(date[:10])

    out = []
    for key, rec in agg.items():
        prices = rec["prices"]
        out.append(
            {
                "name": rec["name_votes"].most_common(1)[0][0],
                "aliases": sorted(n for n in rec["name_votes"] if n),
                "sizes": sorted(rec["sizes"]),
                "orders": rec["orders"],
                "total_qty": round(rec["total_qty"], 2),
                "avg_price": round(sum(prices) / len(prices), 2),
                "stores": sorted(rec["stores"]),
                "first_ordered": min(rec["dates"]),
                "last_ordered": max(rec["dates"]),
            }
        )
    out.sort(key=lambda r: (-r["orders"], r["name"]))

    all_dates = [d for rec in agg.values() for d in rec["dates"]]
    summary = {
        "receipts_parsed": receipts,
        "distinct_items": len(out),
        "date_range": [min(all_dates), max(all_dates)] if all_dates else [],
        "items": out,
    }
    with open(OUT, "w") as fh:
        json.dump(summary, fh, indent=2)

    print(f"files scanned:    {len(files)}")
    print(f"receipts parsed:  {receipts}")
    print(f"distinct items:   {len(out)}")
    if all_dates:
        print(f"date range:       {min(all_dates)} .. {max(all_dates)}")
    print(f"\nwrote {OUT}")
    print("\ntop 25 by order count:")
    for r in out[:25]:
        print(f"  {r['orders']:3d}x  {r['name'][:58]:58s} {r['sizes'][0][:14]}")


if __name__ == "__main__":
    main()
