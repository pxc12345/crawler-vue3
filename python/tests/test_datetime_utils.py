import unittest
from datetime import datetime, timezone, timedelta

from src.datetime_utils import (
    API_DATETIME_FORMAT,
    assume_utc,
    format_api_datetime,
    format_config_for_api,
    get_local_day_bounds_utc,
    get_mysql_tz_offset,
    local_datetime_str_to_utc_naive,
    now_utc,
    parse_to_utc_naive,
    resolve_timezone,
    to_local_hour,
    get_effective_timezone,
    bucket_datetimes_by_local_hour,
)


class TestDatetimeUtils(unittest.TestCase):
    def test_now_utc_is_naive(self):
        dt = now_utc()
        self.assertIsNone(dt.tzinfo)

    def test_assume_utc_on_naive(self):
        naive = datetime(2026, 5, 29, 8, 0, 0)
        aware = assume_utc(naive)
        self.assertEqual(aware.tzinfo, timezone.utc)
        self.assertEqual(aware.hour, 8)

    def test_format_api_datetime_utc_to_shanghai(self):
        utc_naive = datetime(2026, 5, 29, 0, 0, 0)
        result = format_api_datetime(utc_naive, "Asia/Shanghai")
        self.assertEqual(result, "2026-05-29 08:00:00")

    def test_format_api_datetime_utc_to_new_york(self):
        utc_naive = datetime(2026, 5, 29, 12, 0, 0)
        result = format_api_datetime(utc_naive, "America/New_York")
        self.assertEqual(result, "2026-05-29 08:00:00")

    def test_format_api_datetime_from_string(self):
        result = format_api_datetime("2026-05-29 00:00:00", "Asia/Shanghai")
        self.assertEqual(result, "2026-05-29 08:00:00")

    def test_format_api_datetime_none(self):
        self.assertIsNone(format_api_datetime(None))

    def test_parse_to_utc_naive(self):
        parsed = parse_to_utc_naive("2026-05-29 08:00:00")
        self.assertEqual(parsed, datetime(2026, 5, 29, 8, 0, 0))

    def test_format_config_for_api(self):
        config = {"last_run_started_at": "2026-05-29 00:00:00", "target_url": "http://x"}
        result = format_config_for_api(config, "Asia/Shanghai")
        self.assertEqual(result["last_run_started_at"], "2026-05-29 08:00:00")
        self.assertEqual(result["target_url"], "http://x")

    def test_local_datetime_str_to_utc_naive(self):
        utc_naive = local_datetime_str_to_utc_naive("2026-05-29 16:00:00", "Asia/Shanghai")
        self.assertEqual(utc_naive, datetime(2026, 5, 29, 8, 0, 0))

    def test_to_local_hour_utc_to_shanghai(self):
        self.assertEqual(to_local_hour(datetime(2026, 5, 29, 1, 0, 0), "Asia/Shanghai"), 9)
        self.assertEqual(to_local_hour(datetime(2026, 5, 29, 2, 0, 0), "Asia/Shanghai"), 10)

    def test_get_effective_timezone_maps_utc_to_shanghai(self):
        self.assertEqual(get_effective_timezone("UTC"), "Asia/Shanghai")
        self.assertEqual(get_effective_timezone("Asia/Shanghai"), "Asia/Shanghai")

    def test_bucket_datetimes_by_local_hour(self):
        import os
        old = os.environ.get("DB_TIME_STORAGE")
        os.environ["DB_TIME_STORAGE"] = "utc"
        try:
            rows = [
                {"collected_at": datetime(2026, 5, 29, 1, 0, 0)},
                {"collected_at": datetime(2026, 5, 29, 1, 30, 0)},
                {"collected_at": datetime(2026, 5, 29, 2, 0, 0)},
            ]
            hourly = bucket_datetimes_by_local_hour(rows, "Asia/Shanghai")
            self.assertEqual(hourly[1], 0)
            self.assertEqual(hourly[2], 0)
            self.assertEqual(hourly[9], 2)
            self.assertEqual(hourly[10], 1)
            self.assertEqual(sum(hourly), 3)
        finally:
            if old is None:
                os.environ.pop("DB_TIME_STORAGE", None)
            else:
                os.environ["DB_TIME_STORAGE"] = old

    def test_get_mysql_tz_offset(self):
        self.assertEqual(get_mysql_tz_offset("Asia/Shanghai"), "+08:00")

    def test_get_local_day_bounds_utc(self):
        start, end = get_local_day_bounds_utc("Asia/Shanghai")
        self.assertIsNone(start.tzinfo)
        self.assertLess(start, end)
        self.assertEqual((end - start).total_seconds(), 86400)

    def test_format_task_for_api_single_pass(self):
        task = {
            "id": 60002,
            "created_at": datetime(2026, 5, 29, 3, 23, 28),
            "updated_at": datetime(2026, 5, 29, 3, 23, 57),
            "config": {"last_run_started_at": "2026-05-29 03:20:00", "target_url": "http://x"},
        }
        from src.datetime_utils import format_task_for_api

        format_task_for_api(task, "Asia/Shanghai")
        self.assertEqual(task["created_at"], "2026-05-29 11:23:28")
        self.assertEqual(task["updated_at"], "2026-05-29 11:23:57")
        self.assertEqual(task["config"]["last_run_started_at"], "2026-05-29 11:20:00")

    def test_output_format(self):
        result = format_api_datetime(datetime(2026, 1, 5, 3, 4, 0), "UTC")
        self.assertRegex(result, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
        self.assertEqual(result, datetime(2026, 1, 5, 3, 4, 0).strftime(API_DATETIME_FORMAT))


if __name__ == "__main__":
    unittest.main()
