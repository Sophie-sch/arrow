"""Tests for humanize() month/week boundary calibration.

The bug: _SECS_PER_MONTH = 2634000 (30.5 days fixed) causes short months
(28-30 days) to be misclassified as "weeks" instead of "months".
"""

import pytest
from datetime import timezone

import arrow


class TestHumanizeWeekVsMonth:
    """Tests covering the 'x weeks' vs 'x months' boundary issue."""

    def test_exactly_one_calendar_month_feb(self):
        """Feb 15 → Mar 15 = 28 days (non-leap). Should be 'a month', not '4 weeks'."""
        earlier = arrow.Arrow(2025, 2, 15)
        later = arrow.Arrow(2025, 3, 15)
        result = later.humanize(earlier)
        assert "month" in result

    def test_exactly_one_calendar_month_feb_leap(self):
        """Feb 15 → Mar 15 = 29 days (leap year). Should be 'a month'."""
        earlier = arrow.Arrow(2024, 2, 15)
        later = arrow.Arrow(2024, 3, 15)
        result = later.humanize(earlier)
        assert "month" in result

    def test_exactly_one_calendar_month_30day(self):
        """Apr 15 → May 15 = 30 days. Should be 'a month', not '4 weeks'."""
        earlier = arrow.Arrow(2025, 4, 15)
        later = arrow.Arrow(2025, 5, 15)
        result = later.humanize(earlier)
        assert "month" in result

    def test_exactly_one_calendar_month_31day(self):
        """Jan 15 → Feb 15 = 31 days. Should be 'a month'."""
        earlier = arrow.Arrow(2025, 1, 15)
        later = arrow.Arrow(2025, 2, 15)
        result = later.humanize(earlier)
        assert "month" in result

    def test_exactly_one_calendar_month_all_months(self):
        """Each month shift should produce 'a month' regardless of month length."""
        for month in range(1, 12):
            earlier = arrow.Arrow(2025, month, 28)
            later = earlier.shift(months=1)
            result = later.humanize(earlier)
            assert "month" in result, (
                f"Month {month}: expected 'month' in '{result}'"
            )

    def test_two_calendar_months(self):
        """Two month shift should say '2 months', not '8 weeks'."""
        earlier = arrow.Arrow(2025, 1, 15)
        later = earlier.shift(months=2)
        result = later.humanize(earlier)
        assert "2 months" in result

    def test_backward_one_calendar_month(self):
        """Going back one calendar month should say 'a month ago'."""
        later = arrow.Arrow(2025, 3, 15)
        earlier = arrow.Arrow(2025, 2, 15)
        result = earlier.humanize(later)
        assert "month" in result

    def test_boundary_below_month_threshold(self):
        """~2.5 weeks should still say 'weeks', not 'month'."""
        earlier = arrow.Arrow(2025, 3, 1)
        later = earlier.shift(weeks=2, days=3)  # 17 days
        result = later.humanize(earlier)
        assert "week" in result or "day" in result

    def test_boundary_near_month_threshold(self):
        """~4.5 weeks should still say 'weeks' if not a full calendar month."""
        earlier = arrow.Arrow(2025, 3, 1)
        later = earlier.shift(weeks=4, days=5)  # 33 days
        result = later.humanize(earlier)
        # 33 days is more than a month, so may say "month" — that's acceptable
        # The key is that 4 weeks exactly should say "weeks"
        earlier2 = arrow.Arrow(2025, 3, 1)
        later2 = earlier2.shift(weeks=4)  # 28 days
        result2 = later2.humanize(earlier2)
        assert "week" in result2

    def test_only_distance_one_month(self):
        """only_distance=True with one calendar month should return 'a month'."""
        earlier = arrow.Arrow(2025, 4, 15)
        later = earlier.shift(months=1)
        result = later.humanize(earlier, only_distance=True)
        assert result == "a month"

    def test_granularity_month_forces_month(self):
        """granularity='month' should always use months."""
        earlier = arrow.Arrow(2025, 2, 15)
        later = earlier.shift(months=1)
        result = later.humanize(earlier, granularity="month")
        assert "month" in result

    def test_granularity_week_forces_week(self):
        """granularity='week' should always use weeks, even for 1 month span."""
        earlier = arrow.Arrow(2025, 2, 15)
        later = earlier.shift(months=1)
        result = later.humanize(earlier, granularity="week")
        assert "week" in result

    def test_short_month_span_below_four_weeks(self):
        """A span shorter than 4 weeks should say 'weeks' or 'days'."""
        earlier = arrow.Arrow(2025, 3, 1)
        later = earlier.shift(days=20)
        result = later.humanize(earlier)
        assert "week" in result or "day" in result

    def test_cross_year_month_shift(self):
        """Dec → Jan cross-year should still say 'a month'."""
        earlier = arrow.Arrow(2024, 12, 15)
        later = arrow.Arrow(2025, 1, 15)
        result = later.humanize(earlier)
        assert "month" in result

    def test_all_month_lengths_covered(self):
        """
        Verify each calendar month's length:
        Jan=31, Feb=28/29, Mar=31, Apr=30, May=31, Jun=30,
        Jul=31, Aug=31, Sep=30, Oct=31, Nov=30, Dec=31
        All should produce 'a month' when shifted by 1 month.
        """
        month_lengths = {
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31,
        }
        for start_month, length in month_lengths.items():
            day = min(28, length)  # safe day for all months
            earlier = arrow.Arrow(2025, start_month, day)
            later = earlier.shift(months=1)
            result = later.humanize(earlier)
            assert "month" in result, (
                f"Month {start_month} ({length} days): "
                f"expected 'month' in '{result}'"
            )
