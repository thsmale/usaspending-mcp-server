from unittest.mock import patch

from fiscalyear import FiscalQuarter
from freezegun import freeze_time

from utils.dates import (
    is_outdated_fy_fq,
    latest_fy_fq_with_data,
    period_to_quarter,
)


class TestLatestFyFqWithData:
    @freeze_time("2026-01-30")
    @patch("utils.dates.FiscalQuarter.current")
    def test_no_reported_data_yet(self, mock_fq):
        mock_fq.return_value = FiscalQuarter(2026, 2)
        fy, fq = latest_fy_fq_with_data(lag=45)
        assert fy == 2025
        assert fq == 4
        mock_fq.assert_called_once()

    @freeze_time("2026-02-20")
    @patch("utils.dates.FiscalQuarter.current")
    def test_has_reported_data(self, mock):
        mock.return_value = FiscalQuarter(2026, 2)
        fy, fq = latest_fy_fq_with_data(lag=45)
        assert fy == 2026
        assert fq == 2
        mock.assert_called_once()


class TestOutDatedFyFq:
    def test_fy_fq_is_less(self):
        outdated = is_outdated_fy_fq(lower_fy=2025, lower_fq=4, upper_fy=2026, upper_fq=1)
        assert outdated is True

        outdated = is_outdated_fy_fq(2026, 1, 2026, 2)
        assert outdated is True

        outdated = is_outdated_fy_fq(2026, 3, 2027, 1)
        assert outdated is True

    def test_fy_fq_is_greater(self):
        outdated = is_outdated_fy_fq(lower_fy=2026, lower_fq=1, upper_fy=2025, upper_fq=4)
        assert outdated is False

        outdated = is_outdated_fy_fq(2027, 2, 2026, 2)
        assert outdated is False

    def test_fy_fq_is_equal(self):
        outdated = is_outdated_fy_fq(2026, 1, 2026, 1)
        assert outdated is False

    def test_accepts_strings(self):
        outdated = is_outdated_fy_fq(lower_fy="2025", lower_fq="4", upper_fy="2026", upper_fq="1")
        assert outdated is True

        outdated = is_outdated_fy_fq(lower_fy="2026", lower_fq="1", upper_fy=2025, upper_fq=4)
        assert outdated is False


class TestPeriodToQuarter:
    def test_q1(self):
        for i in [1, 2, 3]:
            quarter = period_to_quarter(i)
            assert quarter == 1

    def test_q2(self):
        for i in [4, 5, 6]:
            quarter = period_to_quarter(i)
            assert quarter == 2

    def test_q3(self):
        for i in [7, 8, 9]:
            quarter = period_to_quarter(i)
            assert quarter == 3

    def test_q4(self):
        for i in [10, 11, 12]:
            quarter = period_to_quarter(i)
            assert quarter == 4

    def test_invalid_periods(self):
        for i in [0, 13, -100, 100]:
            quarter = period_to_quarter(i)
            assert quarter is None
