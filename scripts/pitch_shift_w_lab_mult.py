import soundfile as sf
import parselmouth
from parselmouth.praat import call
import numpy as np
import os
import pyworld as world
from tqdm import tqdm

input_folder = input("Enter the path to your wav folder: ")

output_folder = input("Enter your output folder path: ")

pitch_shift_input = input("Enter pitch shifting algorithm | world/tdpsola:")

pitches = []

while True:
    pitch = input("Please enrer one pitch number at a time | Enter Y to proceed: ")
    if pitch.lower() == "y":
        break
    try:
        p_val = float(pitch)
        pitches.append(p_val)
    except ValueError:
        print("Invalid input. Please enter a number or type 'y' to proceed.")

def shift_pitch_pyworld(path):
    loc, fname = os.path.split(path)
    fname_noext, ext = os.path.splitext(fname)

    x, fs = sf.read(path)
    xtype = x.dtype
    int_type = np.issubdtype(xtype, np.integer)

    if int_type:
        info = np.iinfo(xtype)
        x = x / info.max

    if len(x.shape) == 2:
        x = (x[:, 0] + x[:, 1]) / 2

    if x.dtype != np.float64:
        x = x.astype(np.float64)

    f0, t = world.harvest(x, fs)
    sp = world.cheaptrick(x, f0, t, fs)
    ap = world.d4c(x, f0, t, fs, threshold = 0.25)

    new_files = []
    new_lab_files = []

    for i in pitches:
        if i == 0:
            continue
        shift_f0 = f0 * np.exp2(i / 12)
        y = world.synthesize(shift_f0, sp, ap, fs)

        if int_type:
            y = (y * info.max).clip(info.min, info.max).astype(xtype)

        output_file = os.path.join(output_folder, f"{fname_noext}{i:+}.wav")
        sf.write(output_file, y, fs)  
        new_files.append(output_file)

    original_lab = os.path.join(loc, f"{fname_noext}.lab")

    if os.path.exists(original_lab):
        for new_file in new_files:
            new_lab_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(new_file))[0]}.lab")
            with open(original_lab, "r") as lab_file:
                lab_content = lab_file.read()
            with open(new_lab_path, "w") as new_lab_file:
                new_lab_file.write(lab_content)
            new_lab_files.append(new_lab_path)

    return new_files, new_lab_files

def shift_pitch_tdpsola(path):
    loc, fname = os.path.split(path)
    fname_noext, ext = os.path.splitext(fname)

    x, fs = sf.read(path)

    audio = parselmouth.Sound(x.T, sampling_frequency=fs)

    new_files = []
    new_lab_files = []

    for i in pitches:
        if i == 0:
            continue
        
        manipulation = call(audio, "To Manipulation", 0.01, 60, 2400) #100 seems to return better result for some reason but ill stick with 60 for low range ppl
        pitch_tier = call(manipulation, "Extract pitch tier")
        call(pitch_tier, "Shift frequencies", audio.xmin, audio.xmax, i, "semitones")
        call([pitch_tier, manipulation], "Replace pitch tier")
        pitch_shifted = call(manipulation, "Get resynthesis (overlap-add)")

        output_file = os.path.join(output_folder, f"{fname_noext}{i:+}.wav")
        sf.write(output_file, pitch_shifted.values.T, fs)
        new_files.append(output_file)

    original_lab = os.path.join(loc, f"{fname_noext}.lab")

    if os.path.exists(original_lab):
        for new_file in new_files:
            new_lab_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(new_file))[0]}.lab")
            with open(original_lab, "r") as lab_file:
                lab_content = lab_file.read()
            with open(new_lab_path, "w") as new_lab_file:
                new_lab_file.write(lab_content)
            new_lab_files.append(new_lab_path)

    return new_files, new_lab_files

pitch_shift_choice = {
    "world": shift_pitch_pyworld,
    "tdpsola": shift_pitch_tdpsola
}
if pitch_shift_input not in pitch_shift_choice:
    raise ValueError("Invalid pitch shifting input, please enter 'world' or 'tdpsola'")
pitch_shift_algo = pitch_shift_choice[pitch_shift_input]

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

wav_files = [f for f in os.listdir(input_folder) if f.endswith(".wav")]

for wav_file in tqdm(wav_files, desc = "\nProcessing WAV Files"):
    wav_path = os.path.join(input_folder, wav_file)
    pitch_shift_algo(wav_path)
