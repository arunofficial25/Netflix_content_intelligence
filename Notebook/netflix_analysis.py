"""Tasks 1-5 (Netflix dataset)"""
import json
from pathlib import Path

import pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
sns.set_theme(style="whitegrid", palette="Reds_r"); R="#E50914"

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "Dataset.csv"
CLEAN_DIR = ROOT / "data" / "cleaned"
CHARTS_DIR = ROOT / "charts"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

def save(n): plt.tight_layout(); plt.savefig(CHARTS_DIR / f"{n}.png", dpi=130); plt.close()

def markdown_table(frame):
    headers = [frame.index.name or "type", *frame.columns]
    rows = [[index, *values] for index, values in frame.iterrows()]
    lines = [
        "| " + " | ".join(map(str, headers)) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(map(str, row)) + " |" for row in rows)
    return "\n".join(lines)

# ---------- TASK 1: Cleaning ----------
df = pd.read_csv(RAW_PATH); log=[f"Raw shape: {df.shape}"]
obj = df.select_dtypes("object").columns
df[obj] = df[obj].apply(lambda s: s.str.strip())
ph = df[obj].apply(lambda s: s.str.lower().isin(["not given","unknown","n/a",""])).sum()
log.append(f"Placeholder 'Not Given' values: {ph[ph>0].to_dict()}")
df[["director","country"]] = df[["director","country"]].replace(r"(?i)^(not given|unknown|n/a)$", pd.NA, regex=True)
n=len(df); df = df.drop_duplicates(subset=["type","title","release_year","director","country"]); log.append(f"Duplicates removed: {n-len(df)}")
df["type"] = df["type"].str.title().replace({"Tv Show":"TV Show"})
df["country"] = df["country"].str.title().fillna("Unknown")
df["director"] = df["director"].fillna("Unknown")
df["rating"] = df["rating"].str.upper().replace({"UR":"NR"})
df["date_added"] = pd.to_datetime(df["date_added"], format="%m/%d/%Y", errors="coerce")
df["year_added"] = df.date_added.dt.year
df["duration_value"] = df.duration.str.extract(r"(\d+)").astype(int)
df["duration_unit"] = df.duration.str.extract(r"([A-Za-z]+)")[0].str.lower().str.rstrip("s")
aud = {"TV-Y":"Kids","TV-Y7":"Kids","TV-Y7-FV":"Kids","TV-G":"Kids","G":"Kids","TV-PG":"Older Kids","PG":"Older Kids",
       "TV-14":"Teens","PG-13":"Teens","TV-MA":"Adults","R":"Adults","NC-17":"Adults","NR":"Unrated"}
df["audience"] = df.rating.map(aud)
df["genres"] = df.listed_in.str.split(", ")
CLEANED_PATH = CLEAN_DIR / "Netflix_Cleaned.csv"
df.drop(columns="genres").to_csv(CLEANED_PATH, index=False)
dashboard_rows = [
    [
        row.title,
        int(row.type == "TV Show"),
        row.director,
        row.country,
        int(row.release_year),
        None if pd.isna(row.year_added) else int(row.year_added),
        row.rating,
        int(row.duration_value),
        row.listed_in.replace(", ", "|"),
        row.audience,
    ]
    for row in df.itertuples(index=False)
]
with (CLEAN_DIR / "dashboard_data.json").open("w", encoding="utf-8") as output:
    json.dump(dashboard_rows, output, ensure_ascii=False, allow_nan=False)
log.append(f"Clean shape: {df.shape}; remaining nulls: {int(df.drop(columns='genres').isna().sum().sum())}")

# ---------- TASK 2: Content type ----------
tc = df.type.value_counts(); pct = (tc/tc.sum()*100).round(1)
fig,ax = plt.subplots(1,2,figsize=(11,4.5))
sns.barplot(x=tc.index,y=tc.values,ax=ax[0],palette=[R,"#221f1f"]); ax[0].set_title("Movies vs TV Shows")
for i,v in enumerate(tc.values): ax[0].text(i,v,f"{v:,}",ha="center",va="bottom")
ax[1].pie(tc,labels=tc.index,autopct="%1.1f%%",colors=[R,"#221f1f"],textprops={"color":"w","weight":"bold"},startangle=90)
ax[1].set_title("Share of Catalogue"); save("t2_content_type")
dur = df[df.type=="Movie"].duration_value
fig,ax=plt.subplots(1,2,figsize=(11,4))
sns.histplot(dur,bins=30,color=R,ax=ax[0]); ax[0].set_title("Movie Duration (min)")
sns.countplot(x=df[df.type=="TV Show"].duration_value,color="#221f1f",ax=ax[1]); ax[1].set_title("TV Show Seasons"); save("t2_duration")

# ---------- TASK 3: Countries ----------
kc = df[df.country!="Unknown"]; top = kc.country.value_counts().head(10)
plt.figure(figsize=(9,5)); sns.barplot(y=top.index,x=top.values,color=R); plt.title("Top 10 Content-Producing Countries")
for i,v in enumerate(top.values): plt.text(v,i," "+str(v),va="center")
save("t3_top_countries")
ct = pd.crosstab(kc.country,kc.type).loc[top.index]
ct.plot(kind="barh",stacked=True,color=[R,"#221f1f"],figsize=(9,5)).invert_yaxis(); plt.title("Top Countries: Movies vs TV Shows"); save("t3_country_type")

# ---------- TASK 4: Trends ----------
yr = df.groupby(["release_year","type"]).size().unstack(fill_value=0); yr["Total"]=yr.sum(axis=1)
rec = yr.loc[1990:2021]
plt.figure(figsize=(10,5)); plt.plot(rec.index,rec.Movie,color=R,lw=2,label="Movies"); plt.plot(rec.index,rec["TV Show"],color="#221f1f",lw=2,label="TV Shows")
plt.axvline(rec.Total.idxmax(),ls="--",c="grey"); plt.title("Titles by Release Year (1990-2021)"); plt.legend(); save("t4_release_trend")
add = df.groupby(["year_added","type"]).size().unstack(fill_value=0)
add.plot(kind="bar",stacked=True,color=[R,"#221f1f"],figsize=(10,4.5)); plt.title("Titles Added to Netflix per Year"); save("t4_added_trend")
yoy = add.sum(axis=1).pct_change().mul(100).round(1)

# ---------- TASK 5: Ratings & Genres ----------
plt.figure(figsize=(10,4.5)); sns.countplot(data=df,x="rating",hue="type",order=df.rating.value_counts().index,palette=[R,"#221f1f"]); plt.title("Ratings by Content Type"); plt.xticks(rotation=45); save("t5_ratings")
g = df.explode("genres").reset_index(drop=True); tg = g.genres.value_counts().head(12)
plt.figure(figsize=(9,5)); sns.barplot(y=tg.index,x=tg.values,color=R); plt.title("Top 12 Genres"); save("t5_genres")
hm = pd.crosstab(g[g.genres.isin(tg.index[:10])].genres, g.audience); hm = hm.div(hm.sum(axis=1),axis=0)
plt.figure(figsize=(8,5)); sns.heatmap(hm,annot=True,fmt=".0%",cmap="Reds"); plt.title("Audience Mix by Genre"); save("t5_genre_audience")
ra = pd.crosstab(df.type,df.audience,normalize="index").mul(100).round(1)

# ---------- Report ----------
us,ind = top.iloc[0]/len(kc)*100, top.get("India",0)/len(kc)*100
rep = f"""# Netflix Data Analysis - Insights Report
## Task 1 - Cleaning
{chr(10).join('- '+l for l in log)}
- Standardised Type/Country/Rating (UR->NR), parsed dates, split duration, added audience & year_added. Output: `Netflix_Cleaned.csv`.
## Task 2 - Content Type
- Movies: **{tc['Movie']:,} ({pct['Movie']}%)** | TV Shows: **{tc['TV Show']:,} ({pct['TV Show']}%)** - movies outnumber shows ~{tc['Movie']/tc['TV Show']:.1f}:1.
- Median movie length {dur.median():.0f} min; {(df[df.type=='TV Show'].duration_value==1).mean()*100:.0f}% of shows have only 1 season.
## Task 3 - Countries
- Top 5: {', '.join(f'{k} ({v})' for k,v in top.head(5).items())}.
- US alone = {us:.0f}% of titles with known country; India = {ind:.0f}%. Top 3 = {top.head(3).sum()/len(kc)*100:.0f}%.
- Insight: heavy US concentration; India/UK/Pakistan/Canada are key regional-content markets. Unknown country: {(df.country=='Unknown').sum()} rows.
## Task 4 - Trends
- Peak release year: **{yr.Total.idxmax()}** ({yr.Total.max()} titles). Median release year: {int(df.release_year.median())}.
- Catalogue is recent: {(df.release_year>=2015).mean()*100:.0f}% released 2015+.
- Titles added peaked in {add.sum(axis=1).idxmax()} ({add.sum(axis=1).max()}); latest full-year YoY changes: {yoy.dropna().tail(3).to_dict()}.
- 2021 data is partial, so the apparent decline is not a real drop.
## Task 5 - Ratings & Genres
- Ratings: TV-MA {(df.rating=='TV-MA').mean()*100:.0f}%, TV-14 {(df.rating=='TV-14').mean()*100:.0f}% - mature/teen focus.
- Top genres: {', '.join(tg.head(5).index)}.
- Audience mix (% by type):
{markdown_table(ra)}
## Recommendations
1. Keep investing in Adult/Teen dramas & international content - core of the catalogue.
2. Grow TV Shows (only {pct['TV Show']}%), which drive recurring engagement.
3. Diversify beyond US via India/UK/Korea regional originals.
4. Improve metadata: {(df.director=='Unknown').mean()*100:.0f}% of directors and {(df.country=='Unknown').mean()*100:.1f}% of countries are missing.
"""
(ROOT / "Insights_Report.md").write_text(rep, encoding="utf-8")
print(rep)
