# indic-tts-dataset

**End-to-end data engineering for speech: an automated pipeline that turns raw YouTube audio into a clean, structured, style-labelled TTS training corpus — acquisition, segmentation, ASR transcription, LLM labelling, and publishing, fully scripted.**

`yt-dlp` · `ffmpeg` · `ASR (Saaras v3)` · `LLM labelling (sarvam-105b)` · `HuggingFace Datasets`

End-to-end pipeline for building a Hindi + English TTS training dataset from YouTube audio. Downloads source videos, cuts timestamped clips, transcribes with ASR, labels speaking style with an LLM, and publishes a structured dataset to HuggingFace.

**Dataset:** [`aditya1101203/indic-tts-dataset`](https://huggingface.co/datasets/aditya1101203/indic-tts-dataset)

---

## Pipeline

```
YouTube URLs + timestamps
    → 1_acquire.py          yt-dlp download + ffmpeg clip extraction (16kHz mono WAV)
    → 2_transcribe.py       batch ASR transcription (Saaras v3), saves raw JSON
    → 3_label_styles.py     speaking style labeling via sarvam-105b (closed taxonomy)
    → 4_build_metadata.py   merges transcripts + labels → final_metadata.csv
    → 5_verify.py           dataset summary — clip counts, duration, style distribution
    → 6_make_hf_metadata.py generates per-folder metadata.csv for HuggingFace AudioFolder
```

---

## Dataset stats

| | |
|---|---|
| Total clips | 57 |
| Total duration | ~54 minutes |
| English | 29 clips |
| Hindi | 28 clips |
| Audio format | 16kHz mono WAV |

**Style distribution:**

| Style | Count |
|---|---|
| educational | 17 |
| storytelling | 15 |
| motivational | 12 |
| opinion | 9 |
| conversational | 3 |
| review | 1 |

---

## Design decision: style labels, not emotion labels

A deliberate engineering choice in this pipeline is labelling each clip by **speaking style** (educational, storytelling, motivational, …) rather than by emotion. Emotion labels are noisy and inconsistent to assign from transcript text alone, and map poorly onto what a TTS model actually needs. Speaking style is far more reliably labelable from the transcript, and is more directly useful for controlling **prosody** in downstream TTS training. The taxonomy is a fixed, closed set so labels stay consistent across the whole corpus.

---

## Repo structure

```
indic-tts-dataset/
├── scripts/
│   ├── 1_acquire.py
│   ├── 2_transcribe.py
│   ├── 3_label_styles.py
│   ├── 4_build_metadata.py
│   ├── 5_verify.py
│   └── 6_make_hf_metadata.py
├── metadata/
│   ├── english.csv          # source URLs + timestamps for English clips
│   ├── hindi.csv            # source URLs + timestamps for Hindi clips
│   ├── style_labels.csv     # per-clip transcripts + style labels
│   └── final_metadata.csv   # audio_path, transcript, language, style
├── transcripts_eng/         # raw ASR JSON output per English clip
├── transcripts_hindi/       # raw ASR JSON output per Hindi clip
└── README.md
```

Audio files are not stored in this repo — they live on HuggingFace.

---

## Style taxonomy

Labels are assigned by prompting sarvam-105b with the transcript and constraining output to one of:

| Label | Description |
|---|---|
| `educational` | structured explanation or instruction |
| `storytelling` | narrative, anecdote, personal experience |
| `motivational` | persuasive or inspirational tone |
| `opinion` | personal perspective or commentary |
| `conversational` | informal, dialogue-like delivery |
| `review` | evaluation of a product, idea, or experience |

---

## License

MIT
