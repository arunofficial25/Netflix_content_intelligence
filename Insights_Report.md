# Netflix Data Analysis - Insights Report
## Task 1 - Cleaning
- Raw shape: (8790, 10)
- Placeholder 'Not Given' values: {'title': 1, 'director': 2588, 'country': 287}
- Duplicates removed: 4
- Clean shape: (8786, 15); remaining nulls: 0
- Standardised Type/Country/Rating (UR->NR), parsed dates, split duration, added audience & year_added. Output: `Netflix_Cleaned.csv`.
## Task 2 - Content Type
- Movies: **6,123 (69.7%)** | TV Shows: **2,663 (30.3%)** - movies outnumber shows ~2.3:1.
- Median movie length 98 min; 67% of shows have only 1 season.
## Task 3 - Countries
- Top 5: United States (3240), India (1056), United Kingdom (638), Pakistan (420), Canada (271).
- US alone = 38% of titles with known country; India = 12%. Top 3 = 58%.
- Insight: heavy US concentration; India/UK/Pakistan/Canada are key regional-content markets. Unknown country: 287 rows.
## Task 4 - Trends
- Peak release year: **2018** (1144 titles). Median release year: 2017.
- Catalogue is recent: 71% released 2015+.
- Titles added peaked in 2019 (2013); latest full-year YoY changes: {2019: 22.2, 2020: -6.7, 2021: -20.3}.
- 2021 data is partial, so the apparent decline is not a real drop.
## Task 5 - Ratings & Genres
- Ratings: TV-MA 36%, TV-14 25% - mature/teen focus.
- Top genres: International Movies, Dramas, Comedies, International TV Shows, Documentaries.
- Audience mix (% by type):
| type | Adults | Kids | Older Kids | Teens | Unrated |
| --- | --- | --- | --- | --- | --- |
| Movie | 46.7 | 7.2 | 13.5 | 31.3 | 1.3 |
| TV Show | 43.0 | 17.4 | 12.1 | 27.4 | 0.2 |
## Recommendations
1. Keep investing in Adult/Teen dramas & international content - core of the catalogue.
2. Grow TV Shows (only 30.3%), which drive recurring engagement.
3. Diversify beyond US via India/UK/Korea regional originals.
4. Improve metadata: 29% of directors and 3.3% of countries are missing.
