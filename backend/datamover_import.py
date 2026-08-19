"""
datamover_import.py - parses a file exported by DataMover (a sibling GDC
app that offloads + checksum-verifies an entire card/drive) to extract
how many actual video clips were shot and the folder structure, so that
info can be attached to a Project without retyping it.

Confirmed against real sample files from Cristi (offload_checkpoint.json
+ the matching .csv report) - not guessed. Two real quirks that shaped
this:

1. DataMover verifies EVERY file it finds on the source, not just video
   clips - a real checkpoint from Cristi's own test drive had 6954 total
   files but only 10 were actual camera clips (the rest: app bundles,
   Python packages, fonts... whatever else happened to be on that
   volume). So `total_files` is NOT the clip count - clips are counted
   by filtering to known video extensions.
2. The JSON checkpoint's `files` dict only has a per-file "ok"/error
   status (no size, no checksum) - the CSV report has the richer detail
   (`fisier,marime_bytes,verificare_sursa,verificare_destinatie,status,eroare`,
   Romanian headers) if that's what's uploaded instead.
"""

import json
import csv
import io

VIDEO_EXTENSIONS = {
    ".mov", ".mp4", ".mxf", ".braw", ".r3d", ".ari", ".avi",
    ".mkv", ".m4v", ".crm", ".mts", ".m2ts",
}


class DataMoverImportError(Exception):
    pass


def _is_video(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    if "." not in name:
        return False
    return "." + name.rsplit(".", 1)[-1].lower() in VIDEO_EXTENSIONS


def parse(filename: str, raw_bytes: bytes) -> dict:
    """Returns {"clip_count": int, "structure": <json-serializable>}.
    Raises DataMoverImportError with a message safe to show the user if
    the file can't be understood."""
    lower = filename.lower()

    if lower.endswith(".json"):
        return _parse_checkpoint_json(raw_bytes)
    if lower.endswith(".csv"):
        return _parse_report_csv(raw_bytes)
    if lower.endswith(".pdf"):
        raise DataMoverImportError(
            "Import direct din PDF nu e susținut — DataMover generează în paralel "
            "un fișier .json (offload_checkpoint.json) sau .csv cu aceleași date, "
            "mult mai ușor de citit automat. Încarcă unul dintre acelea."
        )
    raise DataMoverImportError(f"Format necunoscut: {filename}")


def _parse_checkpoint_json(raw_bytes: bytes) -> dict:
    try:
        data = json.loads(raw_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise DataMoverImportError(f"JSON invalid: {e}")

    # The real DataMover checkpoint shape.
    if isinstance(data, dict) and isinstance(data.get("files"), dict):
        files = data["files"]
        clip_paths = [p for p in files if _is_video(p)]
        failed = [p for p, status in files.items() if status != "ok"]
        structure = {
            "source": data.get("source"),
            "folder_name": data.get("folder_name"),
            "verification_model": data.get("verification_model"),
            "completed": data.get("completed"),
            "total_files": data.get("total_files", len(files)),
            "clip_files": sorted(clip_paths),
            "failed_files": sorted(failed),
        }
        return {"clip_count": len(clip_paths), "structure": structure}

    # Fallback for a differently-shaped JSON (older/future export) -
    # best-effort rather than a hard failure.
    if isinstance(data, dict):
        for key in ("clip_count", "total_clips", "clipCount"):
            if key in data and isinstance(data[key], int):
                return {"clip_count": data[key], "structure": data}
        for key in ("clips", "files", "items"):
            if key in data and isinstance(data[key], list):
                return {"clip_count": len(data[key]), "structure": data}
        return {"clip_count": None, "structure": data}

    if isinstance(data, list):
        return {"clip_count": len(data), "structure": data}

    raise DataMoverImportError("Structura JSON nu conține o listă de fișiere recognoscibilă.")


def _parse_report_csv(raw_bytes: bytes) -> dict:
    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise DataMoverImportError(f"CSV invalid: {e}")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        return {"clip_count": 0, "structure": {"rows": []}}

    # DataMover's own CSV report ("fisier,marime_bytes,verificare_sursa,
    # verificare_destinatie,status,eroare") - filter to video clips and
    # surface anything that failed verification.
    if "fisier" in rows[0] and "status" in rows[0]:
        clip_rows = [r for r in rows if _is_video(r["fisier"])]
        failed_rows = [r for r in rows if (r.get("status") or "").upper() != "OK" or r.get("eroare")]
        structure = {
            "total_files": len(rows),
            "clip_files": [r["fisier"] for r in clip_rows],
            "failed_files": [
                {"fisier": r["fisier"], "status": r.get("status"), "eroare": r.get("eroare")}
                for r in failed_rows
            ],
        }
        return {"clip_count": len(clip_rows), "structure": structure}

    # Unrecognized CSV shape - fall back to "one row = one clip" only
    # when every row actually looks like a video file; otherwise just
    # report the row count without pretending it's a clip count.
    if all(_is_video(next(iter(r.values()), "")) for r in rows):
        return {"clip_count": len(rows), "structure": {"rows": rows}}
    return {"clip_count": None, "structure": {"rows": rows}}
