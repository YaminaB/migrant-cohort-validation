
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("output/annual_migrant_counts.csv.gz")

# Loop through each unique measure
for measure_name in df["measure"].unique():
    df_filtered = df[df["measure"] == measure_name]
    
    # Try to infer the column to use as hue (grouping)
    group_columns = [col for col in df_filtered.columns if col not in ["interval_start", "numerator", "denominator", "value", "measure"]]
    
    if len(group_columns) == 1:
        hue = group_columns[0]
    else:
        print(f"Skipping {measure_name} (couldn't determine a single subgroup column)")
        continue

    # Create the lineplot
    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=df_filtered,
        x="interval_start",
        y="numerator",
        hue=hue,
        marker="o"
    )
    
    plt.title(f"{measure_name.replace('_', ' ').title()} Over Time")
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save plot
    plot_path = f"output/plots/{measure_name}.png"
    plt.savefig(plot_path)
    plt.close()