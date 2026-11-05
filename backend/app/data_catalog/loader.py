"""
backend.app.data_catalog.loader
===============================
Pure read-only declarative catalog loader and query interface for JESTER.
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from backend.app.data_catalog.models import (
    CatalogSchema,
    Cohort,
    CohortCategory,
    CohortStatus,
)

DEFAULT_CATALOG_PATH = Path(__file__).resolve().parent / "catalog.json"
_CACHED_CATALOG: Optional[CatalogSchema] = None


def load_catalog(catalog_path: Optional[Union[str, Path]] = None, reload: bool = False) -> CatalogSchema:
    """
    Loads and validates the declarative catalog JSON file.
    Does not mutate the database or filesystem.
    """
    global _CACHED_CATALOG
    if _CACHED_CATALOG is not None and not reload and catalog_path is None:
        return _CACHED_CATALOG

    path = Path(catalog_path) if catalog_path else DEFAULT_CATALOG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Catalog file not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    catalog = CatalogSchema.model_validate(data)
    if catalog_path is None:
        _CACHED_CATALOG = catalog

    return catalog


def get_cohort(cohort_id: str, catalog: Optional[CatalogSchema] = None) -> Cohort:
    """Retrieves a single cohort by its unique identifier."""
    cat = catalog or load_catalog()
    for cohort in cat.cohorts:
        if cohort.id == cohort_id:
            return cohort
    raise KeyError(f"Cohort '{cohort_id}' not found in Data Catalog.")


def list_cohorts(
    category: Optional[Union[str, CohortCategory]] = None,
    environment: Optional[str] = None,
    status: Optional[Union[str, CohortStatus]] = None,
    catalog: Optional[CatalogSchema] = None,
) -> List[Cohort]:
    """Filters cohorts by category, environment, and/or status."""
    cat = catalog or load_catalog()
    results = []

    cat_val = category.value if isinstance(category, CohortCategory) else category
    status_val = status.value if isinstance(status, CohortStatus) else status

    for cohort in cat.cohorts:
        if cat_val and cohort.category.value != cat_val:
            continue
        if environment and environment not in cohort.environment:
            continue
        if status_val and cohort.status.value != status_val:
            continue
        results.append(cohort)

    return results


def load_cohort_source(cohort: Cohort, base_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Loads the source records for a cohort if source is a JSON file.
    Pure read-only operation.
    """
    root = base_dir or Path(__file__).resolve().parents[3]
    source_path = root / cohort.source

    if not source_path.exists():
        # Try relative to catalog directory
        alt_path = Path(__file__).resolve().parent / cohort.source
        if alt_path.exists():
            source_path = alt_path
        else:
            raise FileNotFoundError(f"Source file for cohort '{cohort.id}' not found at: {source_path}")

    with open(source_path, "r", encoding="utf-8") as f:
        return json.load(f)

