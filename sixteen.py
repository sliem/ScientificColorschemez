from ScientificColorschemez import Colorschemez, retrieve_tweets
import matplotlib.pyplot as plt

n = 4

tweets = retrieve_tweets(count=n**2)

fig, axes = plt.subplots(ncols=n, nrows=n, figsize=(5*n, 5*n))
for ax, tweet in zip(axes.flatten(), tweets):
    cs = Colorschemez(tweet)
    cs.example_plot(ax)

fig.savefig('sixteen.png', dpi=200, bbox_inches='tight')