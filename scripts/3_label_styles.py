from pathlib import Path
from dotenv import load_dotenv
from sarvamai import SarvamAI
import pandas as pd
import json
import os


load_dotenv()
client = SarvamAI(api_subscription_key=os.getenv("SARVAM_API_KEY"))

TRANSCRIPT_DIRS = [Path("transcripts_eng"), Path("transcripts_hindi")]
OUTPUT_CSV = Path("metadata/emotion_labels.csv")

PROMPT = """You are annotating speech segments for a Text-to-Speech (TTS) dataset.
Identify the PRIMARY speaking style from this transcript.

Choose EXACTLY ONE label:
- motivational: inspiring, encouraging, personal growth, calls to action
- educational: teaching, explaining concepts, tutorials, instructional content
- storytelling: narrating events, anecdotes, personal experiences
- conversational: casual informal discussion, friendly interaction
- formal: official speeches, presentations, announcements
- news: reporting current events, journalism
- review: evaluating a movie, product, book, or service
- opinion: personal viewpoints, commentary, analysis
- reading: reading written material aloud, audiobook narration
- neutral: none of the above

Transcript:
{transcript}

Return ONLY the label. No explanation."""


def get_label(transcript):
    response = client.chat.completions(
        model="sarvam-105b",
        messages=[{"role": "user", "content": PROMPT.format(transcript=transcript)}]
    )
    return response.choices[0].message.content.strip().lower()


# collect all json transcript files
json_files = sorted(
    f for d in TRANSCRIPT_DIRS for f in d.rglob("*.json")
)
print(f"Found {len(json_files)} transcript files\n")

rows = []

for i, path in enumerate(json_files, start=1):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        transcript = data.get("transcript", "").strip()

        if not transcript:
            print(f"[{i}] empty transcript: {path.name}")
            continue

        label = get_label(transcript)
        print(f"[{i}/{len(json_files)}] {path.stem} -> {label}")

        rows.append({
            "file_name": path.stem.replace(".wav", ""),
            "transcript": transcript,
            "label": label
        })

    except Exception as e:
        print(f"[{i}] error: {path.name} — {e}")

df = pd.DataFrame(rows)
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

print(f"\nSaved {len(df)} rows -> {OUTPUT_CSV}")
