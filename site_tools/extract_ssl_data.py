#!/usr/bin/env python3
"""Extract SSL stats workbook -> JSON for the stats page.

Usage: python3 extract_ssl_data.py <workbook.xlsx> <out.json>

Reads all six data sheets of SSL_Stats_20182026.xlsx (or successor) and emits
a JSON object with one array per sheet plus meta. Numbers are emitted as
numbers; pitching IP keeps the baseball-thirds display string AND a decimal
`IPdec` for sorting/rate math (.1 = 1/3, .2 = 2/3).
"""
import sys, json, datetime, os
import openpyxl

SHEETS = {
    "Batting by Season": "batting_season",
    "Batting Career": "batting_career",
    "Pitching by Season": "pitching_season",
    "Pitching Career": "pitching_career",
    "Team by Season": "team_season",
    "Team Career": "team_career",
}

def ip_to_dec(v):
    """Baseball-thirds IP -> decimal innings. '52.2' -> 52.6667. Team IP is
    already decimal but values like 52.2 are ambiguous; per workbook Read Me,
    individual pitcher IP uses thirds, team IP is decimal — caller decides."""
    if v is None:
        return None
    s = str(v)
    if "." in s:
        whole, frac = s.split(".", 1)
        if frac == "1":
            return int(whole) + 1 / 3
        if frac == "2":
            return int(whole) + 2 / 3
    try:
        return float(s)
    except ValueError:
        return None

def clean(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        if v == "":
            return None
        try:
            f = float(v)
            return int(f) if f == int(f) and "." not in v else f
        except ValueError:
            return v
    if isinstance(v, float) and v == int(v):
        return int(v)
    return v

def main(xlsx_path, out_path):
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    out = {}
    for sheet_name, key in SHEETS.items():
        ws = wb[sheet_name]
        rows = ws.iter_rows(values_only=True)
        header = [str(h).strip() for h in next(rows) if h is not None]
        ncol = len(header)
        data = []
        for r in rows:
            vals = [clean(v) for v in r[:ncol]]
            if all(v is None for v in vals):
                continue
            rec = dict(zip(header, vals))
            # skip stray rows without an identity column
            ident = rec.get("Player") or rec.get("Pitcher") or rec.get("Team")
            if ident is None:
                continue
            if key in ("pitching_season", "pitching_career"):
                rec["IP"] = str(rec.get("IP")) if rec.get("IP") is not None else None
                rec["IPdec"] = round(ip_to_dec(rec.get("IP")), 4) if rec.get("IP") is not None else None
            if key in ("team_season", "team_career") and rec.get("IP") is not None:
                rec["IPdec"] = float(rec["IP"])  # team IP already decimal
            data.append(rec)
        out[key] = data
    src_mtime = os.path.getmtime(xlsx_path)
    out["meta"] = {
        "source_file": os.path.basename(xlsx_path),
        "source_modified": datetime.datetime.fromtimestamp(src_mtime).strftime("%Y-%m-%d"),
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "seasons": sorted({r["Season"] for r in out["batting_season"]}),
        "row_counts": {k: len(v) for k, v in out.items() if isinstance(v, list)},
    }
    with open(out_path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(json.dumps(out["meta"], indent=2))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
