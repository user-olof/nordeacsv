import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
d = {"aa": [20, 30, 50, 55], "bb": [100, 50, 20, 15], "cc": [15, 20, 400, 10]}
df = pd.DataFrame(data=d)
g = sns.FacetGrid(data=df, height=10, xlim=(0, 10))
g.map_dataframe(sns.kdeplot, data=df, shade=True)
legend_names = dict(d.keys())
plt.legend(legend_names)
plt.show(block=True)

