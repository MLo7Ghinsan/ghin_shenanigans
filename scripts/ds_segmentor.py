import json
import os
import click

@click.command(help="Segmentor for .ds file")
@click.option("--input", required=True, help="Path to the input ds file or path to folder for batch segmentation")
@click.option("--retime", default=True, help="Retime segment's offset to 1")
@click.option("--export_path", default="segmented_files", help="Path to the folder where segmented files will be saved")

def main(input, retime, export_path):
    if os.path.isdir(input):
        files = [f for f in os.listdir(input) if f.endswith(".ds")]
        for file_name in files:
            file_path = os.path.join(input, file_name)
            process_ds(file_path, retime, export_path)
    else:
        process_ds(input, retime, export_path)

def process_ds(file_path, retime, export_path):
    if not os.path.exists(export_path):
        os.mkdir(export_path)
    with open(file_path, "r", encoding="utf-8") as file:
        content = json.load(file)
        content_list = [content] if not isinstance(content, list) else content
    file_name, _ = os.path.splitext(os.path.basename(file_path))

    for index, segment in enumerate(content_list):
        if retime:
            segment["offset"] = 1
        exp_name = f"{file_name}_seg_{index + 1}.ds"
        exp_path = os.path.join(export_path, exp_name)
        ds_segment = [segment] if not isinstance(segment, list) else segment
        with open(exp_path, "w", encoding="utf-8") as file:
            json.dump(ds_segment, file, indent=2)
        print(f"{file_name}.ds segment {index + 1} saved to {exp_path}")

if __name__ == "__main__":
    main()
