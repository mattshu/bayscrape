"""proxies.py."""
import json
import os
import time

from soup import get_soup

PROXY_SOURCE = "https://piratebayproxy.info/"
DB_FILE = "pb_proxies.db"


def _db_file_fresh(path) -> bool:  # noqa: WPS221
    """Check if database is less than 24 hours old and has data."""
    return (
        os.path.exists(path)
        and time.time() - os.path.getmtime(path) < 24 * 60 * 60
        and os.stat(path).st_size > 0
    )


def _proxy_valid(url) -> bool:
    """Return True if the proxy url is valid by checking for a search bar."""
    web_data = get_soup(url)
    search_bar = web_data.find("input", class_="https_form")
    return search_bar is not None


def get_proxies() -> list:
    """Extract recent proxies from local file, otherwise fetch updated list."""
    if _db_file_fresh(DB_FILE):
        with open(DB_FILE, "r") as fresh_db:
            links = json.load(fresh_db)
    else:
        with open("pb_proxies.db", "w") as new_db:
            soup = get_soup(PROXY_SOURCE)
            links = [td.a["href"] for td in soup.find_all("td", class_="site")]
            json.dump(links, new_db)
    return links
