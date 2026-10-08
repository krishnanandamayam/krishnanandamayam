# Import findings

Nothing here was changed on import. Each item needs a human decision; fix them in the
editor (`uv run python -m tools.serve`, then http://localhost:8000/edit).

## Noticed by hand while reading the sheet

- no. 91: the HK is a verse to Sri Rama (`…bhadrAdrirAmaM…`), but the English translation
  is about Sri Krishna (Rasa dance, Govardhana). The translation probably belongs elsewhere.
- nos. 102, 105a and 106 carry the same verse (`bahurUpa zrIkRSNadhyAnam`) with different
  English translations.

## From the Telugu document (Google Doc 1qbUreHq…)

- The Telugu preface (ముందుమాట) and the Telugu meanings of verses 1-25 and 54 come from it.
  Its Telugu-script slokas in the preface were converted to HK (please check them).
- The author's postal address and phone number in the doc's opening note were **left out** on
  purpose: the site is public.
- Verses 26 onward have no per-verse meaning in the doc. It has only range summaries
  (`59 నుంచి 160 వరకు గీతికలకు తాత్పర్యములు`, e.g. "68 - 74: …"), a Satyanarayana vrata summary,
  the ten-fold worship list and the dasyadasakam. None of that was imported.
- The doc numbers verses differently from the sheet from about no. 53 on (it merges 53 and 54,
  and its 106 is a different verse from the sheet's 106), so nothing beyond no. 25 was matched
  by number. The one meaning inside the doc's no. 53 was placed by content on the sheet's no. 54.
- no. 11: the sheet's HK is a copy of no. 29 (`duSTazikSaNam ziSTarakSaNam…`) but its English
  translation and the doc's no. 11 are about Ganapati, Siva, Brahma, Vishnu, Ayyappa and Sai.
  The doc's sloka would be `gaNezam gaurIzam vANIzam ramezam, zabarigirivAsinam cAruNAcalezam .
  zrI ziRDIkSetrezam puTTaparthivAsinam tatsarvezam smarAmi sadA zrI sAyIzam ..` — not applied,
  because you said the sheet's HK is the ground truth. Say the word and I will replace it.

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

- 4 (`v4`): meanings of parts 1 and 2 are merged into one.
- 76 (`v76`): possible line-break residue inside a word: 'vi. zva'
- 76 (`v76`): possible line-break residue inside a word: 've . dansarv'
- 94 (`v94`): `gItAvaLi:` was left as it is. The sheet's own Telugu has a danda there (గీతావళి|), so this colon may be a danda rather than a visarga.
- 98 (`v98`): backslash in text
