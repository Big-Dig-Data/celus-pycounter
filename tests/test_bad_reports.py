"""Test parsing of deliberately bad data."""

import pytest

import celus_pycounter.exceptions
from celus_pycounter import report


@pytest.mark.parametrize("report_type", ["Bogus Report 7 (R4)"])
def test_report_type(report_type):
    """Report type doesn't exist."""
    data = [[report_type]]
    with pytest.raises(celus_pycounter.exceptions.UnknownReportTypeError):
        report.parse_generic(iter(data))


def test_bogus_file_type():
    with pytest.raises(celus_pycounter.exceptions.PycounterException):
        report.parse("no_such_file", "qsx")
