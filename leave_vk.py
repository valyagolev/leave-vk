import os.path
import sys
import json
import requests

import vk_api

import render_posts


def get_paginated(community, method, **kwargs):
    data = {'profiles': [], 'groups': [], 'items': []}

    while True:
        print('offset', len(data['items']))
        more = method(count=50, offset=len(data['items']), **kwargs)

        if not more['items']:
            break

        for i in more['items']:
            for att in i.get('attachments', []):
                ensure_attachment(community, att)

        for k in data.keys():
            data[k] += more.get(k, [])

    data['profiles'] = {p['id']: p for p in data['profiles']}
    data['groups'] = {p['id']: p for p in data['groups']}

    return data


def get_all_posts(community):
    vk_session = vk_api.VkApi(token=os.environ['TOKEN'])

    vk = vk_session.get_api()

    posts_data = get_paginated(community, vk.wall.get, extended=1, domain=community)

    for post in posts_data['items']:
        if post['comments']['count']:
            post['comments']['data'] = get_paginated(
                community,
                vk.wall.getComments,
                post_id=post['id'],
                owner_id=post['owner_id'],
                thread_items_count=10,
                extended=1,
                need_likes=1,
            )
        # break

    return posts_data


def ensure_attachment(community, attachment):
    if attachment['type'] == 'photo':
        fname = 'attachments/%i.jpg' % attachment['photo']['id']
        full_fname = dir + fname

        if not os.path.isfile(full_fname):
            r = requests.get(
                max(attachment['photo']['sizes'], key=lambda s: s['height'])['url']
            )
            with open(full_fname, 'wb') as f:
                f.write(r.content)

        attachment['rendered'] = "![%s](%s)" % (attachment['photo']['text'], fname)

        return

    if attachment['type'] == 'link':
        attachment['rendered'] = "[%s](%s)" % (
            attachment['link']['title'],
            attachment['link']['url'],
        )
        return

    print("Not sure what to do with attachment type=%s" % attachment['type'])
    attachment['rendered'] = "```\n%s\n```" % json.dumps(attachment, indent=4)


if __name__ == '__main__':
    assert len(sys.argv) == 2, sys.argv
    community = sys.argv[-1]
    assert community.startswith("https://vk.com/")
    community = community.replace("https://vk.com/", "")

    dir = "docs/%s/" % community

    try:
        os.mkdir('docs')
    except FileExistsError:
        pass

    try:
        os.mkdir(dir)
    except FileExistsError:
        pass

    try:
        os.mkdir(dir + "attachments/")
    except FileExistsError:
        pass

    # post_data = get_all_posts(community)

    with open('%s/%s.json' % (dir, community), 'r') as f:
        post_data = json.load(f)

    with open('%s/%s.json' % (dir, community), 'w') as f:
        json.dump(post_data, f, indent=4)

    for p in post_data['items']:
        fname, content = render_posts.render_post(p, post_data)
        with open('%s/%s' % (dir, fname), 'w') as f:
            f.write(content)
