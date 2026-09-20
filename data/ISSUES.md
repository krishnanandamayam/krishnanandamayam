# Import findings

Nothing here was changed on import. Each item needs a human decision; fix them in the
editor (`uv run python -m tools.serve`, then http://localhost:8000/edit).

## Noticed by hand while reading the sheet

- no. 91: the HK is a verse to Sri Rama (`…bhadrAdrirAmaM…`), but the English translation
  is about Sri Krishna (Rasa dance, Govardhana). The translation probably belongs elsewhere.
- nos. 102, 105a and 106 carry the same verse (`bahurUpa zrIkRSNadhyAnam`) with different
  English translations.
- The Telugu preface (ముందుమాట) is empty: the sheet has no Telugu prose. Add it in the editor.
- There are no Telugu tatparyas yet; the `te` field of every verse is empty.

## Preface slokas converted from Devanagari to HK (please check)

- Intro row 9: `karmaNyevAdhikAraste mAphaleSu kadAcana .`
- Intro row 12: `durbhikSecAnadAtAraM, sumikSecahariNyadaM . / caturohaM namasyAmiraNe dhIramRte zuciM ..`
- Intro row 15: `anAghrAtaM puSpaMki salayamiva marUnAMkararuhaiH . / anAviddhaM ratnaM madhunavamanAsvAditarasaM ..`
- Intro row 16: `yamovaivasvato devoyasya sohRdayasthitaH tasyana / vivAda stho mAgaMgAM mAkuruSvatH .`
- Intro row 18: `sarvavedeSuyatpuNyaM sarvatIrtheSu yatphalaM . tatphalaM puruSaApnoti . stutvAdevaM janArdanaM . / zrI vAsudevanamostute ..`
- Intro row 20: `aMkolaM nijabIjasaMtati rayaskAMto palaM sUcikA . sAMdhvInaija - vibhuMlatAkSiti ruhaM siMdhussaridvallabhaM prApnotIti yathA tathApazupate pAdAraviMda dvayaM . cetovRtti rupetyatiSTati sadAsAbhaktirityucyate`
- Intro row 21: `anityAni zarIrANi vibhavonaivazAzvataH : / natyiM sannihito viSNuH kartavyodharma saMgrahaH ..`

## Verses whose HK is identical to an earlier verse

- sheet row 34, no. 29 repeats no. 11 word for word
- sheet row 112, no. 105a repeats no. 102 word for word
- sheet row 114, no. 106 repeats no. 102 word for word

## Rows with no Harvard-Kyoto text (not imported)

- sheet row 94, no. 88: HK cell is ''
- sheet row 151, no. 135: HK cell is '(Telugu)'

## Findings in the HK text

- 76 (`v76`): possible line-break residue inside a word: 'vi. zva'
- 76 (`v76`): possible line-break residue inside a word: 've . dansarv'
- 94 (`v94`): `gItAvaLi:` was left as it is. The sheet's own Telugu has a danda there (గీతావళి|), so this colon may be a danda rather than a visarga.
- 98 (`v98`): backslash in text
