import random

def random_gif():
    gif_collection = (("https://media.giphy.com/media/cjzkCDL3jZTZB6ki1B/giphy.gif"), ("https://media.giphy.com/media/O6Hw3wYDqzUis/giphy.gif"), ("https://media.giphy.com/media/l3q2K5jinAlChoCLS/giphy.gif"), ("https://media.giphy.com/media/pPhyAv5t9V8djyRFJH/giphy.gif"), ("https://media.giphy.com/media/xuDHhHcCR0rew/giphy.gif"), ("https://media.giphy.com/media/QNFhOolVeCzPQ2Mx85/giphy.gif"), ("https://media.giphy.com/media/zOvBKUUEERdNm/giphy.gif"), ("https://media.giphy.com/media/dAJlks3eQE8tBOUbJy/giphy.gif"), ("https://media.giphy.com/media/vVF4udRiZCmqY/giphy.gif"), ("https://media.giphy.com/media/w6I8dFBGcJub6/giphy.gif"), ("https://media.giphy.com/media/12upF0r28LZuTK/giphy.gif"), ("https://media.giphy.com/media/oOxBQwNqGwxeWLDF6A/giphy.gif"), ("https://media.giphy.com/media/JSueytO5O29yM/giphy.gif"), ("https://media.giphy.com/media/glmRyiSI3v5E4/giphy.gif"), ("https://media.giphy.com/media/CDJo4EgHwbaPS/giphy.gif"), ("https://media.giphy.com/media/Qw4X3FGaZ6y9cLu1EwE/giphy.gif"), ("https://media.giphy.com/media/3ohc1ffY03hnhRUyUU/giphy.gif"), ("https://media.giphy.com/media/xTiTnHXbRoaZ1B1Mo8/giphy.gif"), ("https://media.giphy.com/media/9WHE2bo5Na9Gg/giphy.gif"), ("https://media.giphy.com/media/6vYqaGt6N05GM/giphy.gif"), ("https://media.giphy.com/media/M7oKkaur56EFO/giphy.gif"), ("https://media.giphy.com/media/1gXiBFTkANAddVgBKn/giphy.gif"), ("https://media.giphy.com/media/4QFeb79yL3E3xgTjiO/giphy.gif"))

    num = random.randint(0, len(gif_collection) - 1)
    return gif_collection[num]

def random_location_message():
    message_locations = (("I got it, thank you 😜"), ("Now I know where you are 😈😈"), ("Location stored"), ("Thank you, I won't tell FBI. I promise"), ("Oh, what a beatuiful place 😄"), ("👌🏼👌🏼👌🏼"), ("If you want to know the nearest station to your location just say it to me with:  /nearest_station 🤗🤗"))

    num = random.randint(0, len(message_locations) - 1)
    print(num)
    return message_locations[num]
