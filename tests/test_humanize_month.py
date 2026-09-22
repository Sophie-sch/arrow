from arrow import arrow


class TestHumanizeMonthCalibration:
    def test_one_month_shift_in_short_month(self):
        arw = arrow.Arrow(2013, 1, 31)
        later = arw.shift(months=1)

        assert arw.humanize(later) == "a month ago"
        assert later.humanize(arw) == "in a month"

    def test_one_month_shift_in_long_month(self):
        arw = arrow.Arrow(2013, 3, 15)
        later = arw.shift(months=1)

        assert arw.humanize(later) == "a month ago"
        assert later.humanize(arw) == "in a month"

    def test_two_month_shift_within_61_days(self):
        arw = arrow.Arrow(2013, 2, 15)
        later = arw.shift(months=2)

        assert arw.humanize(later) == "2 months ago"
        assert later.humanize(arw) == "in 2 months"

    def test_two_month_shift_across_year_boundary(self):
        arw = arrow.Arrow(2013, 11, 30)
        later = arw.shift(months=2)

        assert arw.humanize(later) == "2 months ago"
        assert later.humanize(arw) == "in 2 months"

    def test_one_month_plus_four_days(self):
        arw = arrow.Arrow(2013, 1, 15)
        later = arw.shift(months=1, days=4)

        assert arw.humanize(later) == "a month ago"
        assert later.humanize(arw) == "in a month"

    def test_sub_month_span_remains_weeks(self):
        arw = arrow.Arrow(2013, 3, 1)
        later = arrow.Arrow(2013, 3, 30)

        assert arw.humanize(later) == "4 weeks ago"
        assert later.humanize(arw) == "in 4 weeks"

    def test_partial_months_are_not_over_counted(self):
        arw = arrow.Arrow(2020, 12, 31)
        later = arrow.Arrow(2021, 3, 15)

        assert arw.humanize(later) == "2 months ago"
        assert later.humanize(arw) == "in 2 months"

    def test_month_only_distance(self):
        arw = arrow.Arrow(2013, 1, 15)
        later = arw.shift(months=1)

        assert arw.humanize(later, only_distance=True) == "a month"
        assert later.humanize(arw, only_distance=True) == "a month"

        arw = arrow.Arrow(2013, 2, 15)
        later = arw.shift(months=2)

        assert arw.humanize(later, only_distance=True) == "2 months"
        assert later.humanize(arw, only_distance=True) == "2 months"
