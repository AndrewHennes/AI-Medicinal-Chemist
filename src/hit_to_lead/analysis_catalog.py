"""Verify and index archived analysis artifacts."""

import csv
import html
import json
from pathlib import Path as path_type
from .io import digest, write
from .settings import repository_root


def load_verified_catalog(root):
    """Reject missing, altered or out-of-tree evidence before making a report."""
    root = path_type(root)
    if not root.is_absolute():
        raise ValueError("The repository root must be absolute")
    root = root.resolve()
    catalog = json.loads((root / "results/analysis_history/catalog.json").read_text())
    seen = set()
    for study in catalog["studies"]:
        if study["id"] in seen:
            raise ValueError("Duplicate study identifier")
        seen.add(study["id"])
        for record in study["files"]:
            path = (root / record["file"]).resolve()
            if not path.is_relative_to(root / "results/analysis_history"):
                raise ValueError("Evidence must remain inside its archive directory")
            if not path.is_file() or digest(path) != record["sha256"]:
                raise ValueError(f"Missing or changed historical evidence: {path}")
    return catalog


def make_catalog(root=repository_root):
    """Create a searchable offline index and a machine-readable coverage table."""
    root = path_type(root)
    catalog = load_verified_catalog(root)
    directory = root / "results/analysis_history"
    rows, cards = [], []
    for study in catalog["studies"]:
        identifier = study["id"]
        title = study.get("title", identifier.replace("_", " "))
        conclusion = study.get("conclusion", "")
        links = []
        for record in study["files"]:
            relative = path_type(record["file"]).relative_to("results/analysis_history")
            links.append(
                f'<li><a href="{html.escape(relative.as_posix(), quote=True)}">{html.escape(relative.name)}</a> <span>{html.escape(record["kind"])}</span></li>'
            )
        code = study.get(
            "reproduction", "Evidence regeneration; original training sources indexed"
        )
        rows.append(
            dict(
                study=identifier,
                status=study["status"],
                conclusion=conclusion,
                reproduction=code,
                evidence_files=len(study["files"]),
                historical_source_files=len(study["source_code"]),
            )
        )
        search = html.escape(
            " ".join((identifier, title, conclusion, study["status"])), quote=True
        )
        summary_html = f"<p>{html.escape(conclusion)}</p>" if conclusion else ""
        cards.append(
            f'<article data-search="{search.lower()}"><h2>{html.escape(title)}</h2><p class="status">{html.escape(study["status"].replace("_", " "))}</p>{summary_html}<p class="scope">Reproduction: {html.escape(code)}</p><details><summary>Evidence files ({len(links)})</summary><ul>{"".join(links)}</ul></details></article>'
        )
    with (directory / "coverage.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    page = (
        """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Project analysis history</title><style>
    body{font:16px/1.55 system-ui,sans-serif;margin:0;background:#f6f7f9;color:#202733}main{max-width:1100px;margin:auto;padding:40px 24px}h1{font-size:36px;line-height:1.15}h2{font-size:20px;margin:0}a{color:#1c527b}header{max-width:880px}input{box-sizing:border-box;width:100%;padding:14px;border:1px solid #acb8c3;border-radius:7px;font:inherit;margin:18px 0}article{background:white;padding:22px;border:1px solid #dce2e8;border-radius:8px;margin:16px 0}.status,.scope,li span{color:#5b6570;font-size:14px}.status{text-transform:uppercase;letter-spacing:.04em}summary{cursor:pointer}li{overflow-wrap:anywhere}article[hidden]{display:none}
    </style><main><header><h1>Project analysis history</h1><p>Archived protocols and results from chemical-series prediction and acquisition studies.</p><p><a href="../../docs/analysis_summary.md">Full project summary</a> · <a href="../../docs/reproduction_guide.md">Reproduction guide</a> · <a href="coverage.csv">Coverage table</a> · <a href="catalog.json">Source manifest</a></p><p>Study status and reproduction details accompany each archived analysis.</p></header><label for="search">Find a topic or model</label><input id="search" type="search" placeholder="For example: memory, multitask, variance, initial hit"><p id="count" aria-live="polite"></p>"""
        + "".join(cards)
        + """</main><script>
    const search=document.getElementById('search'),cards=[...document.querySelectorAll('article')],count=document.getElementById('count');
    function update(){let visible=0;for(const card of cards){card.hidden=!card.dataset.search.includes(search.value.trim().toLowerCase());visible+=!card.hidden}count.textContent=visible+' of '+cards.length+' recorded analysis branches';}
    search.addEventListener('input',update);update();</script></html>"""
    )
    (directory / "index.html").write_text(page)
    write(
        directory / "catalog_verification.json",
        dict(
            passed=True,
            studies=len(rows),
            verified_files=sum(row["evidence_files"] for row in rows),
            new_training_performed=False,
        ),
    )
    return directory / "index.html"
