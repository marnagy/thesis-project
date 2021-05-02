import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="darkgrid")

dots = sns.load_dataset("dots").query("align == 'dots'")
palette = sns.cubehelix_palette(light=.7, n_colors=6)

sns.relplot(x="time", y="firing_rate",
           hue="coherence", size="choice",
           palette=palette,
           kind="line", data=dots)

plt.show()