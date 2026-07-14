"""
Seed script to populate demo data: clinical documents, sample users, and an active experiment.

Usage:
    python -m seed_data.seed
"""
import asyncio
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.experiment import Experiment
from app.models.user import User
from app.settings.config import get_settings
from app.services.rag_service import RAGService

settings = get_settings()

SAMPLE_CLINICAL_DOCUMENTS = {
    "hypertension_guidelines.txt": """
2024 Clinical Practice Guidelines for Hypertension Management

First-line therapy for uncomplicated hypertension:
- ACE inhibitors or ARBs as initial therapy
- Thiazide diuretics as alternative first-line
- Calcium channel blockers if monotherapy insufficient

Target blood pressure goals:
- General population: < 130/80 mmHg
- With diabetes or CKD: < 130/80 mmHg
- Age 65+: < 140/90 mmHg

Combination therapy:
- If BP > 20/10 mmHg above goal, initiate two agents
- Preferred combination: ACE inhibitor + calcium channel blocker
- Avoid combining ACE inhibitor and ARB

Monitoring:
- Check BP at every follow-up visit
- Annual serum creatinine and electrolytes
- Annual lipid panel
""",
    "diabetes_treatment.txt": """
Standards of Medical Care in Type 2 Diabetes

Pharmacologic Therapy:
- First-line: Metformin 500 mg twice daily, titrate to 1000 mg twice daily as tolerated
- If HbA1c remains > 7% after 3 months, add SGLT2 inhibitor or GLP-1 receptor agonist
- GLP-1 RAs preferred in patients with ASCVD or CKD
- SGLT2 inhibitors preferred in patients with HF or CKD

Glycemic Targets:
- HbA1c < 7% for most non-pregnant adults
- Less stringent HbA1c < 8% for patients with severe hypoglycemia history
- Preprandial capillary glucose: 80-130 mg/dL
- Peak postprandial glucose: < 180 mg/dL

Contraindications:
- Metformin: eGFR < 30 mL/min
- SGLT2 inhibitors: history of DKA
- GLP-1 RAs: history of medullary thyroid carcinoma
""",
    "drug_interactions.txt": """
Common Drug Interactions in Primary Care

ACE Inhibitors (Lisinopril, Enalapril):
- Avoid with potassium-sparing diuretics (hyperkalemia risk)
- NSAIDs reduce antihypertensive effect
- Monitor renal function when starting

Metformin:
- Hold metformin before contrast imaging with GFR < 45
- Avoid in acute decompensated HF (lactic acidosis risk)
- Caution with topiramate (increased lactate)

Warfarin:
- Amiodarone increases INR (reduce warfarin dose by 30-50%)
- Fluconazole potentiates warfarin effect
- Rifampin reduces warfarin effect significantly

SSRIs (Sertraline, Fluoxetine):
- Avoid MAOIs (serotonin syndrome risk)
- NSAIDs increase GI bleeding risk
- Fluoxetine inhibits CYP2D6 (affects tamoxifen, metoprolol)
""",
}


async def seed():
    async with async_session_factory() as db:
        user = User(username="demo_clinician")
        db.add(user)
        await db.flush()

        experiment = Experiment(
            name="Hypertension & Diabetes Management",
            description="Compare baseline LLM vs. fine-tuned RAG for clinical Q&A on hypertension and diabetes treatment guidelines",
            status="active",
            traffic_split=0.5,
        )
        db.add(experiment)
        await db.flush()

        rag_service = RAGService(db)
        for filename, content in SAMPLE_CLINICAL_DOCUMENTS.items():
            chunks = await rag_service.ingest_text(filename, content)
            print(f"  Ingested {filename}: {len(chunks)} chunks")

        await db.commit()

        print(f"\nSeed data created:")
        print(f"  User ID: {user.id}")
        print(f"  Experiment ID: {experiment.id}")
        print(f"  Experiment: {experiment.name} ({experiment.status})")
        print(f"  3 clinical documents ingested")
        print(f"\nUse these IDs when testing the API.")


def main():
    asyncio.run(seed())


if __name__ == "__main__":
    main()
