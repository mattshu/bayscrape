"""Responsible for fetching and processing raw soup/HTML data and returning useful data."""
from contextlib import closing
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

from bsutils import strip_unicode
from color import Color, style
from comment import Comment


def get_soup(url, delay=5) -> BeautifulSoup:
    """Get content at `url` by making HTTP GET request."""
    try:
        with closing(requests.get(url, stream=True, timeout=delay)) as response:
            if _is_good_response(response):
                return BeautifulSoup(response.content, "html.parser")
            return BeautifulSoup()
    except requests.RequestException:  # includes timeout
        return BeautifulSoup()


def _is_good_response(response) -> bool:
    """Return True if there is a valid HTML response."""
    content_type = response.headers["Content-Type"]
    return content_type is not None and content_type.find("html") > -1


def process_details_soup(torrent_url) -> (dict, str, list):
    """Build the structure of the details table."""
    soup = get_soup(torrent_url)
    torrent_details_header = _process_details_header(soup)
    torrent_description = "\n".join(soup.pre.get_text().splitlines())
    torrent_description = torrent_description.replace("\t", " " * 4)  # Replace literal that causes errors in the table
    torrent_details_comments = _process_details_comments(soup)
    return torrent_details_header, torrent_description, torrent_details_comments


def _process_details_header(soup) -> dict:
    """Helper to process details."""
    header_right, header_left = soup.find_all("dl")
    torrent_details_columns = header_left.get_text().splitlines() + header_right.get_text().splitlines()
    torrent_details_columns = [elem for elem in torrent_details_columns if elem]  # Remove blank elements
    torrent_name = soup.find(id="title").get_text()
    torrent_details_header = {"name": strip_unicode(torrent_name)}
    detail_headers = {
        "Type:",
        "Files:",
        "Size:",
        "Uploaded:",
        "By:",
        "Seeders:",
        "Leechers:",
        "Comments",
        "Info Hash:",
    }
    # Format HTML data into a dict
    for header in detail_headers:
        if header in torrent_details_columns:
            key = header.replace(":", "").lower()
            value_index = torrent_details_columns.index(header) + 1
            header_value = torrent_details_columns[value_index].replace("\xa0", " ").strip()
            torrent_details_header[key] = header_value
    if "size" in torrent_details_header:
        # Trim byte count of size info
        size = torrent_details_header.get("size").split()
        torrent_details_header["size"] = " ".join(size[:2])  # noqa: WPS529
    magnet_url = soup.find("div", class_="download").a.get("href")
    torrent_details_header["magnet_url"] = magnet_url
    return torrent_details_header


def _process_details_comments(soup) -> list:
    """Helper to process comments."""
    comments = []
    comments_soup = soup.select("div[id^='comment-']")
    if comments_soup:
        for comment in comments_soup:
            comments.append(Comment(comment))
    return comments


def process_results_soup(result_url) -> list:
    """Extract torrent results."""
    soup = get_soup(result_url)
    table = soup.find_all("tr")[1:]
    torrent_list = []
    for row in table:
        # Last row of results table
        if not row.td.has_attr("class"):
            continue
        torrent_data = _extract_row_details(row)
        torrent_list.append(torrent_data)
    return torrent_list


def _extract_row_details(soup) -> dict:
    """Helper to extract row information."""
    author_name = _extract_author_name(soup)
    links = soup.find_all("a")
    torrent_pb_url = links[2]["href"]
    magnet_url = links[3]["href"]
    torrent_name = strip_unicode(links[2].get_text().strip())
    description = soup.find("font", class_="detDesc")
    upload_date = _extract_upload_date(description)
    torrent_size = " ".join(description.get_text().split()[4:6])[:-1]
    up, down = _extract_bandwidth_data(soup)
    return {
        "name": torrent_name,
        "date": upload_date,
        "author": author_name,
        "size": torrent_size,
        "url": torrent_pb_url,
        "magnet_url": magnet_url,
        "ul": up,
        "dl": down,
    }


def _extract_bandwidth_data(soup) -> tuple:
    """Helper to extract seeder/leecher information."""
    bandwidth_data = soup.find_all("td", {"align": "right"})
    if bandwidth_data:
        up, down = [int(_.get_text()) for _ in bandwidth_data]
    else:
        up, down = 0, 0
    return up, down


def _extract_upload_date(soup) -> str:
    """Helper to extract and format the submission date."""
    upload_date = soup.get_text().split(",")[0].split()[1:]
    if upload_date[0] == "Today":
        upload_date = "Today"
    elif "Y-day" in upload_date:
        upload_date = str(date.today() - timedelta(1))
    elif "ago" in upload_date:
        upload_date = f"{upload_date[0]}{upload_date[1]}"
    else:
        month, day = upload_date[0].split("-")
        upload_date = "{0}-{1}-{2}".format(upload_date[1], month, day)
    return upload_date


def _extract_author_name(soup) -> str:
    """Helper to extract and format the uploader's account name."""
    author_soup = soup.find("font", class_="detDesc")
    author_name = "[n/a]"
    # This fixes a bug caused by (currently) one known specific username with unescaped HTML
    if len(author_soup.get_text().split()[8:]) <= 1:
        author_name = author_soup.get_text().split()[-1:][0]
    if soup.find("img", alt="Trusted"):
        author_name = style(author_name, Color.TRUSTED)
    elif soup.find("img", alt="VIP"):
        author_name = style(author_name, Color.VIP)
    return author_name
