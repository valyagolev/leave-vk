import re
import utils


def render_comment(comment, ident, cdata, data):
    ident_whitespace = " " * ident * 4
    ident_next_whitespace = " " * (ident + 1) * 4

    if not comment.get('deleted'):
        try:
            author = cdata['profiles'][str(comment['from_id'])]
            name = author['first_name'] + ' ' + author['last_name']
        except KeyError:
            name = comment['from_id']

        content = "%s  * %s\n%sAuthor: %s, Date: %s, Likes: %i\n\n" % (
            ident_whitespace,
            comment['text'].replace("\n", "\n" + ident_next_whitespace),
            ident_next_whitespace,
            name,
            utils.timestamp_to_moscow_datetime(comment['date']).strftime('%Y-%m-%d %H:%M'),
            comment['likes']['count'],
        )
    else:
        content = "%s  * %s\n%sAuthor: ?, Date: %s, Likes: ?\n\n" % (
            ident_whitespace,
            "(deleted comment)",
            ident_next_whitespace,
            utils.timestamp_to_moscow_datetime(comment['date']).strftime('%Y-%m-%d %H:%M'),
        )

    if comment.get('thread') and comment['thread']['items']:
        for reply in comment['thread']['items']:
            content += render_comment(reply, ident + 1, cdata, data)

    return content


def render_post(post, data):
    dt = utils.timestamp_to_moscow_datetime(post['date'])
    dt_fname = dt.strftime('%Y-%m-%d %H-%M')
    title = ' '.join(post['text'].split()[:5])
    title = re.sub(r'[^ а-яa-z\.]', "", title, flags=re.I)
    fname = ('%s %s' % (dt_fname, title))[:220] + ".md"

    content = "# %s...\n\n%s\n\n" % (title, post['text'])

    for att in post.get('attachments', []):
        content += "%s\n\n" % att['rendered']

    content += "\n".join(
        "    " + s
        for s in [
            "Date: %s" % dt.strftime('%Y-%m-%d %H:%M'),
            "Likes: %i" % post['likes']['count'],
            "Comments: %i" % post['comments']['count'],
            "Reposts: %i" % post['reposts']['count'],
            "Views: %i" % post['views']['count'] if 'views' in post else None,
            "Original URL: https://vk.com/wall-%i_%i" % (-post['owner_id'], post['id']),
        ]
        if s
    )
    content += "\n\n"

    comments = post['comments'].get('data', {}).get('items')
    if comments:
        content += "\n\n" + "-" * 20 + "\n\n"
        content += "\n".join(
            render_comment(c, 0, post['comments']['data'], data) for c in comments
        )

    return fname, content
