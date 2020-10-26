"""results.py."""
from beautifultable import BeautifulTable, enums

from bsutils import get_input, get_terminal_width, output
from color import Color, style
from details import Details
from proxies import get_proxies
from soup import process_results_soup

DEFAULT_PIRATEBAY_URL = "http://thepiratebay.org"
SEARCH_TAGS = ("-audio", "-video", "-apps", "-games")


class Results(object):
    """Encapsulate torrent result processes."""

    HEALTHY = 75
    MINIMUM_WIDTH = 80
    TORRENTS_PER_PAGE = 30
    UNHEALTHY = 25

    def __init__(self, search_term):
        self._current_page = 1
        self._search_term = search_term
        self.user_quits = False
        if search_term == "q":
            self.user_quits = True
            return
        self._results_list = _fetch_results(search_term)

    def __getitem__(self, index) -> int:
        """Return index of list otherwise zero."""
        if self._results_list:
            return self._results_list[index]
        return 0

    def _build_results_table(self) -> BeautifulTable:
        """Build table using extracted results."""
        max_term_width = get_terminal_width()
        results_table = BeautifulTable(maxwidth=max_term_width)
        results_table.columns.header = ["ID", "Name", "Author", "Size", "Date", "S/L", "Health"]
        results_table.columns.alignment = enums.ALIGN_RIGHT
        results_table.columns.alignment["Name"] = enums.ALIGN_LEFT
        results_table.columns.width_exceed_policy = enums.WEP_ELLIPSIS
        results_table.set_style(enums.STYLE_MARKDOWN)
        results_table.border.bottom = "="
        for index, torrent in enumerate(self._results_list):
            index = style(index + 1, Color.HIGHLIGHT)
            title = torrent["name"]
            author = torrent["author"]
            bandwidth = f"{torrent['ul']}/{torrent['dl']}"
            upload, download = torrent["ul"], torrent["dl"]
            health = max(0, round((upload - download) / (max(1, upload) / 100)))
            diagnosis = Color.HEALTHY
            if Results.HEALTHY > health >= Results.UNHEALTHY:
                diagnosis = Color.UNHEALTHY
            elif health < Results.UNHEALTHY:
                diagnosis = Color.SICK
            health = f"{style(health, diagnosis)}%"
            results_table.rows.append([
                index,
                title,
                author,
                torrent["size"],
                torrent["date"],
                bandwidth,
                health,
            ])
        # Remove `Health` column if terminal size is narrow
        if max_term_width < Results.MINIMUM_WIDTH:
            results_table.columns.pop("Health")
        return results_table

    def is_empty(self) -> bool:
        """."""
        return not self._results_list

    def open_interface(self) -> None:
        """Print results and get user input."""
        if self.is_empty():
            return
        output(f":- Showing page {self._current_page} for '{self._search_term}'")
        table = self._build_results_table()
        while True:
            _display_table(table)
            user_input = get_input()
            if not len(user_input):
                continue
            if user_input.isnumeric():
                selection = int(user_input)
                if 0 < selection <= Results.TORRENTS_PER_PAGE:
                    details = Details(self._results_list[selection - 1]["url"])
                    details.open_interface()
            elif user_input == "n":
                self._results_list = self.next_page()
                self.open_interface()
                return
            elif user_input == "p":
                self._results_list = self.prev_page()
                self.open_interface()
                return
            else:
                return

    def next_page(self) -> list:
        """Returns next page or current list if at the end."""
        if len(self._results_list) < Results.TORRENTS_PER_PAGE:
            return self._results_list
        next_page_results = _fetch_results(self._search_term, self._current_page + 1)
        if not next_page_results:
            return self._results_list
        self._current_page += 1
        return next_page_results

    def prev_page(self) -> list:
        """Returns the previous page or current list if at the beginning."""
        if self._current_page <= 1:
            return self._results_list
        self._current_page -= 1
        return _fetch_results(self._search_term, self._current_page)


def _display_table(table) -> None:
    output(table)
    output(
        f"| Enter {style('ID#', Color.NOTICE)} to view torrent information, "
        f"'{style('n', Color.NOTICE)}' for next page,"
        f"'{style('p', Color.NOTICE)}' for previous page,"
        f"'{style('q', Color.NOTICE)}' to go back.",
    )


def _fetch_results(search_term, page=1) -> list:
    full_url = _build_search_url(search_term, page)
    return process_results_soup(full_url)


def _build_search_url(search_term, page=1) -> str:
    """Build search URL by getting first available proxy."""
    proxies = get_proxies()
    domain = next(iter(proxies)) or DEFAULT_PIRATEBAY_URL
    tag_id = 0
    tag = next((tag for tag in SEARCH_TAGS if tag in search_term), "")  # Get first tag occurence if any
    if tag:
        tag_id = (SEARCH_TAGS.index(tag) + 1) * 100 or 0
        search_term = search_term.replace(tag, "")
    return "{0}/search/{1}/{2}/99/{3}".format(domain, search_term, page, tag_id)
