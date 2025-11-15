"""
Grant finder tool uses a JSON catalogue of grants to match initiatives.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class GrantFinderTool:
    def __init__(self, catalog_path: Path):
        self.catalog_path = catalog_path
        self.grants: List[Dict] = json.loads(catalog_path.read_text(encoding="utf-8"))

    def search(self, *, city: str, state: str, keywords: List[str], max_results: int = 5) -> List[Dict]:
        geography_tokens = {state.upper(), f"US-{state.upper()}"}
        results: List[Dict] = []
        for grant in self.grants:
            tags = {tag.lower() for tag in grant.get("tags", [])}
            if keywords and not any(keyword.lower() in tags for keyword in keywords):
                continue
            geography = {geo.upper() for geo in grant.get("geography", [])}
            if geography and not geography_tokens.intersection(geography) and "US" not in geography:
                continue
            results.append(grant)
            if len(results) >= max_results:
                break
        return results

