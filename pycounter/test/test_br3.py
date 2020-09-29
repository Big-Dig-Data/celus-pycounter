"""Test parsing of COUNTER 4 BR3 report (turnaways)"""

import datetime


def test_metric_csv(br3_report_csv):
    assert br3_report_csv.metric is None  # Multiple metrics per report


def test_type_csv(br3_report_csv):
    assert br3_report_csv.report_type == "BR3"


def test_data_csv(br3_report_csv):
    i = iter(br3_report_csv)
    row = next(i)
    item = next(iter(row))
    assert item == (
        datetime.date(2012, 1, 1),
        "Access denied: concurrent/simultaneous user license limit exceeded",
        4,
    )


def test_metric_csv(br3_report_tsv):
    assert br3_report_tsv.metric is None  # Multiple metrics per report


def test_type_csv(br3_report_tsv):
    assert br3_report_tsv.report_type == u"BR3"


def test_data_csv(br3_report_tsv):
    i = iter(br3_report_tsv)
    row = next(i)
    item = next(iter(row))
    assert item == (
        datetime.date(2019, 12, 1),
        u"Access denied: content item not licensed",
        1,
    )
