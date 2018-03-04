import time
import tweepy
import requests
import numpy as np
from twitter_credentials import *

class ButterRobot():
    def __init__(self):
        self.base_url = 'https://rickandmortyapi.com/api'
        self.categories = ['/character', '/location', '/episode']
        self.text = ['{} is seen in {} episodes.\nLocation: {}\nOrigin: {}\nSpecies: {}\nStatus: {}\nType: {}', 
                     '{} has {} residents.\nType: {}\nDimension: {}', 
                     '{} was aired on {}\nName: {}\nNumber of characters: {}']

    def request_url(self, entity_type, id_=''):
        """Make a request to the API using one of its main entity types ('/character' ... ) """
        r = requests.get(''.join([self.base_url, entity_type, ''.join(['/', str(id_)])]))
        return r.json()
    
    def random_selection(self, elements):
        return np.random.choice(elements)
    
    def get_info(self, category, response):
        if category == self.categories[0]:
            return self.text[0].format(response['name'], len(response['episode']), response['location']['name'], response['origin']['name'], response['species'], response['status'], response['type'])
        elif category == self.categories[1]:
            return self.text[1].format(response['name'], len(response['residents']), response['type'], response['dimension'])
        else:
            return self.text[2].format(response['episode'], response['air_date'], response['name'], len(response['characters']))

def main():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    morty_bot = ButterRobot()

    nonstop_posting = True
    
    while nonstop_posting:
        # Randomly select between posting info about characters, locations or episodes
        category = morty_bot.random_selection(morty_bot.categories)
        results = morty_bot.request_url(category)
        
        # Number of IDs in that category
        ids = results['info']['count']
        
        # Randomly select and ID
        id_ = morty_bot.random_selection(ids)
        response = morty_bot.request_url(category, id_)
        
        try:
            tweet = '\n'.join(['#RickandMorty info:', morty_bot.get_info(category, response)])
            api.update_status(tweet)
        except tweepy.error.TweepError as e:
            print(e)
            old_post = [status.id for status in tweepy.Cursor(api.user_timeline).items() if status.text == tweet][0]
            api.destroy_status(old_post)
            api.update_status(tweet)
            
        time.sleep(15*60)

if __name__ == '__main__':
    main()