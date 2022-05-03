"""Test COUNTER JR1 journal report (CSV)"""

import datetime
import os
import unittest

from pycounter import report

import pytest


@pytest.mark.parametrize(
    "pub_number,expected",
    [
        (0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        (1, [2, 1, 0, 0, 0, 5, 1, 1, 0, 5, 1, 0]),
    ],
)
def test_counter4_csv_data(csv_jr1_report_common_data, pub_number, expected):
    publication = csv_jr1_report_common_data.pubs[pub_number]
    assert [x[2] for x in publication] == expected


def test_metric(csv_jr1_report_std):
    assert csv_jr1_report_std.metric == "FT Article Requests"


def test_customer(csv_jr1_report):
    assert csv_jr1_report.customer == "University of Maximegalon"


def test_date_run(csv_jr1_report):
    assert csv_jr1_report.date_run == datetime.date(2012, 2, 21)


def test_period(csv_jr1_report):
    assert csv_jr1_report.period == (
        datetime.date(2011, 1, 1),
        datetime.date(2011, 12, 31),
    )


def test_report_type(csv_jr1_report_std):
    assert csv_jr1_report_std.report_type == "JR1"


def test_ibsn(csv_jr1_r4_report):
    assert csv_jr1_r4_report.pubs[1].isbn is None


def test_multiyear_period(multiyear):
    assert multiyear.period == (datetime.date(2011, 10, 1), datetime.date(2012, 2, 29))


def test_multiyear_monthdata_exception(multiyear):
    with pytest.raises(AttributeError):
        # pylint: disable=pointless-statement
        multiyear.pubs[0].monthdata


def test_multiyear_data(multiyear):
    assert len(list(multiyear.pubs[0])) == 5
    usage = [x[2] for x in multiyear.pubs[0]]
    assert usage == [0, 0, 0, 0, 0]


def test_multiyear_month_data(multiyear):
    expected = [
        datetime.date(2011, 10, 1),
        datetime.date(2011, 11, 1),
        datetime.date(2011, 12, 1),
        datetime.date(2012, 1, 1),
        datetime.date(2012, 2, 1),
    ]

    months = [x[0] for x in multiyear.pubs[0]]

    assert months == expected


# Multi-year report with more than 12 months of data


def test_big_period(big_multiyear):
    assert big_multiyear.period == (
        datetime.date(2012, 1, 1),
        datetime.date(2013, 12, 31),
    )


class ParseJR1(unittest.TestCase):
    """JR1a Archive Access Report
    """

    def setUp(self):
        self.report = report.parse(
            os.path.join(os.path.dirname(__file__), "data/C4JR1a.csv")
        )

    def test_metric(self):
        self.assertEqual(self.report.metric, u"Archive Article Requests")

def test_big_monthdata_exception(big_multiyear):
    with pytest.raises(AttributeError):
        # pylint: disable=pointless-statement
        big_multiyear.pubs[0].monthdata


def test_big_data(big_multiyear):
    usage = [x[2] for x in big_multiyear.pubs[0]]
    assert usage == [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ]


def test_goa_metric(goa):
    assert goa.metric == "Gold Open Access Article Requests"


def test_counter4_bad_csv_data(jr1_bad):

    publication = jr1_bad.pubs[0]
    assert [x[2] for x in publication] == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    publication = jr1_bad.pubs[1]
    assert [x[2] for x in publication] == [2, 1, 0, 0, 0, 5, 1, 1, 0, 5, 1, 1000]

class ParseMultiyear(unittest.TestCase):
    """Multi-year COUNTER report
    """

    def setUp(self):
        self.report = report.parse(
            os.path.join(os.path.dirname(__file__), "data/C4JR1my.csv")
        )

    def test_period(self):
        self.assertEqual(
            self.report.period, (datetime.date(2011, 10, 1), datetime.date(2012, 2, 29))
        )

    def test_monthdata_exception(self):
        self.assertRaises(AttributeError, getattr, self.report.pubs[0], "monthdata")

    def test_data(self):
        self.assertEqual(len(list(self.report.pubs[0])), 5)
        usage = [x[2] for x in self.report.pubs[0]]
        self.assertEqual(usage, [0, 0, 0, 0, 0])

    def test_month_data(self):
        expected = [
            datetime.date(2011, 10, 1),
            datetime.date(2011, 11, 1),
            datetime.date(2011, 12, 1),
            datetime.date(2012, 1, 1),
            datetime.date(2012, 2, 1),
        ]

        months = [x[0] for x in self.report.pubs[0]]

        self.assertEqual(months, expected)


class ParseBigMultiyear(unittest.TestCase):
    """Multi-year report with more than 12 months of data
    """

    def setUp(self):
        self.report = report.parse(
            os.path.join(os.path.dirname(__file__), "data/C4JR1big.csv")
        )

    def test_period(self):
        self.assertEqual(
            self.report.period, (datetime.date(2012, 1, 1), datetime.date(2013, 12, 31))
        )

    def test_monthdata_exception(self):
        self.assertRaises(AttributeError, getattr, self.report.pubs[0], "monthdata")

    def test_data(self):
        usage = [x[2] for x in self.report.pubs[0]]
        self.assertEqual(
            usage,
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        )


class ParseGOA(unittest.TestCase):
    """Gold Open Access Report
    """

    def setUp(self):
        self.report = report.parse(
            os.path.join(os.path.dirname(__file__), "data/C4JR1GOA.csv")
        )

    def test_metric(self):
        self.assertEqual(self.report.metric, u"Gold Open Access Article Requests")


class ParseCounter4Bad(unittest.TestCase):
    """Tests for parsing C4 JR1 with questionable formatting..."""

    def setUp(self):
        self.report = report.parse(
            os.path.join(os.path.dirname(__file__), "data/C4JR1_bad.csv")
        )

    def test_counter4_csv_data(self):

        publication = self.report.pubs[0]
        self.assertEqual(
            [x[2] for x in publication], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        )
        publication = self.report.pubs[1]
        self.assertEqual(
            [x[2] for x in publication], [2, 1, 0, 0, 0, 5, 1, 1, 0, 5, 1, 1000]
        )
