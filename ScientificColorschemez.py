import tweepy
import numpy as np
import matplotlib.pyplot as plt

class Colorschemez:
    def __init__(self, status):
        """Constructs a Colorscheme from a @colorschemez tweet.
        
        Arguments:
        status -- a @colorschemez tweet in a Tweepy status object.
        """

        c = status.text.split('\n')
        c[-1] = ' '.join(c[-1].split()[:-1])
        self.colornames = c

        self.url = status._json['entities']['media'][0]['url']

        self.image_url = status._json['entities']['media'][0]['media_url_https']
        
        self.colors = self._extract_colors(
            self._retrieve_image(self.image_url)
        )


    @classmethod
    def latest(cls):
        """Retrieves the latest @colorschemez tweet and returns the corresponding Colorscheme."""
        latest_tweet = retrieve_tweets(count=1)
        return cls(latest_tweet[0])


    def _extract_colors(self, fp):
        """Extract the three colors from a @colorschemez image and return their hex code.

        Uses KMeans clustering to find the colors as @colorschemez images include color transitions which makes the raw sRGB codes unreliable.

        Arguments:
        fp -- A filename (string), pathlib.Path object or a file object. Accepts whatever PIL's Image.open() accepts.
        """
        from PIL import Image
        from sklearn.cluster import KMeans

        im = Image.open(fp)
        self.image = im

        # Extract the sRGB codes for the colors in the image.
        # The output of getcolors is unique colors and the number of
        # pixel with that color. We 'uncompress' this in order for the 
        # K-means clustering to be able to account for observation
        # weights.
        sRGB = []
        for w, srgb in im.getcolors(maxcolors=512*512):
            sRGB += (w//512) * [srgb]

        kmeans = KMeans(n_clusters=3).fit(sRGB)

        center_sRGB = np.round(kmeans.cluster_centers_).astype(np.int)

        to_hex = lambda x: '#'+''.join(['{:02x}'.format(n) for n in x])

        return [to_hex(c) for c in center_sRGB]


    def _retrieve_image(self, url):
        """Downloads an image and returns it as a bytestream.

        Arguments:
        url - the url of the image.
        """
        import requests
        from io import BytesIO 
        r = requests.get(url) # TODO check failure
        return BytesIO(r.content)


    def example_plot(self, ax):
        """Construct an example plot from the Colorscheme.

        Arguments:
        ax -- matplotlib axes object to draw the example plot on.
        """
        x = np.linspace(-1, 1, 100)
        functions = [np.sin, lambda x: np.cos(x)-0.30, lambda x: 0.5*x]

        for f, c in zip(functions, self.colors):
            ax.plot(x, f(x), c=c, lw=6)

        ax.imshow(np.asarray(self.image),
                  extent=(0.3, 1.0, -0.8, -0.1))
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-0.9, 1.1)
        
        ax.text(-1.05, 1.05, '\n'.join(self.colornames),
                horizontalalignment='left',
                verticalalignment='top')

        ax.set_xlabel('Colors by @colorschemez: %s' % self.url)


def retrieve_tweets(count):
    """Retrieve the user timeline of @colorschemez and return it as list of Tweepy Status objects.

    Arguments:
    count -- the number of tweets to retrieve.
    """
    import config as cfg

    auth = tweepy.OAuthHandler(cfg.consumer_key, cfg.consumer_secret)
    auth.set_access_token(cfg.access_token, cfg.access_token_secret)

    api = tweepy.API(auth)

    valid_tweets = []
    oldest_tweet_checked_id = None
    while True:
        if len(valid_tweets) == count:
            break
        
        if oldest_tweet_checked_id == None:
            tweets = api.user_timeline(screen_name='colorschemez',
                                       count=count-len(valid_tweets))
        else:
            tweets = api.user_timeline(screen_name='colorschemez',
                                       count=count-len(valid_tweets),
                                       max_id=oldest_tweet_checked_id)

        oldest_tweet_checked_id = tweets[-1].id
        valid_tweets += list(filter(valid_status, tweets))

    return valid_tweets 


def valid_status(status):
    """ Checks if a status fullfills our assumptions. Return True if it does, False if it doesn't.

    Arguments:
    status -- a Tweepy Status object.
    """
    # The tweet should consist of three lines, name of the colours.
    if len(status.text.split('\n')) != 3:
        return False

    json = status._json
    # The tweet should include one image.
    if 'media' not in json['entities']:
        return False
    if len(json['entities']['media']) != 1:
        return False
    media = json['entities']['media'][0]
    if 'url' not in media:
        return False
    if 'media_url_https' not in media:
        return False
    if not valid_url(media['url']):
        return False
    if not valid_url(media['media_url_https']):
        return False

    return True


class ColorschemezError(Exception):
    def __init__(self, message):
        self.message = message


def valid_url(url):
    """ Check that an url is valid.
    
    Uses Django's regex. """
    import re
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return False if regex.match(url) is None else True


if __name__ == '__main__':
    """Plot the last 16 color schemes as a grid.
    Saves to results to ./sixteen.png.
    """
    n = 4

    tweets = retrieve_tweets(count=n**2)

    fig, axes = plt.subplots(ncols=n, nrows=n, figsize=(5*n, 5*n))
    for ax, tweet in zip(axes.flatten(), tweets):
        cs = Colorschemez(tweet)
        cs.example_plot(ax)

    fig.savefig('sixteen.png', dpi=200)
