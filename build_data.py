#!/usr/bin/env python3
"""Generate the website data from data/exercises.json.

Produces:
  data/index.json   -- slim search index (one tiny object per exercise)
  data/ex/<id>.json -- full detail per exercise (loaded on demand by the site)

Run:  python build_data.py
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "data", "exercises.json")
EXDIR = os.path.join(ROOT, "data", "ex")


def main():
    with open(SRC, encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(EXDIR, exist_ok=True)
    slim = []
    for e in data:
        base = os.path.basename(e["image"])          # 0001-2gPfomN.jpg
        media = os.path.splitext(base)[0]            # 0001-2gPfomN
        slim.append({
            "i": e["id"], "n": e["name"], "b": e["body_part"],
            "q": e["equipment"], "t": e["target"], "m": media,
        })
        detail = {
            "id": e["id"], "name": e["name"], "body_part": e["body_part"],
            "equipment": e["equipment"], "target": e["target"],
            "muscle_group": e.get("muscle_group"),
            "secondary_muscles": e.get("secondary_muscles", []),
            "instructions": e.get("instructions", {}),
            "instruction_steps": e.get("instruction_steps", {}),
            "media": media,
        }
        with open(os.path.join(EXDIR, e["id"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(detail, f, ensure_ascii=False, separators=(",", ":"))

    with open(os.path.join(ROOT, "data", "index.json"), "w", encoding="utf-8") as f:
        json.dump(slim, f, ensure_ascii=False, separators=(",", ":"))

    print(f"Wrote data/index.json ({len(slim)} exercises) and {len(slim)} detail files.")


if __name__ == "__main__":
    main()
