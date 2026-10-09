# Import findings

Nothing here was changed on import. Each item needs a human decision; fix them in the
editor (`uv run python -m tools.serve`, then http://localhost:8000/edit).

Rechecked against `data/grantha.yaml` on 2026-10-09. Items the file no longer shows were
removed or reworded below; entries to come back to are in `data/flags.toml`.

## Noticed by hand while reading the sheet

- nos. 102, 105a and 106 all have the title `bahurUpa zrIkRSNadhyAnam` and different English
  translations. The HK of 102 and 106 is identical; 105a's HK has since been edited and differs.
- no. 91 (earlier: HK to Sri Rama, English about Sri Krishna) no longer shows that: its HK and
  English now both speak of Sri Rama and the syllables "ra" and "ma".

## From the Telugu document (Google Doc 1qbUreHq…)

- The Telugu preface (ముందుమాట) and the Telugu meanings of verses 1-25 and 54 came from it.
  Telugu meanings have since been added for more verses: 168 of the 190 verses now have one.
  The 22 without: v105, v109, v113, v120-0, v121-v130, u1, u2, v135A, u3, v151-v153, v183.
  Its Telugu-script slokas in the preface were converted to HK (please check them).
- The author's postal address and phone number in the doc's opening note were **left out** on
  purpose: the site is public.
- Verses 26 onward have no per-verse meaning in the doc. It has only range summaries
  (`59 నుంచి 160 వరకు గీతికలకు తాత్పర్యములు`, e.g. "68 - 74: …"), a Satyanarayana vrata summary,
  the ten-fold worship list and the dasyadasakam. None of that was imported.
- The doc numbers verses differently from the sheet from about no. 53 on (it merges 53 and 54,
  and its 106 is a different verse from the sheet's 106), so nothing beyond no. 25 was matched
  by number. The one meaning inside the doc's no. 53 was placed by content on the sheet's no. 54.
- no. 11: the sheet's HK was a copy of no. 29, while its English translation and the doc's no. 11
  are about Ganapati, Siva, Brahma, Vishnu, Ayyappa and Sai. The HK of v11 now reads
  `gaNezam gaurIzam vANIzam ramezam, zabarigirivAsinam ca aruNAcalezam .`, the doc's sloka
  (edited in the editor); nothing is left of the mismatch.

## Preface slokas converted from Devanagari to HK (please check)

These are the HK strings as converted on import. The file keeps HK in zuddha form, so the
anusvaras of some of them (`M` here) are now stored as the class nasal and the strings below do
not appear verbatim; they were not compared word by word on this recheck.

- Intro row 9: `karmaNyevAdhikAraste mAphaleSu kadAcana .`
- Intro row 12: `durbhikSecAnadAtAraM, sumikSecahariNyadaM . / caturohaM namasyAmiraNe dhIramRte zuciM ..`
- Intro row 15: `anAghrAtaM puSpaMki salayamiva marUnAMkararuhaiH . / anAviddhaM ratnaM madhunavamanAsvAditarasaM ..`
- Intro row 16: `yamovaivasvato devoyasya sohRdayasthitaH tasyana / vivAda stho mAgaMgAM mAkuruSvatH .`
- Intro row 18: `sarvavedeSuyatpuNyaM sarvatIrtheSu yatphalaM . tatphalaM puruSaApnoti . stutvAdevaM janArdanaM . / zrI vAsudevanamostute ..`
- Intro row 20: `aMkolaM nijabIjasaMtati rayaskAMto palaM sUcikA . sAMdhvInaija - vibhuMlatAkSiti ruhaM siMdhussaridvallabhaM prApnotIti yathA tathApazupate pAdAraviMda dvayaM . cetovRtti rupetyatiSTati sadAsAbhaktirityucyate`
- Intro row 21: `anityAni zarIrANi vibhavonaivazAzvataH : / natyiM sannihito viSNuH kartavyodharma saMgrahaH ..`

## Verses whose HK is identical to an earlier verse

- `v106` repeats `v102` word for word.
- (Earlier also v29 = v11 and v105a = v102; their HK now differs.)

## Rows with no Harvard-Kyoto text (not imported)

- sheet row 94, no. 88: HK cell is ''; the file has no entry for no. 88.
- sheet row 151, no. 135: HK cell is '(Telugu)'; the file has no entry for no. 135 (there is `v135A`).
- Entries whose `hk` is empty now, with only an English meaning: `v105` and `v109`.

## Findings in the HK text

- 4 (`v4`): meanings of parts 1 and 2 are merged into one.
- The lint (`HK.lint`, as the editor runs it) reports nothing on any entry at the moment. The
  earlier findings, `v76` (possible line-break residue), `v94` (`gItAvaLi:`) and `v98` (a
  backslash), are no longer reported. `v183`'s colons are accepted in `data/lint-ok.toml`.
- `v129` has no English meaning and no Telugu meaning.
