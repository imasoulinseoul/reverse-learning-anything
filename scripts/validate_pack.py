"""Validate the versioned format and cross-reference constraints."""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

def validate(pack):
    schema = json.loads((ROOT / "schemas/learning-pack.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(pack)
    seen = set()
    def unique(value):
        if value in seen:
            raise ValueError(f"Duplicate ID: {value}")
        seen.add(value)
    unique(pack["id"])
    sources = {s["id"] for s in pack["sources"]}
    for source in pack["sources"]:
        unique(source["id"])
    def refs(item):
        if not set(item["sourceRefs"]) <= sources:
            raise ValueError(f"Unknown source reference in {item['id']}")
    if sorted(l["order"] for l in pack["lessons"]) != list(range(1, len(pack["lessons"]) + 1)):
        raise ValueError("Lesson order must be contiguous from 1")
    for lesson in pack["lessons"]:
        unique(lesson["id"])
        refs(lesson)
        for question in lesson["questions"]:
            unique(question["id"])
            refs(question)
            for choice in question["choices"]:
                unique(choice["id"])
            if question["correctChoiceId"] not in {c["id"] for c in question["choices"]}:
                raise ValueError(f"Invalid correctChoiceId in {question['id']}")

if __name__ == "__main__":
    for path in sys.argv[1:]:
        validate(json.loads(Path(path).read_text()))
        print(f"Valid: {path}")
    if len(sys.argv) < 2:
        raise SystemExit("Usage: validate_pack.py PACK.json [...]")
