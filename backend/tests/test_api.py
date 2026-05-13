import tempfile
import unittest
from pathlib import Path

import db
import main


def _setup_test_db() -> tempfile.TemporaryDirectory:
    temp_dir = tempfile.TemporaryDirectory()
    db.DB_PATH = Path(temp_dir.name) / "watchlist-test.db"
    db.init_db()
    return temp_dir


class ApiBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temp_dir = _setup_test_db()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temp_dir.cleanup()

    def test_get_watchlist_page_one_starts_at_zero_offset(self) -> None:
        page_one = main.get_watchlist(page=1, size=2)
        page_two = main.get_watchlist(page=2, size=2)

        self.assertEqual(page_one["items"][0]["watchlist_id"], 1)
        self.assertNotEqual(
            page_one["items"][0]["watchlist_id"],
            page_two["items"][0]["watchlist_id"],
        )

    def test_get_catalog_uses_release_year_camel_case(self) -> None:
        catalog = main.get_catalog()
        first_item = catalog[0]

        self.assertIn("releaseYear", first_item)
        self.assertNotIn("release_year", first_item)

    def test_get_watchlist_uses_release_year_camel_case(self) -> None:
        watchlist = main.get_watchlist(page=1, size=5)
        first_item = watchlist["items"][0]

        self.assertIn("releaseYear", first_item)
        self.assertNotIn("release_year", first_item)

    def test_mark_watched_raises_not_found_for_missing_row(self) -> None:
        with self.assertRaises(main.HTTPException) as exc:
            main.mark_watched(999999, main.WatchUpdate(is_watched=True))

        self.assertEqual(exc.exception.status_code, 404)

    def test_get_watchlist_validates_page_and_size_bounds(self) -> None:
        with self.assertRaises(main.HTTPException) as invalid_page:
            main.get_watchlist(page=0, size=5)
        with self.assertRaises(main.HTTPException) as invalid_size_low:
            main.get_watchlist(page=1, size=0)
        with self.assertRaises(main.HTTPException) as invalid_size_high:
            main.get_watchlist(page=1, size=101)

        self.assertEqual(invalid_page.exception.status_code, 422)
        self.assertEqual(invalid_size_low.exception.status_code, 422)
        self.assertEqual(invalid_size_high.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
