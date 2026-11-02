"""Validate the versioned format and cross-reference constraints."""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

def validate(pack):
    version = pack.get("schemaVersion")
    if version not in ("1.0.0", "2.0.0"):
        raise ValueError(f"Unsupported schemaVersion: {version}")
    filename = "learning-pack-v1.schema.json" if version == "1.0.0" else "learning-pack.schema.json"
    schema = json.loads((ROOT / "schemas" / filename).read_text())
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
            kind = question["type"]
            for item in question.get("choices", question.get("items", question.get("pairs", []))):
                unique(item["id"])
            if kind in ("multipleChoice", "multipleSelect"):
                choices = {c["id"] for c in question["choices"]}
                correct = ({question["correctChoiceId"]} if kind == "multipleChoice"
                           else set(question["correctChoiceIds"]))
                if not correct <= choices:
                    raise ValueError(f"Invalid answer references in {question['id']}")
            if kind == "ordering":
                expected = {item["id"] for item in question["items"]}
                if set(question["correctOrder"]) != expected:
                    raise ValueError(f"Order must include every item in {question['id']}")
            if kind == "matching":
                # Equal visible labels make a unique ID match ambiguous to a learner.
                for side in ("left", "right"):
                    labels = [pair[side].strip().casefold() for pair in question["pairs"]]
                    if len(labels) != len(set(labels)):
                        raise ValueError(f"Ambiguous matching labels in {question['id']}")
            if kind in ("shortAnswer", "fillBlank", "codeCompletion"):
                if any(not answer.strip() for answer in question["acceptedAnswers"]):
                    raise ValueError(f"Blank accepted answer in {question['id']}")
            if kind == "fillBlank" and question["prompt"].count("___") != 1:
                raise ValueError("fillBlank requires exactly one ___ placeholder")
            if kind == "codeCompletion" and question["code"].count("___") != 1:
                raise ValueError("codeCompletion requires exactly one ___ placeholder")

if __name__ == "__main__":
    for path in sys.argv[1:]:
        validate(json.loads(Path(path).read_text()))
        print(f"Valid: {path}")
    if len(sys.argv) < 2:
        raise SystemExit("Usage: validate_pack.py PACK.json [...]")
