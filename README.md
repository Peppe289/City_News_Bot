# News Bot

This code is used to pool my municipality's site in a completely autonomous way. Takes new news via the site's ajax calls and analyzes the response and creates a message to send in a telegram chat using the keys (chat_id and token_bot).

# How work?

The ajax requests provide 3 pieces of news for each cluster. It means that if I request page 0 it provides me with the latest 3 news. If I request page 1 (with request 3) it provides me with the last 6 and if I request page 2 (request 6) it provides me with the last 9. Therefore in multiples of 3.

This bot sees the last 3 news clusters and saves them in a database. If the news has already been posted then it ignores it, otherwise it posts it and saves it in the database for future checking. The bot itself is not able to do pooling autonomously and periodically, which is why you should set up a cron or a daemon that starts it periodically.

# How to use?

Very simple, put the keys you are interested in in the environment of your system and start it.
Like:

```sh
env TG_TOKEN="7082907773:AAGx-50TmQr_v7KAGsR0H7FSE0FcFA9clR8" CHAT_ID="519932241" python3 main.py
```

or with export:

```sh
export TG_TOKEN="7082907773:AAGx-50TmQr_v7KAGsR0H7FSE0FcFA9clR8"
export CHAT_ID="519932241"
python3 main.py
```

# Set up

Make sure you have installed the dependencies with python. You should need to install `requests`:

```sh
pip install requests
```
