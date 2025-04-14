import pandas as pd

data = pd.read_csv("output/dataset.csv.gz")

fig = data.year_of_birth.plot.hist().get_figure()
fig.savefig("output/report.png")