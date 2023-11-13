"""Test parsing of COUNTER BR1 book report."""


def test_reportname(br1_report_tsv):
    assert br1_report_tsv.report_type == "BR1"
    assert br1_report_tsv.report_version == 4


def test_metric(br1_report_tsv):
    assert br1_report_tsv.metric == "Book Title Requests"


def test_isbn(br1_report_tsv):
    publication = br1_report_tsv.pubs[0]
    assert publication.isbn == "9787490833809"


def test_proprietary_id(br1_report_tsv):
    publication = br1_report_tsv.pubs[0]
    assert publication.proprietary_id == "1111:5555"
