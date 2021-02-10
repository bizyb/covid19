import tweepy
import time
from pymongo import MongoClient

db_client = MongoClient(port=27017)
db = db_client["db"]
collection = db["timeslots"]
registration_link = "https://www.walgreens.com/findcare/vaccination/covid-19/appointment"

def tweet():
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler("camlOUeYcz8jJ1rZgUO6i9IGt", "wJzQOX3ozwPuSjI80OGyLATuh1GDBTX1fzMzIjhTOuUBHplSU3")
    auth.set_access_token("1344712833532047360-bb9s2esVa5VQdFjcAPbn3sug7PjBAe",
                          "5CFFALuJjFfeX2ut9QsbkehZy8hX3EQiBYFfZF6tuR6HG")
    api = tweepy.API(auth)
    while True:
        cursor = collection.find({"tweeted": True})
        for c in cursor:
            status = """{},{} - {}: {} slots for {}\n\nRegister here: {}""".format(
                c.get("city"),
                c.get("state"),
                c.get("provider"),
                c.get("num_slots"),
                c.get("day_available"),
                registration_link
            )
            api.update_status(status)
            print "New Status: ", status
            collection.update_one({"_id": c.get('_id')}, {"$set": {"tweeted": True}})

        # Sleep ofr 5 minutes
        time.sleep(5 * 60)


if __name__ == '__main__':
    tweet()
