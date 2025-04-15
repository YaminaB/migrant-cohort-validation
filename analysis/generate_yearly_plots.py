
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("output/annual_migrant_counts.csv.gz")

df_filtered = df[df["measure"] == "migrant_sex"]

sns.lineplot(
    data = df_filtered,
    x = "interval_start",
    y = "numerator", 
    hue = "sex"
)

plt.title("Number of migrants over time")
plt.xlabel("Date")
plt.ylabel("Number")
plt.xticks(rotation=45)
plt.tight_layout()

# Save to outputs folder
plt.savefig("output/measure_plot.png")