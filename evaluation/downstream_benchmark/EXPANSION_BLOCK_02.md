# Section-M Expansion Block 02

Status: `SECTION_M_EXPANSION_BLOCK_02_FROZEN`.

## A. Authority and controlling identities

The Human PI's corrected Block-02 instruction authorizes exactly ten additional metadata candidate identities under `SCREENING_SPEC_V1.md` section M. `EXPANSION_BLOCK_02_TRIGGER_V1.md` records the joint authority for the pre-oracle capacity trigger. This freeze is selection-only; the 27 accepted environment exclusions establish need and do not enter candidate ranking or admission.

- Pinned BugsInPy commit: `11c5f1eea954a42132cfd06bf257766a7963e0fd`.
- Pinned BugsInPy tree: `d00ce0495ba73abe50317599f48bced3c9afe4b3`.
- Frozen candidate universe SHA-256: `78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c`.
- Sampling seed: `20260922`; rank digest: SHA-256 of `20260922|candidate|<project>::<bug_id>`, sorted by digest then canonical ID.
- Cumulative admission cap: four metadata candidates per project, including all 40 initial admissions and all 10 Block-01 admissions, regardless of later environment exclusion.

## B. Previous cursor and cumulative project counts

The Block-01 selection and traversal ledgers end with their tenth admission, `luigi::20`, at rank **102**. Its canonical identity independently rehashes to `8a478d475066ab94afccf80472aa031e141ec8639296487fdd7fa572308ae02c`. Block 02 first examines rank **103** and never revisits a rank at or below 102. Project counts were derived from frozen initial-40 membership and the ten frozen Block-01 admissions.

| Project | Before Block 02 | After Block 02 |
| --- | ---: | ---: |
| `PySnooper` | 0 | 1 |
| `ansible` | 4 | 4 |
| `black` | 4 | 4 |
| `cookiecutter` | 0 | 2 |
| `fastapi` | 3 | 4 |
| `httpie` | 3 | 4 |
| `keras` | 4 | 4 |
| `luigi` | 4 | 4 |
| `matplotlib` | 4 | 4 |
| `pandas` | 4 | 4 |
| `sanic` | 2 | 2 |
| `scrapy` | 4 | 4 |
| `spacy` | 2 | 4 |
| `thefuck` | 4 | 4 |
| `tornado` | 2 | 4 |
| `tqdm` | 2 | 3 |
| `youtube-dl` | 4 | 4 |
| **Total** | **50** | **60** |

## C. Complete deterministic traversal

Every ranked row from **103** through **246**, inclusive, was examined once: **144** rows. The detailed metadata, membership, pre-decision project count, decision, exact reason, and admission order are frozen in `expansion_block_02_traversal.csv` (SHA-256 `985de4e8e751400144c5143f0eb7e581b6bcf3e122dd8314592f0f5714acddc9`). All examined rows were metadata eligible and outside the previously selected/previously skipped range. Decision counts: `ADMIT=10`, `SKIP_PROJECT_CAP=134`, `SKIP_PREVIOUSLY_SKIPPED=0`, `SKIP_ALREADY_SELECTED=0`, `SKIP_METADATA_INELIGIBLE=0`. Each cap skip means `CUMULATIVE_PROJECT_CAP_4_REACHED`; each admission means `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP`.

| Rank | Case | Project count before | Decision | Exact reason | Block order |
| ---: | --- | ---: | --- | --- | ---: |
| 103 | `thefuck::5` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 104 | `pandas::67` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 105 | `keras::10` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 106 | `pandas::156` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 107 | `youtube-dl::38` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 108 | `tornado::13` | 2 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 1 |
| 109 | `thefuck::18` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 110 | `pandas::25` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 111 | `scrapy::5` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 112 | `youtube-dl::26` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 113 | `pandas::55` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 114 | `scrapy::1` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 115 | `pandas::1` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 116 | `black::23` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 117 | `pandas::153` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 118 | `matplotlib::1` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 119 | `pandas::42` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 120 | `youtube-dl::2` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 121 | `matplotlib::26` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 122 | `thefuck::30` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 123 | `scrapy::6` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 124 | `luigi::9` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 125 | `scrapy::7` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 126 | `youtube-dl::39` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 127 | `keras::32` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 128 | `pandas::34` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 129 | `matplotlib::6` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 130 | `pandas::56` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 131 | `pandas::71` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 132 | `pandas::127` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 133 | `ansible::14` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 134 | `scrapy::35` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 135 | `tornado::4` | 3 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 2 |
| 136 | `scrapy::24` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 137 | `pandas::103` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 138 | `pandas::91` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 139 | `scrapy::21` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 140 | `pandas::37` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 141 | `pandas::149` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 142 | `pandas::166` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 143 | `black::1` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 144 | `pandas::77` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 145 | `tornado::14` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 146 | `pandas::154` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 147 | `youtube-dl::28` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 148 | `youtube-dl::6` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 149 | `ansible::10` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 150 | `youtube-dl::23` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 151 | `pandas::57` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 152 | `keras::30` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 153 | `matplotlib::20` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 154 | `pandas::58` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 155 | `youtube-dl::10` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 156 | `pandas::41` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 157 | `scrapy::40` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 158 | `thefuck::27` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 159 | `youtube-dl::14` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 160 | `matplotlib::23` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 161 | `pandas::161` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 162 | `pandas::5` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 163 | `youtube-dl::32` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 164 | `black::11` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 165 | `tornado::1` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 166 | `matplotlib::3` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 167 | `ansible::6` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 168 | `pandas::126` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 169 | `spacy::6` | 2 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 3 |
| 170 | `matplotlib::15` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 171 | `fastapi::12` | 3 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 4 |
| 172 | `pandas::13` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 173 | `luigi::28` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 174 | `keras::41` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 175 | `cookiecutter::3` | 0 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 5 |
| 176 | `matplotlib::8` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 177 | `luigi::32` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 178 | `pandas::12` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 179 | `ansible::5` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 180 | `ansible::7` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 181 | `pandas::70` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 182 | `tqdm::7` | 2 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 6 |
| 183 | `youtube-dl::33` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 184 | `scrapy::27` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 185 | `cookiecutter::4` | 1 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 7 |
| 186 | `scrapy::34` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 187 | `youtube-dl::9` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 188 | `pandas::35` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 189 | `youtube-dl::41` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 190 | `youtube-dl::34` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 191 | `youtube-dl::42` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 192 | `keras::13` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 193 | `matplotlib::14` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 194 | `luigi::17` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 195 | `thefuck::22` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 196 | `thefuck::25` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 197 | `luigi::18` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 198 | `pandas::95` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 199 | `keras::44` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 200 | `scrapy::17` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 201 | `pandas::59` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 202 | `youtube-dl::8` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 203 | `scrapy::11` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 204 | `pandas::6` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 205 | `keras::23` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 206 | `pandas::43` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 207 | `black::7` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 208 | `keras::5` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 209 | `pandas::101` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 210 | `tornado::7` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 211 | `pandas::74` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 212 | `pandas::54` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 213 | `pandas::123` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 214 | `ansible::17` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 215 | `thefuck::13` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 216 | `pandas::87` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 217 | `scrapy::18` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 218 | `keras::34` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 219 | `luigi::5` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 220 | `black::5` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 221 | `luigi::15` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 222 | `pandas::162` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 223 | `luigi::11` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 224 | `pandas::128` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 225 | `fastapi::15` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 226 | `tornado::10` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 227 | `spacy::7` | 3 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 8 |
| 228 | `matplotlib::19` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 229 | `pandas::121` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 230 | `pandas::144` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 231 | `keras::42` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 232 | `spacy::9` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 233 | `fastapi::10` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 234 | `ansible::18` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 235 | `pandas::132` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 236 | `keras::3` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 237 | `tornado::8` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 238 | `pandas::73` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 239 | `pandas::63` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 240 | `httpie::5` | 3 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 9 |
| 241 | `pandas::16` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 242 | `youtube-dl::5` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 243 | `pandas::169` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 244 | `youtube-dl::21` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 245 | `pandas::99` | 4 | `SKIP_PROJECT_CAP` | `CUMULATIVE_PROJECT_CAP_4_REACHED` | — |
| 246 | `PySnooper::1` | 0 | `ADMIT` | `SECTION_M_NEXT_RANKED_UNDER_PROJECT_CAP` | 10 |

## D. Exact ten admissions

`expansion_block_02.csv` (SHA-256 `b1d4cc0a8c863535ef881d4c25b4ddd469ab5925cedc36a6e5783c20d01cd6a7`) preserves the selected source metadata exactly as recorded in `candidate_universe.csv`. All ten rows are `METADATA_ELIGIBLE`, outside the initial 40 and Block 01, and in increasing frozen rank order.

| Block order | Rank | Case | Rank SHA-256 | Project count after |
| ---: | ---: | --- | --- | ---: |
| 1 | 108 | `tornado::13` | `3577808a4946416ee0db75b4d06855788017fd4f8b89a4e71cfb86ac32480345` | 3 |
| 2 | 135 | `tornado::4` | `43774778abc30b7d6293ab84c862e75f3403cb5e6a3205d19c65bde050c1d746` | 4 |
| 3 | 169 | `spacy::6` | `563b2e92c7826a96eb2d1d77387b8e78cdb0fb199bb5e8cd6689622ae6bee4d3` | 3 |
| 4 | 171 | `fastapi::12` | `5791819b713483bfd8a15c067ab88b2d1351990039e331e0cbdfe9f6e34eade3` | 4 |
| 5 | 175 | `cookiecutter::3` | `5891f187b776c9172a477426ec1994ce243f0b3986cfc617837248fd3f8f3160` | 1 |
| 6 | 182 | `tqdm::7` | `5d33135c88e2a3662c79689ac488e3b8c5f787fdb9f8d02a91ba82c297dea548` | 3 |
| 7 | 185 | `cookiecutter::4` | `5e6349b1ebbdaf555fac8e9f90419d4e5d94b20eefd0727ee990de47d460f4fc` | 2 |
| 8 | 227 | `spacy::7` | `7705e1cabb197428a8b0525ff94729b5ca074a287f1f74bcf5bc5fe563b6f2b4` | 4 |
| 9 | 240 | `httpie::5` | `79b620f49cda76ecb2c1135d44ba316734af86b1c365db2de9c8b5f756f22820` | 4 |
| 10 | 246 | `PySnooper::1` | `7cce5ccb9baf06930fc504464a864fd58ec37a3c482b59bff9119a0b8b014cc3` | 1 |

## E. Canonical block identity and next cursor

Canonical identity is UTF-8 JSON with lexicographically sorted keys, deterministic separators `(',', ':')`, JSON integer counts/ranks/seed, and no timestamp. The exact canonical JSON bytes decode as:

```json
{"block_admitted_count":10,"block_number":2,"bugsinpy_commit":"11c5f1eea954a42132cfd06bf257766a7963e0fd","candidate_universe_sha256":"78208adf610a50542be6dfbd03a9b25960ba0b5cfc80768b08ffe7a4c78f3b8c","cumulative_admitted_count":60,"first_examined_rank":103,"next_cursor_rank":246,"ordered_10_candidate_ranks":[108,135,169,171,175,182,185,227,240,246],"ordered_10_case_ids":["tornado::13","tornado::4","spacy::6","fastapi::12","cookiecutter::3","tqdm::7","cookiecutter::4","spacy::7","httpie::5","PySnooper::1"],"ordered_10_rank_sha256":["3577808a4946416ee0db75b4d06855788017fd4f8b89a4e71cfb86ac32480345","43774778abc30b7d6293ab84c862e75f3403cb5e6a3205d19c65bde050c1d746","563b2e92c7826a96eb2d1d77387b8e78cdb0fb199bb5e8cd6689622ae6bee4d3","5791819b713483bfd8a15c067ab88b2d1351990039e331e0cbdfe9f6e34eade3","5891f187b776c9172a477426ec1994ce243f0b3986cfc617837248fd3f8f3160","5d33135c88e2a3662c79689ac488e3b8c5f787fdb9f8d02a91ba82c297dea548","5e6349b1ebbdaf555fac8e9f90419d4e5d94b20eefd0727ee990de47d460f4fc","7705e1cabb197428a8b0525ff94729b5ca074a287f1f74bcf5bc5fe563b6f2b4","79b620f49cda76ecb2c1135d44ba316734af86b1c365db2de9c8b5f756f22820","7cce5ccb9baf06930fc504464a864fd58ec37a3c482b59bff9119a0b8b014cc3"],"previous_admitted_count":50,"previous_cursor_rank":102,"project_cap":4,"sampling_seed":20260922,"schema":"SECTION_M_EXPANSION_BLOCK_IDENTITY_V1","traversal_terminal_rank":246}
```

**Block identity SHA-256:** `6d5a8a713ddcb18ea70b8268c72e7aa2d5e1eb44bace81f1bd485c88907c0b95`.

The tenth admission and traversal terminal are at rank **246**. The next cursor is rank **246**; any separately authorized subsequent block would start at rank **247**.

## F. Independent reproduction and execution boundary

Derivation A reconstructed the digest-sorted universe, the initial 40 first-pass admissions, every Block-01 traversal decision, and then Block 02. Derivation B rebuilt the pre-block project counts from the committed `selected_initial_40` flags plus `expansion_block_01.csv`, used the frozen `candidate_rank` map, and traversed from 103. Both agreed on all 144 examined identities, each decision, reason and `project_count_before`, all ten admission identities and orders, terminal rank 246, post-block project counts, the canonical JSON bytes, and identity SHA-256 `6d5a8a713ddcb18ea70b8268c72e7aa2d5e1eb44bace81f1bd485c88907c0b95`. The informational cross-check in the Human-PI instruction also matched.

No subject repository was acquired or checked out. No Block-02 preparation, environment recipe or build, dependency installation, subject import/test, oracle, 3/3 screening, eligibility decision, pilot/final allocation, ErrPilot or other repair, or downstream model/API invocation occurred. The 60 cumulative admissions are metadata candidates, not eligible cases. All Block-02 preparation, materialization, and later execution require separate Human-PI authority and controlling identity gates. Automatic repository CI after an approved push, if triggered, is classified only under `CI_SIDE_EFFECT_BOUNDARY_V1.md` when its conditions hold.
