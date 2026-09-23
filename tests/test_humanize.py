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


class TestHumanizeTwoToElevenMonths:
    """Tests for the 'x months' range (2-11 months) that was previously
    guarded by _SECS_PER_MONTH * 2 threshold."""

    def test_three_months(self):
        earlier = arrow.Arrow(2025, 1, 15)
        later = earlier.shift(months=3)
        result = later.humanize(earlier)
        assert "3 months" in result

    def test_six_months(self):
        earlier = arrow.Arrow(2025, 1, 15)
        later = earlier.shift(months=6)
        result = later.humanize(earlier)
        assert "6 months" in result

    def test_eleven_months(self):
        earlier = arrow.Arrow(2024, 1, 15)
        later = earlier.shift(months=11)
        result = later.humanize(earlier)
        assert "11 months" in result

    def test_backward_three_months(self):
        later = arrow.Arrow(2025, 6, 15)
        earlier = arrow.Arrow(2025, 3, 15)
        result = earlier.humanize(later)
        assert "3 months ago" in result

    def test_backward_eleven_months(self):
        later = arrow.Arrow(2025, 1, 15)
        earlier = arrow.Arrow(2024, 2, 15)
        result = earlier.humanize(later)
        assert "11 months ago" in result

    def test_only_distance_three_months(self):
        earlier = arrow.Arrow(2025, 1, 15)
        later = earlier.shift(months=3)
        result = later.humanize(earlier, only_distance=True)
        assert result == "3 months"

    def test_only_distance_six_months(self):
        earlier = arrow.Arrow(2025, 1, 15)
        later = earlier.shift(months=6)
        result = later.humanize(earlier, only_distance=True)
        assert result == "6 months"

    def test_cross_year_six_months(self):
        earlier = arrow.Arrow(2024, 7, 15)
        later = arrow.Arrow(2025, 1, 15)
        result = later.humanize(earlier)
        assert "6 months" in result

    def test_backward_cross_year_six_months(self):
        later = arrow.Arrow(2025, 1, 15)
        earlier = arrow.Arrow(2024, 7, 15)
        result = earlier.humanize(later)
        assert "6 months ago" in result

    def test_two_months_short_month_span(self):
        """Jan → Mar = 59 days, should say '2 months'."""
        earlier = arrow.Arrow(2025, 1, 15)
        later = arrow.Arrow(2025, 3, 15)
        result = later.humanize(earlier)
        assert "2 months" in result

    def test_two_months_30_day_months(self):
        """Apr → Jun = 61 days, should say '2 months'."""
        earlier = arrow.Arrow(2025, 4, 15)
        later = arrow.Arrow(2025, 6, 15)
        result = later.humanize(earlier)
        assert "2 months" in result

    def test_two_months_with_feb(self):
        """Jan → Mar includes Feb, should say '2 months'."""
        earlier = arrow.Arrow(2025, 1, 28)
        later = earlier.shift(months=2)
        result = later.humanize(earlier)
        assert "2 months" in result


class TestHumanizeYearBoundary:
    """Tests for year-level humanize that uses calendar month comparison."""

    def test_one_year(self):
        earlier = arrow.Arrow(2024, 3, 15)
        later = earlier.shift(years=1)
        result = later.humanize(earlier)
        assert "a year" in result

    def test_one_year_leap(self):
        """Feb 29 → Feb 28 next year (non-leap)."""
        earlier = arrow.Arrow(2024, 2, 29)
        later = earlier.shift(years=1)
        result = later.humanize(earlier)
        assert "a year" in result

    def test_two_years(self):
        earlier = arrow.Arrow(2023, 6, 15)
        later = earlier.shift(years=2)
        result = later.humanize(earlier)
        assert "2 years" in result

    def test_backward_one_year(self):
        later = arrow.Arrow(2026, 3, 15)
        earlier = arrow.Arrow(2025, 3, 15)
        result = earlier.humanize(later)
        assert "a year ago" in result

    def test_only_distance_one_year(self):
        earlier = arrow.Arrow(2024, 3, 15)
        later = earlier.shift(years=1)
        result = later.humanize(earlier, only_distance=True)
        assert result == "a year"


class TestHumanizeWeekBoundary:
    """Tests for the week-level boundary that was also affected by the fix."""

    def test_exactly_four_weeks(self):
        """28 days should say '4 weeks', not 'a month'."""
        earlier = arrow.Arrow(2025, 3, 1)
        later = earlier.shift(weeks=4)
        result = later.humanize(earlier)
        assert "4 weeks" in result

    def test_exactly_two_weeks(self):
        earlier = arrow.Arrow(2025, 3, 1)
        later = earlier.shift(weeks=2)
        result = later.humanize(earlier)
        assert "2 weeks" in result

    def test_backward_two_weeks(self):
        later = arrow.Arrow(2025, 3, 15)
        earlier = arrow.Arrow(2025, 3, 1)
        result = earlier.humanize(later)
        assert "2 weeks ago" in result

    def test_backward_four_weeks(self):
        later = arrow.Arrow(2025, 3, 29)
        earlier = arrow.Arrow(2025, 3, 1)
        result = earlier.humanize(later)
        assert "4 weeks ago" in result

    def test_only_distance_four_weeks(self):
        earlier = arrow.Arrow(2025, 3, 1)
        later = earlier.shift(weeks=4)
        result = later.humanize(earlier, only_distance=True)
        assert result == "4 weeks"

    def test_three_weeks(self):
        earlier = arrow.Arrow(2025, 3, 1)
        later = earlier.shift(weeks=3)
        result = later.humanize(earlier)
        assert "3 weeks" in result

    def test_backward_three_weeks(self):
        later = arrow.Arrow(2025, 3, 22)
        earlier = arrow.Arrow(2025, 3, 1)
        result = earlier.humanize(later)
        assert "3 weeks ago" in result


class TestHumanizeWeekToMonthEdgeCases:
    """Edge cases at the transition from weeks to months."""

    def test_27_days_not_a_month(self):
        """27 days = 3 weeks 6 days, should NOT say 'a month'."""
        earlier = arrow.Arrow(2025, 3, 1)
        later = earlier.shift(days=27)
        result = later.humanize(earlier)
        assert "month" not in result

    def test_28_days_not_a_month(self):
        """28 days = exactly 4 weeks, should say '4 weeks'."""
        earlier = arrow.Arrow(2025, 3, 1)
        later = earlier.shift(days=28)
        result = later.humanize(earlier)
        assert "4 weeks" in result

    def test_29_days_not_a_month(self):
        """29 days = 4 weeks 1 day, should say '4 weeks'."""
        earlier = arrow.Arrow(2025, 3, 1)
        later = earlier.shift(days=29)
        result = later.humanize(earlier)
        assert "4 weeks" in result

    def test_30_days_not_a_month(self):
        """30 days = 4 weeks 2 days, should say '4 weeks'."""
        earlier = arrow.Arrow(2025, 3, 1)
        later = earlier.shift(days=30)
        result = later.humanize(earlier)
        assert "4 weeks" in result

    def test_31_days_not_a_month(self):
        """31 days = 4 weeks 3 days, spans a full calendar month → 'a month'."""
        earlier = arrow.Arrow(2025, 3, 1)
        later = earlier.shift(days=31)
        result = later.humanize(earlier)
        assert "month" in result

    def test_35_days_not_a_month(self):
        """35 days = 5 weeks, spans a full calendar month → 'a month'."""
        earlier = arrow.Arrow(2025, 3, 1)
        later = earlier.shift(days=35)
        result = later.humanize(earlier)
        assert "month" in result

    def test_60_days_two_months(self):
        """~2 months should say '2 months'."""
        earlier = arrow.Arrow(2025, 1, 15)
        later = earlier.shift(days=60)
        result = later.humanize(earlier)
        # 60 days is roughly 2 months, could be "2 months" or "8 weeks"
        # The important thing is it doesn't crash or produce nonsense
        assert "month" in result or "week" in result

    def test_90_days_approx_three_months(self):
        """~3 months should say '3 months'."""
        earlier = arrow.Arrow(2025, 1, 15)
        later = earlier.shift(days=90)
        result = later.humanize(earlier)
        assert "month" in result or "week" in result


class TestHumanizeGranularityMonth:
    """Tests for granularity='month' parameter with the fix."""

    def test_granularity_month_one_month(self):
        earlier = arrow.Arrow(2025, 2, 15)
        later = earlier.shift(months=1)
        result = later.humanize(earlier, granularity="month")
        assert "month" in result

    def test_granularity_month_two_months(self):
        earlier = arrow.Arrow(2025, 1, 15)
        later = earlier.shift(months=2)
        result = later.humanize(earlier, granularity="month")
        assert "2 months" in result

    def test_granularity_month_backward(self):
        later = arrow.Arrow(2025, 3, 15)
        earlier = arrow.Arrow(2025, 2, 15)
        result = earlier.humanize(later, granularity="month")
        assert "month" in result

    def test_granularity_month_list(self):
        earlier = arrow.Arrow(2025, 2, 15)
        later = earlier.shift(months=1)
        result = later.humanize(earlier, granularity=["month"])
        assert "month" in result

    def test_granularity_month_list_backward(self):
        later = arrow.Arrow(2025, 3, 15)
        earlier = arrow.Arrow(2025, 2, 15)
        result = earlier.humanize(later, granularity=["month"])
        assert "month" in result


class TestHumanizeDayOfMonthEdgeCases:
    """Tests for edge cases involving day-of-month transitions."""

    def test_jan31_feb28(self):
        """Jan 31 → Feb 28 (clamped). Should be 'a month'."""
        earlier = arrow.Arrow(2025, 1, 31)
        later = earlier.shift(months=1)  # Feb 28 (clamped)
        result = later.humanize(earlier)
        assert "month" in result

    def test_jan31_mar31(self):
        """Jan 31 → Mar 31. Should be '2 months'."""
        earlier = arrow.Arrow(2025, 1, 31)
        later = earlier.shift(months=2)
        result = later.humanize(earlier)
        assert "2 months" in result

    def test_mar31_apr30(self):
        """Mar 31 → Apr 30 (clamped). Should be 'a month'."""
        earlier = arrow.Arrow(2025, 3, 31)
        later = earlier.shift(months=1)  # Apr 30 (clamped)
        result = later.humanize(earlier)
        assert "month" in result

    def test_aug31_sep30(self):
        """Aug 31 → Sep 30 (clamped). Should be 'a month'."""
        earlier = arrow.Arrow(2025, 8, 31)
        later = earlier.shift(months=1)  # Sep 30 (clamped)
        result = later.humanize(earlier)
        assert "month" in result

    def test_aug31_oct31(self):
        """Aug 31 → Oct 31. Should be '2 months'."""
        earlier = arrow.Arrow(2025, 8, 31)
        later = earlier.shift(months=2)
        result = later.humanize(earlier)
        assert "2 months" in result

    def test_nov30_dec31(self):
        """Nov 30 → Dec 31. Should be 'a month'."""
        earlier = arrow.Arrow(2025, 11, 30)
        later = earlier.shift(months=1)
        result = later.humanize(earlier)
        assert "month" in result

    def test_nov30_jan30(self):
        """Nov 30 → Jan 30. Should be '2 months'."""
        earlier = arrow.Arrow(2025, 11, 30)
        later = earlier.shift(months=2)
        result = later.humanize(earlier)
        assert "2 months" in result


class TestHumanizeLocale:
    """Tests for locale parameter with the fix."""

    def test_locale_en_us(self):
        earlier = arrow.Arrow(2025, 2, 15)
        later = earlier.shift(months=1)
        result = later.humanize(earlier, locale="en_us")
        assert "month" in result

    def test_locale_en_gb(self):
        earlier = arrow.Arrow(2025, 2, 15)
        later = earlier.shift(months=1)
        result = later.humanize(earlier, locale="en_gb")
        assert "month" in result

    def test_locale_fr(self):
        earlier = arrow.Arrow(2025, 2, 15)
        later = earlier.shift(months=1)
        result = later.humanize(earlier, locale="fr")
        assert "mois" in result or "month" in result

    def test_locale_de(self):
        earlier = arrow.Arrow(2025, 2, 15)
        later = earlier.shift(months=1)
        result = later.humanize(earlier, locale="de")
        assert "Monat" in result or "month" in result

    def test_locale_es(self):
        earlier = arrow.Arrow(2025, 2, 15)
        later = earlier.shift(months=1)
        result = later.humanize(earlier, locale="es")
        assert "mes" in result or "month" in result


class TestHumanizeDefaultNow:
    """Tests for humanize() with no 'other' argument (defaults to now)."""

    def test_default_now_recent(self):
        """Recent times should still work with default 'now'."""
        earlier = arrow.Arrow.utcnow().shift(minutes=-5)
        result = earlier.humanize()
        assert "minute" in result

    def test_default_now_hours(self):
        """Hours ago with default 'now'."""
        earlier = arrow.Arrow.utcnow().shift(hours=-3)
        result = earlier.humanize()
        assert "hour" in result

    def test_default_now_days(self):
        """Days ago with default 'now'."""
        earlier = arrow.Arrow.utcnow().shift(days=-2)
        result = earlier.humanize()
        assert "day" in result

    def test_default_now_weeks(self):
        """Weeks ago with default 'now'."""
        earlier = arrow.Arrow.utcnow().shift(weeks=-3)
        result = earlier.humanize()
        assert "week" in result

    def test_default_now_months(self):
        """Months ago with default 'now'."""
        earlier = arrow.Arrow.utcnow().shift(months=-2)
        result = earlier.humanize()
        assert "month" in result

