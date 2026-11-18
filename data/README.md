# Data provenance

The original report identifies Baseball Reference as the source of the Yankees
schedule and attendance CSV exports for 2022-2025. The supplied exports are
preserved in `raw/`; they include away games, which the analysis filters out.

The home/away column is read by pandas as `Unnamed: 4`: blank means home and `@`
means away. Rows without numeric attendance are dropped. Doubleheader markers
are removed from dates, while the games remain separate observations.

The resulting sample has 237 training games (2022-2024) and 80 evaluation games
(2025), rather than every nominal home game. Missing attendance and export
coverage should be audited before extending the study.

These are the historical files supplied with the project, not a live feed.
Source ownership is retained by its respective owners; no third-party data
license is granted by this repository. Export dates and redistribution terms
were not recorded in the original files.
