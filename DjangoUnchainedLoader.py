#!/usr/bin/env python

# Written by Raahul Seshadri (http://crossplatform.net)
# for the TutsPlus course "Django Unchained" by
# Christopher Roach.
#
# Revision 2: Now also picks up dates from HackerNews

# Set up the django environment
import os
import sys
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hackernews.settings")


import requests
import re
from django.contrib.auth.models import User
from stories.models import Story
from django.utils.timezone import utc
import datetime


def getHomepageContents():
    r = requests.get('http://news.ycombinator.com')
    if r.status_code == 200:
        return r.text
    else:
        raise Exception('Could not download HackerNews homepage contents.')


# As (url, title, points, user)
def getAllStories(contents):
    regex = re.compile(r'<td class="title"><a href="([^\"]*)">([^<]*)</a><span class="comhead">[^<]*</span></td></tr><tr><td colspan=2></td><td class="subtext"><span id=score_[0-9]+>([0-9]+) points</span> by <a href="user\?id=[^"]+">([^"]+)</a> ([0-9]+) (minute|minutes|hour|hours|day|days)')
    return regex.findall(contents)


stories = getAllStories(getHomepageContents())

for my_story in stories:
    url = my_story[0]
    title = my_story[1]
    points = int(my_story[2])
    user = my_story[3]
    timeValue = int(my_story[4])
    timeName = my_story[5]
    timeNow = datetime.datetime.utcnow().replace(tzinfo=utc)

    if timeName == 'hour' or timeName == 'hours':
        createTime = timeNow - datetime.timedelta(hours=timeValue)
    elif timeName == 'minute' or timeName == 'minutes':
        createTime = timeNow - datetime.timedelta(minutes=timeValue)
    else:
        createTime = timeNow - datetime.timedelta(days=timeValue)

    existingUser = User.objects.filter(username=user)[:1]
    if existingUser:
        existingUser = existingUser[0]
    else:
        existingUser = User(username=user, password='12345')
        existingUser.save()

    # Check if story already present
    existingStory = Story.objects.filter(url=url)[:1]
    if not existingStory:
        existingStory = Story()
    else:
        existingStory = existingStory[0]

    existingStory.title = title
    existingStory.url = url
    existingStory.points = points
    existingStory.created_at = createTime
    existingStory.moderator = existingUser
    existingStory.save()

    print title, '::', existingUser.username, '::', points
