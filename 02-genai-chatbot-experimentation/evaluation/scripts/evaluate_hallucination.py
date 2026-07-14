"""
Offline hallucination evaluation script.

Usage:
    python scripts/evaluate_hallucination.py --input data/sample_responses.json

Expects a JSON file with format:
    [
        {
            "response": "The recommended dose is...",
            "source_chunks": ["Chunk 1 text...", "Chunk 2 text..."],
            "variant": "B"
        }
    ]
"""
import json
import asyncio
import argparse
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.core.database import engine
from app.services.hallucination_service import HallucinationService
from app.services.settings_service import SettingsService


async def evaluate(input_path: str):
    with open(input_path) as f:
        samples = json.load(f)

    async with async_sessionmaker(engine, class_=AsyncSession)() as db:
        hallu_service = HallucinationService(db)

        results = []
        for i, sample in enumerate(samples):
            response = sample["response"]
            source_chunks = sample.get("source_chunks", [])
            variant = sample.get("variant", "B")

            score = await hallu_service.score_message(
                message_id=f"eval-{i}",
                response=response,
                source_chunks=source_chunks if variant == "B" else None,
            )

            details = json.loads(score.details_json) if score.details_json else {}
            results.append({
                "sample_index": i,
                "variant": variant,
                "hallucination_score": score.score,
                "category": score.category,
                "claim_count": details.get("claim_count", 0),
                "entail_ratio": details.get("entail_ratio", 0),
                "contradiction_ratio": details.get("contradiction_ratio", 0),
            })

            print(f"[{i+1}/{len(samples)}] Variant {variant}: {score.category} (score={score.score:.3f})")

    output_path = Path(input_path).parent / "hallucination_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {output_path}")

    total = len(results)
    consistent = sum(1 for r in results if r["category"] == "Consistent")
    minor = sum(1 for r in results if r["category"] == "Minor Inconsistency")
    major = sum(1 for r in results if r["category"] == "Major Hallucination")
    print(f"\nSummary: {consistent} Consistent, {minor} Minor, {major} Major (out of {total})")


def main():
    parser = argparse.ArgumentParser(description="Offline hallucination evaluation")
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    args = parser.parse_args()
    asyncio.run(evaluate(args.input))


if __name__ == "__main__":
    main()
