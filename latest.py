from ScientificColorschemez import Colorschemez
import matplotlib.pyplot as plt

cs = Colorschemez.latest()

for name, hexcode in zip(cs.colornames, cs.colors):
    print('%s: %s' % (hexcode, name))

fig, ax = plt.subplots()
cs.example_plot(ax)
fig.savefig('latest.png', dpi=200, bbox_inches='tight')
