import sys, json, mlx_whisper, glob, os
model = "mlx-community/whisper-large-v3-turbo"
os.makedirs("transcripts", exist_ok=True)
for wav in sorted(glob.glob("audio/*.wav")):
    name = os.path.basename(wav)[:-4]
    print("==>", name, flush=True)
    r = mlx_whisper.transcribe(wav, path_or_hf_repo=model, language="ru", verbose=False)
    with open(f"transcripts/{name}.json", "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    with open(f"transcripts/{name}.txt", "w") as f:
        for s in r["segments"]:
            f.write(f"[{s['start']:7.1f} - {s['end']:7.1f}] {s['text'].strip()}\n")
    print("done", name, flush=True)
