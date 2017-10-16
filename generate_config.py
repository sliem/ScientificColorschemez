import tweepy
from requests_oauthlib.oauth1_session import TokenRequestDenied

def main():
    print('To setup Scientific Colorschemez you need access to the Twitter API. This entails setting up an Twitter app, and authorise access for this code.\n')

    print('Setting up an Twitter app:\n\t1. Go to https://apps.twitter.com/\n\t2. Create new app.\n\t3. Fill in details.\n')
    consumer_key = input('Type the newly generated consumer key: ')
    consumer_secret = input('Type the newly generated consumer secret: ')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
   
    try:
        auth_url = auth.get_authorization_url()
    except tweepy.TweepError as e:
        print(e)
        exit(1)
    
    print('To grant your newly created Twitter app access to your twitter account please visit this url:\n\t' + auth_url)
    
    verifier = input('Type the generate validation code: ')

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError as e:
        print(e)
        exit(1)

    api = tweepy.API(auth)

    print('The details are:')
    print('consumer_key        = "%s"' % consumer_key)
    print('consumer_secret     = "%s"' % consumer_secret)
    print('access_token        = "%s"' % auth.access_token)
    print('access_token_secret = "%s"' % auth.access_token_secret)


if __name__ == '__main__':
    main()
