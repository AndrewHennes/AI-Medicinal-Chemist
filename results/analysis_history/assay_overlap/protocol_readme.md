# Assay overlap viewer

Open `/Users/asselism/Documents/Codex/2026-09-23/i-h/outputs/assay_overlap/assay_overlap.html` in a browser. The HTML embeds all data and works offline. It includes the six endpoint datasets in the current acquisition benchmark.

Default settings use curated benchmark pools, any species, at least three distinct molecules per species pool, and at least one exact shared standardized molecule to link two assay-local series. The 4,625 benchmark pools contain 3,644 distinct endpoint-local series. Linking across endpoints produces 2,245 inferred groups, of which 676 (30.1%) cover at least two assays and 237 cover at least three. Two groups cover all six assays. With at least 15 molecules per species pool, 85 of 345 inferred groups cover multiple assays.

Linked series groups are connected components of endpoint-local `Analog_Series_ID` values. Edges require exact supplied `Standardized_SMILES` overlap across endpoints after filtering. No shared-document-only links are used. A triple overlap can be supported by different molecules along different links. The shared-molecule threshold is adjustable.

Source mode is also available. At its default minimum of one molecule, 2,866 of 8,378 inferred groups cover multiple assays. This mode includes singleton local series. With a minimum of three molecules, the corresponding counts are 782 of 2,482. Source mode uses inclusion-flagged, finite numeric rows with nonmissing series and standardized structure; it does not repeat benchmark curation or embedding validation. Any-species matching can bridge species, whereas selecting one species restricts all links to it.

Select three assays, click a Venn count or an exclusive-region row, and inspect the underlying local IDs and source documents. Search and pagination apply to this table. Export groups downloads all matching rows, not only the current page. Save diagram downloads an SVG with the current filter labels. Circle areas are schematic; numeric labels are exact.

Verification compared the browser against independent Python calculations for 140 assay-triplet/filter combinations. Assay selection, empty states, region selection, searching, pagination, CSV and SVG exports, and mobile layout passed. No external requests were made by the page.

Supporting files:

- `overlap_summary.csv`: threshold and pool-size sensitivity for both data scopes.
- `benchmark_linked_series.csv`: membership of every default benchmark group.
- `source_audit.json`: input paths, SHA-256 hashes, row counts and definitions.
- `viewer_verification.json`: browser check results.
- `build_overlap_data.py`, `build_viewer.py`, `viewer_template.html`: reproducible sources with absolute paths and no CLI options.

This analysis reads existing datasets only. It does not modify any training data, fold assignment, checkpoint, or running benchmark.
