"""
datamover_import.py - parses a file exported/logged by DataMover (a
sibling GDC app) to extract how many clips were shot and the folder/card
structure, so that info can be attached to a Project without retyping it.

STATUS: placeholder. The exact shape of a real DataMover export hasn't
been confirmed yet (Cristi is sending a sample file) - this handles the
generic cases that are reasonably safe to guess (a JSON file with an
obvious clip list/count, or a CSV where each row is one clip) and is
explicit about what it DOESN'T understand yet, rather than silently
returning a wrong number. Once the real format is known, replace the
body of `parse_json`/`parse_csv` (or add a dedicated branch) with the
exact field names DataMover actually uses.
"""

import json
import csv
import io


class DataMoverImportError(Exception):
    pass


def parse(filename: str, raw_bytes: bytes) -> dict:
    """Returns {"clip_count": int, "structure": <json-serializable>}.
    Raises DataMoverImportError with a message safe to show the user if
    the file can't be understood yet."""
    lower = filename.lower()

    if lower.endswith(".json"):
        return _parse_json(raw_bytes)
    if lower.endswith(".csv"):
        return _parse_csv(raw_bytes)
    if lower.endswith(".pdf"):
        raise DataMoverImportError(
            "Import din PDF nu e încă implementat - trimite un fișier JSON sau CSV, "
            "sau un exemplu de PDF ca să adaug suportul exact."
        )
    raise DataMoverImportError(f"Format necunoscut: {filename}")


def _parse_json(raw_bytes: bytes) -> dict:
    try:
        data = json.loads(raw_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise DataMoverImportError(f"JSON invalid: {e}")

    # Best-effort heuristics for a still-unknown export shape:
    # 1) an explicit clip_count / total_clips field
    # 2) a top-level "clips" list
    # 3) the whole payload IS a list of clips
    if isinstance(data, dict):
        for key in ("clip_count", "total_clips", "clipCount"):
            if key in data and isinstance(data[key], int):
                return {"clip_count": data[key], "structure": data}
        for key in ("clips", "files", "items"):
            if key in data and isinstance(data[key], list):
                return {"clip_count": len(data[key]), "structure": data}
        # Nothing recognizable - hand back the raw structure with no
        # count rather than guessing wrong.
        return {"clip_count": None, "structure": data}

    if isinstance(data, list):
        return {"clip_count": len(data), "structure": data}

    raise DataMoverImportError("Structura JSON nu conține o listă de clipuri recognoscibilă.")


def _parse_csv(raw_bytes: bytes) -> dict:
    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise DataMoverImportError(f"CSV invalid: {e}")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    return {"clip_count": len(rows), "structure": {"rows": rows}}
