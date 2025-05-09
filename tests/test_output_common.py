"""Check data in common output formats."""

from datetime import date

from celus_pycounter.report import CounterBook, CounterReport


def _check_lines(a, b):
    # some report headers are missing ':' in the end
    # and some have trailing spaces
    # and are case insensitive
    # and some might be wrapped in
    assert a.lower().strip(' "').rstrip(": ") == b.lower().strip(' "').rstrip(": ")


def test_header_content(common_output):
    converted, raw = common_output
    for i in range(7):
        assert len(converted[i]) == len(raw[i])
        for j in range(len(converted[i])):
            _check_lines(converted[i][j], raw[i][j])


def test_table_header(common_output):
    converted, raw = common_output
    assert len(converted[7]) == len(raw[7])
    for i in range(len(converted[7])):
        _check_lines(converted[7][i], raw[7][i])


def test_totals(common_output):
    assert common_output[0][8:] == common_output[1][8:]


def test_data(common_output):
    for index, line in enumerate(common_output[1][9:], 9):
        assert line == common_output[0][index]


def test_writing_file(report_file_output, tmp_path):
    report, expected_data = report_file_output

    report.write_tsv(str(tmp_path / "outputfile.tsv"))
    with open(str(tmp_path / "outputfile.tsv"), "rb") as new_file:
        new_content = new_file.read()

    assert expected_data == new_content


def test_totals_sparse_data(tmp_path):
    """
    Check that when sparse data (data where some months are missing) are used, both
    the monthly totals and the monthly data are properly outputed into TSV
    """

    start = date(2019, 1, 1)
    end = date(2019, 3, 31)
    cb1 = CounterBook(
        period=(start, end),
        title="Book 1",
        month_data=[(date(2019, 2, 1), 3), (date(2019, 3, 1), 5)],
    )
    cb2 = CounterBook(
        period=(start, end),
        title="Book 2",
        month_data=[(date(2019, 1, 1), 1), (date(2019, 3, 1), 7)],
    )
    report = CounterReport(report_type="BR2", period=(start, end))
    report.pubs = [cb1, cb2]
    report.write_tsv(str(tmp_path / "outputfile.tsv"))
    with open(str(tmp_path / "outputfile.tsv"), "r") as new_file:
        output_lines = list(new_file.readlines())
    assert len(output_lines) == 11
    # check totals computation
    totals_line = output_lines[8]
    assert totals_line.startswith("Total for all titles")
    totals = totals_line.split("\t")
    assert [int(t) for t in totals[-3:]] == [0 + 1, 3 + 0, 5 + 7], "check totals match"
    # book 1 line
    book_line = output_lines[9]
    assert book_line.startswith("Book 1")
    numbers = [int(num) for num in book_line.split("\t")[-3:]]
    assert numbers == [0, 3, 5], "check counts for book 1"


def test_roundtrippable(all_reports, tmp_path):
    """Test that all of our parsable reports can also be output."""
    all_reports.write_tsv(str(tmp_path / "output.tsv"))
