#!/usr/bin/env python3
"""Build the SSL stats page: workbook -> ssl_stats.html.

Usage: python3 build_page.py <workbook.xlsx> <out.html> [template.html]
Runs the extractor, injects the JSON into the template's __DATA__ slot.
"""
import sys, os, json, subprocess, tempfile

def main():
    xlsx, out_html = sys.argv[1], sys.argv[2]
    here = os.path.dirname(os.path.abspath(__file__))
    template = sys.argv[3] if len(sys.argv) > 3 else os.path.join(here, "template.html")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        tmp = tf.name
    subprocess.run([sys.executable, os.path.join(here, "extract_ssl_data.py"), xlsx, tmp], check=True)
    with open(tmp) as f:
        data = f.read()
    os.unlink(tmp)
    # keep the inline <script> safe
    data = data.replace("</", "<\\/")
    with open(template) as f:
        html = f.read()
    assert "__DATA__" in html, "template missing __DATA__ slot"
    html = html.replace("__DATA__", data)
    with open(out_html, "w") as f:
        f.write(html)
    print(f"Wrote {out_html} ({os.path.getsize(out_html):,} bytes)")

if __name__ == "__main__":
    main()
