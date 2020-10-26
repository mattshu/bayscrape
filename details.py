"""Handle the display of torrent details and user comments."""
import webbrowser
from enum import Enum

from beautifultable import BeautifulTable, enums

from bsutils import get_input, get_terminal_width, output
from color import Color, style
from soup import process_details_soup


class View(Enum):
    """Determine which view the Details table is in."""

    INFO = "information"
    COMMENTS = "comments"


class Details(object):
    """Build the details table from the results list."""

    def __init__(self, torrent_url):
        self._url = torrent_url
        header, description, comments = process_details_soup(self._url)
        self._header = header
        self._description = description
        self._comments = comments

    def open_interface(self) -> None:
        """DOCSTRING."""
        user_input = "i"  # Show torrent description by default
        while True:
            if not len(user_input):
                continue
            if user_input == "i":
                details_table = self._build_details_table()
                _display_table(details_table, View.INFO)
            elif user_input == "c":
                comments_table = self._build_comments_table()
                _display_table(comments_table, View.COMMENTS)
            elif user_input == "d":
                magnet_url = self._header["magnet_url"]
                _open_magnet(magnet_url)
                output("")
                return
            elif user_input == "q":
                return
            else:
                continue
            user_input = get_input()

    def _build_comments_table(self):
        """DOCSTRING."""
        comments_table = BeautifulTable(maxwidth=get_terminal_width())
        comments_table.columns.header = ["Author", "Date", self._header["name"]]
        comments_table.columns.alignment = enums.ALIGN_LEFT
        comments_table.set_style(enums.STYLE_SEPARATED)
        if self._comments:
            for comment in self._comments:
                comments_table.rows.append([
                    comment.author,
                    comment.date,
                    comment.body,
                ])
        else:
            comments_table.rows.append(["", "", "No comments found."])
        return comments_table

    def _build_details_table(self) -> BeautifulTable:
        """DOCSTRING."""
        table = BeautifulTable(maxwidth=get_terminal_width())
        table.columns.header = [self._header["name"]]
        table.columns.alignment = enums.ALIGN_LEFT
        table.rows.append([self._get_formatted_header()])
        table.rows.append([self._description])
        return table

    def _get_formatted_header(self) -> str:
        """DOCSTRING."""
        return "\n".join((
            _align_detail_row("type", self._header["type"], "uploaded", self._header["uploaded"]),
            _align_detail_row("files", self._header["files"], "by", self._header["by"]),
            _align_detail_row("size", self._header["size"], "seeders", self._header["seeders"]),
            _align_detail_row("comments", self._header["comments"], "leechers", self._header["leechers"]),
            _align_detail_row("info hash", self._header["info hash"]),
        ))


def _display_table(table, view=View.INFO):
    """DOCSTRING."""
    info_view = view == View.INFO
    option = "comments" if info_view else "description"
    output(table)
    output(
        f"| Enter '{style('c' if info_view else 'i', Color.NOTICE)}' to view torrent {option},"
        f"'{style('d', Color.NOTICE)}' to download torrent, "
        f"'{style('q', Color.NOTICE)}' to go back.",
    )


def _open_magnet(magnet_url) -> None:
    """TODO: handle bad magnet."""
    if not webbrowser.open_new_tab(magnet_url):
        output("Error: Bad magnet URL")


def _align_detail_row(left_label, left_value, right_label=None, right_value=None) -> str:
    """DOCSTRING."""
    dot_width = 15
    mid_width = 25
    row = left_label + "." * (dot_width - len(left_label))
    row += left_value + " " * (mid_width - len(left_value))
    if right_label and right_value:
        row += right_label + "." * (dot_width - len(right_label))
        row += right_value
    return row
