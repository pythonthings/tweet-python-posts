import os
import private
import tweepy
import sqlite3
import requests

def get_api(cfg):
    auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
    auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
    return tweepy.API(auth)

def send(msg):
    api = get_api(private.cfg)
    try:
        api.update_status(status=msg)
    except tweepy.error.TweepError as e:
        print("tweet dupe: {}".format(msg), e)

def send_img(msg, url_img):
    api = get_api(private.cfg)
    filename = 'temp.jpg'
    request = requests.get(url_img, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)

        api.update_with_media(filename, status=msg)
        os.remove(filename)
    else:
        print("Unable to download image")

def generate(source, uid):
    conn = sqlite3.connect('Posts.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM Posts WHERE Source = ? AND UID =?", (source, uid))
        data = cursor.fetchone()[0]
        # If this post doesn't exist, do not send a tweet
        if data == 0:
            return None
        else:
            cursor.execute("SELECT Twitter FROM Source WHERE Source = ?", (source,))
            handle = cursor.fetchone()[0]
            cursor.execute("SELECT * FROM Posts WHERE Source = ? AND UID =?", (source, uid))
            post = cursor.fetchone()
            title = post[1]
            link = post[2]

            msg = "{}\n{}\n{}\n{}".format(title, link, handle, "#python")

            if len(msg) > 140:
                title_length = 140 - len(link) - len(handle)
                msg = "{}\n{}\n{}".format(title[:title_length], link, handle)

            if len(msg) > 140:
                title_length = 140 - len(link)
                msg = "{}\n{}".format(title[:title_length], link)

            if len(msg) > 140:
                msg = "{}\n{}".format(link, handle)

            send(msg)


def generate_video(UID):
    conn = sqlite3.connect('Posts.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM Videos WHERE UID =?", (UID,))
        data = cursor.fetchone()[0]
        # If this post doesn't exist, do not send a tweet
        if data == 0:
            return None
        else:
            cursor.execute("SELECT * FROM Videos WHERE UID =?", (UID, ))
            post = cursor.fetchone()
            title = post[1]
            link = post[2]
            date = post[3]
            thumb = post[4]

            msg = "{}\n{}\n{}\n{}\n{}".format(title, link, date, "@PyvideoOrg", "#python")

            if len(msg) > 140:
                title_length = 140 - len(link)
                msg = "{}\n{}\n{}".format(title[:title_length], link, date)

            if len(msg) > 140:
                title_length = 140 - len(link)
                msg = "{}\n{}".format(title[:title_length], link)

            #send(msg)
            send_img(msg, thumb)