"""Pytest fixtures for main test suite."""

import os

import pytest

import celus_pycounter.sushi
from celus_pycounter import csvhelper, report


def parsedata(filename):
    """Helper function returns a report from a filename relative to data directory."""
    return report.parse(os.path.join(os.path.dirname(__file__), "data", filename))


@pytest.fixture(params=["csvC4JR1", "C4JR1.csv", "C4JR1_bad.csv", "C4JR1GOA.csv"])
def csv_jr1_report(request):
    """Various CSV format JR1 reports."""
    return parsedata(request.param)


@pytest.fixture(params=["simpleJR1.tsv", "tsvC4JR1", "issue_14.tsv"])
def tsv_jr1(request):
    """TSV file"""
    return parsedata(request.param)


@pytest.fixture(params=["csvC4JR1", "C4JR1.csv", "C4JR1_bad.csv"])
def csv_jr1_report_std(request):
    """Standard (non-GOA) JR1 reports."""
    return parsedata(request.param)


@pytest.fixture(params=["csvC4JR1", "C4JR1.csv"])
def csv_jr1_report_common_data(request):
    """JR1 reports with shared common data we can make assertions about."""
    return parsedata(request.param)


@pytest.fixture(params=["csvC4JR1", "C4JR1.csv", "C4JR1_bad.csv"])
def csv_jr1_r4_report(request):
    """Revision 4 JR1 reports."""
    return parsedata(request.param)


@pytest.fixture(params=["JR1.xlsx", "JR1_bad.xlsx", "xlsxJR1"])
def jr1_report_xlsx(request):
    """Excel formatted JR1 reports."""
    return parsedata(request.param)


def parse_sushi_file(filename):
    """Turn SUSHI data file into a report."""
    with open(os.path.join(os.path.dirname(__file__), "data", filename)) as datafile:
        return celus_pycounter.sushi.raw_to_full(datafile.read())


@pytest.fixture(
    params=[
        "sushi_simple.xml",
        "sushi_simple_no_customer.xml",
        "sushi_simple_br1.xml",
        "sushi_simple_db1.xml",
        "sushi_db1_missing_record_view.xml",
        "sushi_br3.xml",
        "sushi_jr2.xml",
    ]
)
def sushi_report_all(request):
    """Report from SUSHI, shared common data."""
    return parse_sushi_file(request.param)


@pytest.fixture(
    params=[
        "sushi_simple.xml",
        "sushi_simple_br1.xml",
        "sushi_simple_db1.xml",
        "sushi_db1_missing_record_view.xml",
    ]
)
def sushi_report_with_customer(request):
    """Report from SUSHI, shared common data with customer set."""
    return parse_sushi_file(request.param)


@pytest.fixture(params=["sushi_simple_no_customer.xml"])
def sushi_report_no_customer(request):
    """Report from SUSHI, shared common data with customer not set."""
    return parse_sushi_file(request.param)


@pytest.fixture(params=["sushi_simple.xml", "sushi_simple_no_customer.xml"])
def sushi_report_jr1(request):
    """Report from SUSHI, shared common data, JR1 only."""
    return parse_sushi_file(request.param)


@pytest.fixture
def sushi_report_jr2():
    """Journal turnaways."""
    return parse_sushi_file("sushi_jr2.xml")


@pytest.fixture
def sushi_report_br3():
    """Book turnaways."""
    return parse_sushi_file("sushi_br3.xml")


@pytest.fixture
def sushi_simple_br1():
    """Book report."""
    return parse_sushi_file("sushi_simple_br1.xml")


@pytest.fixture
def sushi_simple_db1():
    """Database report."""
    return parse_sushi_file("sushi_simple_db1.xml")


@pytest.fixture
def sushi_missing_ii():
    """SUSHI response with missing ISSN."""
    return parse_sushi_file("sushi_missing_ii.xml")


@pytest.fixture
def sushi_missing_rec():
    """Database report with January missing, no record_view records."""
    rpt = parse_sushi_file("sushi_db1_missing_record_view.xml")
    # missing data added on export
    rpt.as_generic()
    return rpt


@pytest.fixture
def sushi_missing_jan():
    """SUSHI with months missing."""
    return parse_sushi_file("sushi_missing_jan.xml")


@pytest.fixture(
    params=[
        "C4BR1.tsv",
        "C4DB1.tsv",
        "C4JR1.csv",
        "C4JR1GOA.csv",
        "C4BR2.tsv",
        "C4DB2.tsv",
        "C4JR1mul.csv",
    ]
)
def common_output(request):
    """Common data for output."""
    delim = {"tsv": "\t", "csv": ","}[request.param.split(".")[1]]
    filename = os.path.join(os.path.dirname(__file__), "data", request.param)
    with csvhelper.UnicodeReader(filename, delimiter=delim) as report_reader:
        content = list(report_reader)
    return parsedata(request.param).as_generic(), content


@pytest.fixture(params=["C4BR2.tsv", "C4BR1.tsv"])
def all_book_reports(request):
    """All book reports."""
    return parsedata(request.param)


@pytest.fixture(params=["C4BR1.tsv", "simpleJR1.tsv"])
def report_file_output(request):
    """Reports with their expected output."""
    rpt = parsedata(request.param)
    with open(os.path.join(os.path.dirname(__file__), "data", request.param), "rb") as f:
        expected_data = f.read()
    return rpt, expected_data


@pytest.fixture(params=["C4DB1.tsv", "C4DB2.tsv"])
def db_report(request):
    """All C4 database reports."""
    return parsedata(request.param)


@pytest.fixture
def c4db2():
    """DB2."""
    return parsedata("C4DB2.tsv")


@pytest.fixture
def c4db1():
    """DB1."""
    return parsedata("C4DB1.tsv")


@pytest.fixture
def c4db1_sy():
    """DB1 split year"""
    return parsedata("C4DB1_split_year.tsv")


@pytest.fixture
def br3_report_csv():
    """Book report 3 (turnaways)."""
    return parsedata("C4BR3.csv")


@pytest.fixture
def br1_report_tsv():
    """Book report 1."""
    return parsedata("C4BR1.tsv")


@pytest.fixture
def br2_report_tsv():
    """Book report 2."""
    return parsedata("C4BR2.tsv")


@pytest.fixture
def br3_report_tsv():
    """Book report 3 (turnaways)."""
    return parsedata("C4BR3.tsv")


@pytest.fixture
def jr2_report():
    """Journal report 2 (turnaways)."""
    return parsedata("C4JR2.csv")


@pytest.fixture
def pr1_report():
    """Platform report 1."""
    return parsedata("PR1.tsv")


@pytest.fixture
def jr1_bad():
    """C4 JR1 with questionable formatting..."""
    return parsedata("C4JR1_bad.csv")


@pytest.fixture
def goa():
    """Gold Open Access."""
    return parsedata("C4JR1GOA.csv")


@pytest.fixture
def big_multiyear():
    """Big report spanning multiple years."""
    return parsedata("C4JR1big.csv")


@pytest.fixture
def multiyear():
    """Multiyear report."""
    return parsedata("C4JR1my.csv")


@pytest.fixture
def mr1_report_tsv():
    """Multimedia report 1"""
    return parsedata("C4MR1.tsv")


@pytest.fixture(
    params="""C4BR1.tsv
C4BR2.tsv
C4BR3.csv
C4DB1.tsv
C4DB1_split_year.tsv
C4DB2.tsv
C4JR1.csv
C4JR1_bad.csv
C4JR1big.csv
C4JR1GOA.csv
C4JR1mul.csv
C4JR1my.csv
C4JR2.csv
C4JR2_single_month.csv
C4MR1.tsv
PR1.tsv
simpleJR1.tsv
""".split()
)
def all_reports(request):
    """All COUNTER 4 reports."""
    return parsedata(request.param)
