import pandas as pd

df = pd.read_csv("output/full_study_cohort.csv.gz")

# year of birth

bins = [1925, 1945, 1965, 1985, 2005, 2025]
labels = [
    "1925-1945", "1946-1965", "1966-1985",
    "1986-2005", "2006-2025"]

df["year_band"] = pd.cut(df["year_of_birth"], bins=bins, labels=labels, right=True)

print(df)


#summary = {
#    "sex": df["sex"].value_counts(normalize=True).round(2) * 100,
#    "Year of birth": df[]
#    "imd_decile": df["imd_decile"].value_counts().sort_index()
#}

print(summary)