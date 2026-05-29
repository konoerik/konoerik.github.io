#!/usr/bin/env python3
"""FLAC integrity checker.

Usage:
    uv run check.py <file> [<file> ...]

Checks each FLAC file for:
  - Metadata completeness (title, artist, album, date, tracknumber)
  - Stream properties vs target (44100 Hz / 16-bit / stereo)
  - File size relative to expected raw audio size
  - Effective frequency cutoff (detects upsampled lossy sources)
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from mutagen.flac import FLAC

TARGET_SAMPLE_RATE = 44100
TARGET_SUBTYPE     = "PCM_16"
TARGET_CHANNELS    = 2

METADATA_FIELDS = ["title", "artist", "album", "date", "tracknumber"]

# Frequency cutoff zones:
#   >= CUTOFF_OK   → ok    (genuine lossless reaches ~22kHz)
#   >= CUTOFF_WARN → warn  (borderline — could be 320kbps upsampled; inspect with Spek)
#   <  CUTOFF_WARN → fail  (almost certainly upsampled lossy)
CUTOFF_OK   = 21_000
CUTOFF_WARN = 20_000

CUTOFF_THRESHOLD_DB = -65
ANALYZE_SECONDS     = 60
WINDOW_SIZE         = 4096  # ~93ms at 44100 Hz

RULE = "─" * 56


# ---------------------------------------------------------------------------
# checks — return (warnings, issues); no I/O
# ---------------------------------------------------------------------------

def check_metadata(path):
    issues = []
    tags = FLAC(path)
    for field in METADATA_FIELDS:
        if not tags.get(field):
            issues.append(f"missing tag: {field}")
    return issues


def check_stream(info):
    issues = []
    if info.samplerate != TARGET_SAMPLE_RATE:
        issues.append(f"sample rate {info.samplerate} Hz (expected {TARGET_SAMPLE_RATE})")
    if info.subtype != TARGET_SUBTYPE:
        issues.append(f"bit depth {info.subtype} (expected {TARGET_SUBTYPE})")
    if info.channels != TARGET_CHANNELS:
        issues.append(f"{info.channels} channels (expected {TARGET_CHANNELS})")
    return issues


def check_frequency_cutoff(path, info):
    max_frames = int(ANALYZE_SECONDS * info.samplerate)
    with sf.SoundFile(path) as f:
        data = f.read(max_frames, dtype="float32")

    mono = data.mean(axis=1) if data.ndim > 1 else data

    hop     = WINDOW_SIZE // 2
    freqs   = np.fft.rfftfreq(WINDOW_SIZE, 1.0 / info.samplerate)
    max_mag = np.zeros(len(freqs))

    for start in range(0, len(mono) - WINDOW_SIZE + 1, hop):
        mag = np.abs(np.fft.rfft(mono[start : start + WINDOW_SIZE]))
        np.maximum(max_mag, mag, out=max_mag)

    peak_db   = 20 * np.log10(max_mag.max() + 1e-12)
    threshold = 10 ** ((peak_db + CUTOFF_THRESHOLD_DB) / 20)
    above     = np.where(max_mag > threshold)[0]
    cutoff_hz = int(freqs[above[-1]]) if len(above) else 0

    warnings, issues = [], []
    if cutoff_hz >= CUTOFF_OK:
        pass
    elif cutoff_hz >= CUTOFF_WARN:
        warnings.append(
            f"frequency cutoff ~{cutoff_hz} Hz — borderline, possible 320kbps upsampled; inspect with Spek"
        )
    else:
        issues.append(
            f"frequency cutoff ~{cutoff_hz} Hz — likely upsampled lossy source"
        )
    return warnings, issues, cutoff_hz


def collect(path):
    info     = sf.info(path)
    warnings = []
    issues   = check_metadata(path) + check_stream(info)

    cutoff_w, cutoff_i, cutoff_hz = check_frequency_cutoff(path, info)
    warnings.extend(cutoff_w)
    issues.extend(cutoff_i)

    return {
        "path":        path,
        "duration":    info.frames / info.samplerate,
        "compression": path.stat().st_size / (info.frames * info.channels * 2),
        "cutoff_hz":   cutoff_hz,
        "warnings":    warnings,
        "issues":      issues,
    }


# ---------------------------------------------------------------------------
# display
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: uv run check.py <file> [<file> ...]")
        sys.exit(1)

    raw_paths = [Path(p) for p in sys.argv[1:]]
    missing   = [p for p in raw_paths if not p.exists()]
    paths     = [p for p in raw_paths if p.exists()]

    # Header
    print(RULE)
    print(f" Target: {TARGET_SAMPLE_RATE} Hz · {TARGET_SUBTYPE} · {TARGET_CHANNELS}ch stereo")
    print(RULE)

    # Group files by parent directory, preserving input order
    grouped = {}
    for path in paths:
        grouped.setdefault(path.parent, []).append(path)

    total_warnings = 0
    total_issues   = len(missing)
    summary_notes  = []

    for directory, dir_paths in grouped.items():
        print(f"\n {directory.name}/")

        results = [collect(p) for p in dir_paths]

        for i, r in enumerate(results):
            is_last      = i == len(results) - 1
            connector    = "└─" if is_last else "├─"
            continuation = "   " if is_last else "│  "

            total_warnings += len(r["warnings"])
            total_issues   += len(r["issues"])

            tagged = [("!", m) for m in r["issues"]] + [("?", m) for m in r["warnings"]]

            status = "ok" if not tagged else f"{tagged[0][0]} {tagged[0][1]}"
            print(f" {connector} {r['path'].name}  {status}")

            for marker, msg in tagged[1:]:
                print(f" {continuation}  {marker} {msg}")

            for marker, msg in tagged:
                summary_notes.append(f" {marker} {r['path'].name}: {msg}")

    for p in missing:
        summary_notes.append(f" ! not found: {p}")

    # Footer
    print(f"\n{RULE}")
    if total_issues == 0 and total_warnings == 0:
        print(f" {len(paths)} file(s) — all ok")
    else:
        parts = []
        if total_issues:
            parts.append(f"{total_issues} issue(s)")
        if total_warnings:
            parts.append(f"{total_warnings} warning(s)")
        print(f" {len(paths)} file(s) — {', '.join(parts)}")
        for note in summary_notes:
            print(note)
    print(RULE)

    if total_issues:
        sys.exit(1)
    elif total_warnings:
        sys.exit(2)


if __name__ == "__main__":
    main()
