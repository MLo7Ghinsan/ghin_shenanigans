___
## ds_segmentor.py

### what it does:
- segment your .ds file (or files) into multiple segments based on the note group

```
python ds_segmentor.py [path to .ds file OR folder containing .ds files] [options]
```

info:
- `--retime False` | use the original "offset" instead of retiming to 0.5 second | default: True
- `--export_path` | path to the folder you want to save the segment to | default: segmented_files
- module(s): `click`
___
## pitch_shift_w_lab_mult.py

### what it does:
- pitch shift your .wav and duplicate .lab file that goes along with it (if exist)

```
python pitch_shift_w_lab_mult.py
```
info:
- prompt based
- module(s): `soundfile praat-parselmouth numpy pyworld tqdm`
___
## corpus_segmenter.py

### what it does:
- segments your corpus to the nearest value of max segment length input while keeping the first and last phoneme as the pause phoneme(s)
- adds silence and fade in/out to the first/last pause phoneme
- remove segments that only contains pause phoneme(s)
- print out report information

```
python corpus_segmenter.py
```
info:
- prompt based
- module(s): `soundfile numpy`
