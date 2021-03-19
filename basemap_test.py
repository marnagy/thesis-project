import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

m = Basemap(projection='mill')
    
m.drawcoastlines()
m.fillcontinents()

plt.title("Basemap Tutorial")
plt.show()

