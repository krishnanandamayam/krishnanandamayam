# Sri Krishnanandamayam

A stotra grantha, readable in Telugu, Devanagari, Kannada, Tamil, Malayalam, Odia, Gujarati,
Bengali, Gurmukhi, Grantha and Roman (IAST), with meanings under each verse and a print-to-PDF
option (A4 or US Letter).

Every script is generated from **one ground truth**: the Harvard-Kyoto text in
[`data/grantha.yaml`](data/grantha.yaml). Transliteration is done at build time with
[Aksharamukha](https://www.aksharamukha.com/); the site itself is static files.

## See it on your own computer

```bash
cd ~/krishnanandamayam
uv run python -m tools.serve
```

- reader: http://localhost:8000/
- HK editor: http://localhost:8000/edit

## Correcting the text

Use the editor. It shows one verse at a time: the HK text box, the live శుద్ధ తెలుగు rendition
under it, the English and Telugu meanings, and (for reference only) the Telugu that was in the
original sheet, with the words that differ highlighted. **Save** writes that one verse into
`data/grantha.yaml` and rebuilds the site. The editor never runs git; when you are happy:

```bash
git diff data/grantha.yaml
git commit -m "Correct HK" data/grantha.yaml
git push
```

Pushing to `main` runs the tests, builds the site and publishes it to GitHub Pages.

## The two anusvara conventions

`data/grantha.yaml` is kept in **zuddha** form; the tests fail if it is not.

| | zuddha · శుద్ధ | saraLa · సరళ |
|---|---|---|
| nasal before a stop | class nasal: `gaGgA` గఙ్గా | anusvara: `gaMgA` గంగా |
| end of a word | `m`, word break kept: `rAmam ca` రామమ్ చ | anusvara: `rAmaM ca` రామం చ |
| before y r l v z S s h | anusvara: `saMzaya` | anusvara |
| the pranava | `oM` ఓం | `oM` ఓం |

The rules are `Z1`-`Z6` and `S1`-`S6` in [`tools/hk.py`](tools/hk.py); every rule and every
nasal + consonant combination has a named test in `tests/`.

## Layout

| | |
|---|---|
| `data/grantha.yaml` | the ground truth: prefaces, section titles, verses (`hk`, `en`, `te`) |
| `data/ISSUES.md` | what the import found that needs a human decision |
| `data/ZUDDHA_PASS.md` | every word the to_zuddha pass changed on import |
| `data/source/` | the original Google Sheet export, for provenance |
| `scripts.toml` | the scripts on offer; add one here and rebuild |
| `tools/hk.py` | HK alphabet, `to_zuddha`, `to_saraLa`, danda/line splitting, lint |
| `tools/render.py` | HK → any script (used by the build and by the editor preview) |
| `tools/build.py` | builds `site/index.html` and `site/data/*.json` |
| `tools/serve.py`, `tools/editor/` | the local server and editor; never published |
| `site/` | `template.html`, `app.js`, `style.css`, `print.css` |

```bash
uv run pytest            # all tests
uv run python -m tools.build
```
