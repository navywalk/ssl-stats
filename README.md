# Saltaire Softball League — Stats

Interactive stats site for the SSL, 2018–present. Built automatically from
`SSL_Stats_20182026.xlsx` by GitHub Actions on every push and published via
GitHub Pages.

- **Site:** see the Pages URL in the repo sidebar (leaders, career leaders,
  single-season records, standings, full sortable tables — works on phones).
- **Data:** all stats compiled from GameChanger box scores. ERA is on a
  7-inning basis; pitcher IP uses baseball thirds (.1 = ⅓, .2 = ⅔).
- **Updating:** replace the workbook with a new version and push to `main`;
  the site rebuilds itself in about a minute. The workbook itself is maintained
  in Claude Cowork (game merging + name reconciliation), then pushed here.

`site_tools/` holds the generator: `build_page.py` extracts the six workbook
sheets to JSON (`extract_ssl_data.py`) and injects it into `template.html`,
producing one self-contained HTML file with no server-side dependencies.
