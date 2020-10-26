"""Container class for user comments."""


class Comment(object):
    """Build a comment based on TPB's formatting."""

    def __init__(self, comment_soup):
        self.author = comment_soup.a.get_text()
        date = comment_soup.get_text().split()[2:4]
        self.date = "{0} {1}".format(date[1], date[0])
        raw_text = comment_soup.div.get_text()
        body = raw_text.split("\n")[1:-1]
        self.body = "\n".join(body)
