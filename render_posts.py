import os
import sys
import json
import datetime

import vk_api
import pytz
import re
import requests

import render_posts


def timestamp_to_moskow_datetime(ts):
    local_tz = pytz.timezone('Europe/Moscow')
    dt = datetime.datetime.utcfromtimestamp(ts).replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(local_tz)


def render_comment(comment, ident):
    ident_whitespace = " " * ident * 4
    ident_next_whitespace = " " * (ident + 1) * 4

    content = "%s  * %s\n%sAuthor: %s, Date: %s, Likes: %i*\n\n" % (
        ident_whitespace,
        comment['text'].replace("\n", "\n" + ident_next_whitespace),
        ident_next_whitespace,
        comment['from_id'],
        timestamp_to_moskow_datetime(comment['date']).strftime('%Y-%m-%d %H:%M'),
        0,
    )

    if comment.get('thread') and comment['thread']['items']:
        print("thread")
        for reply in comment['thread']['items']:
            content += render_comment(reply, ident + 1)

    return content


def render_post(post, data):
    print(post)
    dt = timestamp_to_moskow_datetime(post['date'])
    dt_fname = dt.strftime('%Y-%m-%d %H-%M')
    title = ' '.join(post['text'].split()[:5])
    title = re.sub(r'[^ а-яa-z\.]', "", title, flags=re.I)
    fname = '%s %s.txt' % (dt_fname, title)

    content = "# %s...\n\n%s\n\n" % (title, post['text'])

    content += "\n".join(
        [
            "Date: %s" % dt.strftime('%Y-%m-%d %H:%M'),
            "Likes: %i" % post['likes']['count'],
            "Comments: %i" % post['comments']['count'],
            "Reposts: %i" % post['reposts']['count'],
            "Views: %i" % post['views']['count'],
            "Original URL: https://vk.com/wall-%i_%i" % (-post['owner_id'], post['id']),
        ]
    )
    content += "\n\n"

    for att in post.get('attachments', []):
        content += "%s\n\n" % att['rendered']

    comments = post['comments'].get('items')
    if comments:
        content += "\n\n" + "-" * 20 + "\n\n"
        content += "\n".join(render_comment(c, 0) for c in comments)

    return fname, content
