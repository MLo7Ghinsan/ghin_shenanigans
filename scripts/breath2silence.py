import os
import numpy as np
import soundfile as sf

breath_phonemes = ["AP", "bre"]
silence_phonemes = ["pau", "sil", "SP"]
all_pause_phonemes = breath_phonemes + silence_phonemes

fade_percent = 0.05 # i think 5% is enough
max_silence_length = 0.25 # seconds
input_folder = input("Enter Enter the path to the input folder: ")

yellow = "\033[93m"
green = "\033[92m"
cyan = "\033[96m"
reset = "\033[0m"

print(f"{yellow}Running post-processing breath cleanup (SP merge + silence trim)...{reset}\n")

def load_lab(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()
    return [tuple(line.strip().split()) for line in lines]

def save_lab(file_path, entries):
    with open(file_path, "w") as f:
        for start, end, phoneme in entries:
            f.write(f"{start} {end} {phoneme}\n")

def process_file(wav_path, lab_path):
    audio, sample_rate = sf.read(wav_path)
    base_name = os.path.basename(wav_path)

    lab_entries = load_lab(lab_path)
    if not lab_entries:
        return

    modified = False
    last = lab_entries[-1]
    last_start, last_end, last_phn = int(last[0]), int(last[1]), last[2]

    second_last = lab_entries[-2] if len(lab_entries) > 1 else None
    second_phn = second_last[2] if second_last else None

    target_idx = None

    if last_phn in breath_phonemes:
        target_idx = -1
    elif last_phn in silence_phonemes and second_phn in breath_phonemes:
        target_idx = -2

    if target_idx is not None:
        start, end, phn = lab_entries[target_idx]
        start, end = int(start), int(end)
        duration = end - start

        if duration > 0:
            fade_len = int(duration * fade_percent)
            fade_start_sample = int(start * sample_rate / 1e7)
            fade_mid_sample = int((start + fade_len) * sample_rate / 1e7)
            end_sample = int(end * sample_rate / 1e7)

            fade_mid_sample = min(fade_mid_sample, len(audio))
            end_sample = min(end_sample, len(audio))

            fade_out_curve = np.linspace(1, 0, fade_mid_sample - fade_start_sample)
            audio[fade_start_sample:fade_mid_sample] *= fade_out_curve
            audio[fade_mid_sample:end_sample] = 0

            lab_entries[target_idx] = (str(start), str(end), "SP")
            modified = True

    if len(lab_entries) >= 2 and lab_entries[-1][2] == "SP" and lab_entries[-2][2] == "SP":
        merged_start = lab_entries[-2][0]
        merged_end = lab_entries[-1][1]
        lab_entries = lab_entries[:-2] + [(merged_start, merged_end, "SP")]
        modified = True

    if lab_entries and lab_entries[-1][2] == "SP":
        start, end = int(lab_entries[-1][0]), int(lab_entries[-1][1])
        duration_sec = (end - start) / 1e7

        if duration_sec > max_silence_length:
            new_end = start + int(max_silence_length * 1e7)
            lab_entries[-1] = (str(start), str(new_end), "SP")

            end_sample = int(new_end * sample_rate / 1e7)
            end_sample = min(end_sample, len(audio))
            audio[end_sample:] = 0
            modified = True

    if modified:
        sf.write(wav_path, audio, sample_rate)
        save_lab(lab_path, lab_entries)
        print(f"{green}Updated:{reset} {base_name}")

def process_all_files(root_folder):
    for root, dirs, files in os.walk(root_folder):
        base_filenames = set(os.path.splitext(f)[0] for f in files if f.endswith(".wav") or f.endswith(".lab"))
        for base in base_filenames:
            wav_path = os.path.join(root, base + ".wav")
            lab_path = os.path.join(root, base + ".lab")
            if os.path.exists(wav_path) and os.path.exists(lab_path):
                process_file(wav_path, lab_path)

process_all_files(input_folder)

print(f"\n{cyan}Processing complete.{reset}")
