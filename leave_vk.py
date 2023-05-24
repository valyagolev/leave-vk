import os.path
import sys
import json
import requests

import vk_api

import render_content
import utils

vk_session = vk_api.VkApi(token=os.environ['TOKEN'])
vk = vk_session.get_api()


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


def download_album(community, owner_id, album):
    # photos = get_paginated(
    #                 community,
    #                 ,
    #                 ownder_id=attachment['album']['owner_id'],
    #                 )
    data = {'items': []}

    while True:
        print('album offset', len(data['items']))
        more = vk.photos.get(
            count=50, offset=len(data['items']), owner_id=owner_id, album_id=album['id']
        )

        if not more['items']:
            break

        for i in more['items']:
            t, p = ensure_photo('albums/%s_%s' % (album['id'], album['title']), i)
            data['items'].append((t, p))

    return data['items']


def get_community_info(community):
    return vk.groups.getById(group_id=community)


def get_all_posts(community):

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


def get_all_albums(community, community_id):
    albums_data = get_paginated(community, vk.photos.getAlbums, extended=1, domain=community, owner_id=-community_id)

    for album in albums_data['items']:
        photos = download_album(
            community,
            owner_id=album['owner_id'],
            album=album,
        )
        print('album with ID %s downloaded' % album['id'])


def ensure_photo(photoDir, photo):
    full_dir = '%s/%s' % (dir, photoDir)
    fname = '%s/%s_%i.jpg' % (photoDir, utils.timestamp_to_moscow_datetime(photo['date']).strftime('%Y-%m-%d %H-%M'), photo['id'])
    full_fname = '%s/%s' % (dir, fname)

    try:
        os.mkdir(full_dir)
    except FileExistsError:
        pass

    if not os.path.isfile(full_fname):
        r = requests.get(max(photo['sizes'], key=lambda s: s['height'])['url'])
        with open(full_fname, 'wb') as f:
            f.write(r.content)

    return (photo['text'], fname)


def ensure_doc(doc):
    fname = 'attachments/%i.%s' % (doc['id'], doc['ext'])
    full_fname = dir + fname

    if not os.path.isfile(full_fname):
        r = requests.get(doc['url'])
        with open(full_fname, 'wb') as f:
            f.write(r.content)

    return (doc['title'], fname)


def ensure_attachment(community, attachment):
    if attachment['type'] == 'photo':
        text, fname = ensure_photo('attachments', attachment['photo'])
        attachment['rendered'] = "![%s](%s)" % (text, fname)

        return

    if attachment['type'] == 'link':
        attachment['rendered'] = "[%s](%s)" % (
            attachment['link']['title'],
            attachment['link']['url'],
        )
        return

    if attachment['type'] == 'album':
        photos = download_album(
            community,
            owner_id=attachment['album']['owner_id'],
            album=attachment['album'],
        )
        attachment['rendered'] = "Album: %s\n" + "\n".join(
            "![%s](%s)" % (t, f) for (t, f) in photos
        )
        return

    if attachment['type'] == 'doc':
        t, f = ensure_doc(attachment['doc'])
        attachment['rendered'] = "Doc: ![%s](%s)" % (t, f)
        return

    print("Not sure what to do with attachment type=%s" % attachment['type'])
    print(repr(attachment))
    # assert False
    attachment['rendered'] = "```\n%s\n```" % json.dumps(attachment)


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

    try:
        os.mkdir(dir + "albums/")
    except FileExistsError:
        pass

    community_data = get_community_info(community)

    with open('%s/%s.json' % (dir, community), 'w', encoding = "utf-32") as f:
        json.dump(community_data, f, indent=4)

    if community_data[0]:
        community_id = community_data[0]['id']
        album_data = get_all_albums(community, community_id)

        with open('%s/%s_albums.json' % (dir, community), 'w', encoding = "utf-32") as f:
            json.dump(album_data, f, indent=4)

    post_data = get_all_posts(community)

    # with open('%s/%s.json' % (dir, community), 'r') as f:
    #     post_data = json.load(f)

    with open('%s/%s_wall.json' % (dir, community), 'w') as f:
        json.dump(post_data, f, indent=4)

    for p in post_data['items']:
        fname, content = render_content.render_post(p, post_data)
        with open('%s/%s' % (dir, fname), 'w', encoding = "utf-32") as f:
            f.write(content)
