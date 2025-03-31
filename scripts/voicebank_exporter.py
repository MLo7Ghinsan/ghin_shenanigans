import os
import shutil
import glob
import yaml
import click

phoneme_types_list = { #based from first letter cus yea well it kinda work
    "a": "vowel",
    "i": "vowel",
    "u": "vowel",
    "e": "vowel",
    "o": "vowel",
    "b": "stop",
    "d": "stop",
    "g": "stop",
    "k": "stop",
    "p": "stop",
    "q": "stop",
    "t": "stop",
    "c": "affricate",
    "j": "affricate",
    "f": "fricative",
    "h": "fricative",
    "s": "fricative",
    "v": "fricative",
    "z": "fricative",
    "l": "liquid",
    "r": "liquid",
    "m": "nasal",
    "n": "nasal",
    "w": "semivowel",
    "y": "semivowel",
}

@click.command(help="OpenUtau voicebank builder")
@click.argument("acoustic_onnx_folder", required=True)
@click.argument("variance_onnx_folder", required=True)
@click.option("--name", default="my_diffsinger_vb", help="Name of your speaker")
@click.option("--output", default="output", help="Path to the folder where the voicebank will be saved")

#acoustic_onnx_folder = "acoustic"
#variance_onnx_folder = "variance"
#name = "Neiro"
#output = "test"

def build_ou(acoustic_onnx_folder, variance_onnx_folder, name, output):
    ou_build_out = os.path.join(output, name)

    dsacoustic = os.path.join(ou_build_out, "dsacoustic")
    dsvariance = os.path.join(ou_build_out, "dsvariance")
    dsdur = os.path.join(ou_build_out, "dsdur")
    dspitch = os.path.join(ou_build_out, "dspitch")

    acoustic_embed_target_dir = os.path.join(ou_build_out, "embeds", "acoustic")
    variance_embed_target_dir = os.path.join(ou_build_out, "embeds", "variance")
    phonemes_json_target_dir = dsacoustic
    lang_dictionary_target_dir = dsacoustic

    print("Making folder directories")
    for folder in [
        dsacoustic, dsvariance, dsdur, dspitch,
        acoustic_embed_target_dir,
        variance_embed_target_dir
    ]:
        os.makedirs(folder, exist_ok=True)

    print("Copying acoustic files")
    shutil.copytree(acoustic_onnx_folder, ou_build_out, dirs_exist_ok=True)

    print("Moving acoustic items...")
    acoustic_onnx = os.path.join(ou_build_out, "acoustic.onnx")
    if os.path.exists(acoustic_onnx):
        print(f"Found: {os.path.basename(acoustic_onnx)}, moving it to dsacoustic")
        shutil.move(acoustic_onnx, dsacoustic)

    embeds_files = glob.glob(os.path.join(ou_build_out, "*.emb"))
    for embeds_file in embeds_files:
        if os.path.exists(embeds_file):
            print(f"Found: {os.path.basename(embeds_file)}, moving it to {os.path.join('embeds', 'acoustic')}")
            shutil.move(embeds_file, acoustic_embed_target_dir)

    phonemes_json_files = glob.glob(os.path.join(ou_build_out, "*.json"))
    for phonemes_json_file in phonemes_json_files:
        if os.path.exists(phonemes_json_file):
            print(f"Found: {os.path.basename(phonemes_json_file)}, moving it to dsacoustic")
            shutil.move(phonemes_json_file, phonemes_json_target_dir)

    lang_dictionary_files = glob.glob(os.path.join(ou_build_out, "*.txt"))
    for lang_dictionary_file in lang_dictionary_files:
        if os.path.exists(lang_dictionary_file):
            print(f"Found: {os.path.basename(lang_dictionary_file)}, moving it to dsacoustic")
            shutil.move(lang_dictionary_file, lang_dictionary_target_dir)

    # ill use this later in character.yaml
    acoustic_speakers = [
            os.path.join("embeds", "acoustic", os.path.splitext(os.path.basename(emb))[0])
            for emb in embeds_files
    ]

    print("Appending dsconfig.yaml for acoustic")
    dsconfig_path = os.path.join(ou_build_out, "dsconfig.yaml")
    if os.path.exists(dsconfig_path):
        with open(dsconfig_path, "r") as config:
            acoustic_config = yaml.safe_load(config)

        acoustic_config["acoustic"] = os.path.join("dsacoustic", "acoustic.onnx")
        acoustic_config["languages"] = os.path.join("dsacoustic", "acoustic_languages.json")
        acoustic_config["phonemes"] = os.path.join("dsacoustic", "acoustic_phonemes.json")
        acoustic_config["speakers"] = acoustic_speakers

        with open(dsconfig_path, "w") as config:
            yaml.dump(acoustic_config, config)

        # Temporarily move dsconfig.yaml into dsacoustic
        shutil.move(dsconfig_path, dsacoustic)
    print("Done!")

    print("Copying variance files")
    shutil.copytree(variance_onnx_folder, ou_build_out, dirs_exist_ok=True)

    print("Moving variance items")
    variance_files = [
        ("variance.onnx", "dsvariance"),
        ("pitch.onnx", "dspitch"),
        ("dur.onnx", "dsdur"),
        ("linguistic.onnx", "dsacoustic"),
    ]

    for filename, variance_folder in variance_files:
        source = os.path.join(ou_build_out, filename)
        destination = os.path.join(ou_build_out, variance_folder)
        if os.path.exists(source):
            print(f"Found: {os.path.basename(source)}, moving it to {destination}")
            shutil.move(source, destination)

    embeds_files = glob.glob(os.path.join(ou_build_out, "*.emb"))
    for embeds_file in embeds_files:
        if os.path.exists(embeds_file):
            print(f"Found: {os.path.basename(embeds_file)}, moving it to {os.path.join('embeds', 'variance')}")
            shutil.move(embeds_file, variance_embed_target_dir)

    phonemes_json_files = glob.glob(os.path.join(ou_build_out, "*.json"))
    for phonemes_json_file in phonemes_json_files:
        if os.path.exists(phonemes_json_file):
            print(f"Found: {os.path.basename(phonemes_json_file)}, copying it to dsvariance, dsdur, and dspitch")
            shutil.copy(phonemes_json_file, dsvariance)
            shutil.copy(phonemes_json_file, dsdur)
            shutil.copy(phonemes_json_file, dspitch)
            os.remove(phonemes_json_file)

    lang_dictionary_files = glob.glob(os.path.join(ou_build_out, "*.txt"))
    print("Dictionary files found:", [os.path.basename(dict_name) for dict_name in lang_dictionary_files])

    all_symbols = []
    all_replacements = []
    all_entries = []

    for dictionary_file in lang_dictionary_files:
        dictionary_ext = os.path.basename(dictionary_file).split("-")[1].split(".")[0]

        symbols = []
        replacements = []
        entries = []

        with open(dictionary_file, "r", encoding="utf-8") as f:
            for line in f:
                phoneme = line.strip().split()[0]
                phoneme_type = phoneme_types_list.get(phoneme[0], "stop")
                symbol_entry = {"symbol": f"{dictionary_ext}/{phoneme}", "type": phoneme_type}
                replacement_entry = {"from": phoneme, "to": f"{dictionary_ext}/{phoneme}"}
                entry_entry = {"grapheme": phoneme, "phonemes": [f"{dictionary_ext}/{phoneme}"]}

                symbols.append(symbol_entry)
                replacements.append(replacement_entry)
                entries.append(entry_entry)

                all_symbols.append(symbol_entry)
                all_replacements.append(replacement_entry)
                all_entries.append(entry_entry)

        out_path = os.path.join(ou_build_out, f"dsdict-{dictionary_ext}.yaml")
        print(f"Writing file: dsdict-{dictionary_ext}.yaml with {len(symbols)} entries")
        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write("symbols:\n")
            out_f.write('- {symbol: SP, type: vowel}\n')
            out_f.write('- {symbol: AP, type: vowel}\n')
            for item in symbols:
                out_f.write(f"- {{symbol: {item['symbol']}, type: {item['type']}}}\n")
            out_f.write("\nreplacements:\n")
            for item in replacements:
                out_f.write(f"- {{from: \"{item['from']}\", to: \"{item['to']}\"}}\n")
            out_f.write("\nentries:\n")
            for item in entries:
                out_f.write(f"- {{grapheme: \"{item['grapheme']}\", phonemes: [\"{item['phonemes'][0]}\"]}}\n")
            out_f.write('- {grapheme: "SP", phonemes: [SP]}\n')
            out_f.write('- {grapheme: "AP", phonemes: [AP]}\n')

    dsdict_path = os.path.join(ou_build_out, "dsdict.yaml")
    print(f"Writing file: dsdict.yaml with {len(all_symbols)} entries")
    with open(dsdict_path, "w", encoding="utf-8") as out_f:
        out_f.write("symbols:\n")
        out_f.write('- {symbol: SP, type: vowel}\n')
        out_f.write('- {symbol: AP, type: vowel}\n')
        for item in all_symbols:
            out_f.write(f"- {{symbol: {item['symbol']}, type: {item['type']}}}\n")
        out_f.write("\nreplacements:\n")
        for item in all_replacements:
            out_f.write(f"- {{from: \"{item['from']}\", to: \"{item['to']}\"}}\n")
        out_f.write("\nentries:\n")
        for item in all_entries:
            out_f.write(f"- {{grapheme: \"{item['grapheme']}\", phonemes: [\"{item['phonemes'][0]}\"]}}\n")
        out_f.write('- {grapheme: "SP", phonemes: [SP]}\n')
        out_f.write('- {grapheme: "AP", phonemes: [AP]}\n')

    print(f"Copying generated dictionary to dsvariance, dsdur, and dspitch")

    lang_dictionary_files = glob.glob(os.path.join(ou_build_out, "*.txt"))
    for lang_dictionary_file in lang_dictionary_files:
        if os.path.exists(lang_dictionary_file):
            shutil.copy(lang_dictionary_file, dsvariance)
            shutil.copy(lang_dictionary_file, dsdur)
            shutil.copy(lang_dictionary_file, dspitch)
            os.remove(lang_dictionary_file)

    lang_dictionary_files_yaml = glob.glob(os.path.join(ou_build_out, "*.yaml"))
    for yaml_dictionary_file in lang_dictionary_files_yaml:
        filename = os.path.basename(yaml_dictionary_file)
        if filename != "dsconfig.yaml" and os.path.exists(yaml_dictionary_file):
            shutil.copy(yaml_dictionary_file, dsvariance)
            shutil.copy(yaml_dictionary_file, dsdur)
            shutil.copy(yaml_dictionary_file, dspitch)
            os.remove(yaml_dictionary_file)

    print("Appending dsconfig.yaml for variance")
    dsconfig_path = os.path.join(ou_build_out, "dsconfig.yaml")
    if os.path.exists(dsconfig_path):
        with open(dsconfig_path, "r") as config:
            base_config = yaml.safe_load(config)

        base_config["languages"] = "variance_languages.json"
        base_config["phonemes"] = "variance_phonemes.json"
        base_config["linguistic"] = os.path.join("..", "dsacoustic", "linguistic.onnx")
        base_config["speakers"] = [
            os.path.join("..", "embeds", "variance", os.path.splitext(os.path.basename(emb))[0])
            for emb in embeds_files
        ]

        target_configs = {
            dsvariance: "variance",
            dsdur: "dur",
            dspitch: "pitch"
        }

        for folder, key_to_add in target_configs.items():
            config_copy = base_config.copy()
            config_copy[key_to_add] = f"{key_to_add}.onnx"

            for key in {"variance", "dur", "pitch"} - {key_to_add}:
                config_copy.pop(key, None)

            output_config_path = os.path.join(folder, "dsconfig.yaml")
            with open(output_config_path, "w") as f:
                yaml.dump(config_copy, f,)
    os.remove(dsconfig_path)
    shutil.move(os.path.join(dsacoustic, "dsconfig.yaml"), ou_build_out)
    print("Done!")

    print("Cleaning folders")
    onnx_requirements = {
        dsvariance: "variance.onnx",
        dsdur: "dur.onnx",
        dspitch: "pitch.onnx",
    }

    for folder, required_file in onnx_requirements.items():
        required_path = os.path.join(folder, required_file)
        if not os.path.isfile(required_path):
            shutil.rmtree(folder)

    print("Writing file: character.txt")
    lines = [
        f"name={name}\n",
        "author=\n",
        "web=\n",
        "version=\n",
        "group=\n"
    ]
    with open(os.path.join(ou_build_out, "character.txt"), "w", encoding="utf-8") as file:
        file.writelines(lines)

    print("Writing file: character.yaml")
    lines = [
        "portrait_opacity: 0.5\n",
        "portrait:\n",
        "image:\n",
        "default_phonemizer: OpenUtau.Core.DiffSinger.DiffSingerPhonemizer\n",
        "singer_type: diffsinger\n",
        "text_file_encoding: utf-8\n",
        "subbanks:\n"
    ]

    for i, spk in enumerate(acoustic_speakers, start=1):
        speaker_name = os.path.basename(spk)
        lines.append(f" - color: \"{i:02d}: {speaker_name}\"\n")
        lines.append(f"   suffix: {spk}\n")
    with open(os.path.join(ou_build_out, "character.yaml"), "w", encoding="utf-8") as f:
        f.writelines(lines)


if __name__ == "__main__":
    build_ou()
