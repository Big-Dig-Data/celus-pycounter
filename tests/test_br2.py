"""Test parsing of COUNTER BR2 book report."""


def test_reportname(br2_report_tsv):
    assert br2_report_tsv.report_type == "BR2"


def test_report_version(br2_report_tsv):
    assert br2_report_tsv.report_version == 4


def test_metric(br2_report_tsv):
    assert br2_report_tsv.metric == "Book Section Requests"
