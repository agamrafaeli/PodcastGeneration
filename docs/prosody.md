# Prosody Interface

The project provides a simple prosody system that lets the CLI adjust rate, pitch and volume using named styles and intensity levels.

## CLI usage
- `--prosody-style <style>` – select a speaking style such as `newscast` or `dramatic`.
- `--prosody-intensity <1-5>` – control how strongly the style affects rate, pitch and volume.
- `--prosody-list` and `--prosody-info <style>` – discover available styles and inspect their details.

## Configuration files
- `src/prosody/config/styles.yaml` defines each style with baseline `rate`, `pitch`, `volume`, and `emphasis_strength`, plus intensity multipliers 1–5 that scale the effect.
- `src/prosody/config/calibration.yaml` optionally adjusts these parameters per voice so styles sound natural on different voices.

## Parameter conversion
- `get_prosody_params(style, intensity)` in `src/prosody/prosody.py` applies the chosen style and intensity to produce standard prosody parameters like `{ "rate": "+5%", "pitch": "+8Hz", "volume": "+4dB" }`.
- The resulting values are stored in `ConversionParams` (`src/engines/core/types.py`) through the `style` and `style_intensity` fields so engines can apply them consistently.

## Example
```bash
python src/cli.py script.txt --engine edge_tts --prosody-style newscast --prosody-intensity 3
```
