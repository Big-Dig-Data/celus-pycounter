"""Tests for COUNTER 5 SUSHI support."""

import os

import pytest
from httmock import HTTMock, all_requests

import celus_pycounter.exceptions
import celus_pycounter.sushi5


def test_report_type(sushi5_report_trj1):
    assert sushi5_report_trj1.report_type == "TR_J1"


def test_report_version(sushi5_report_trj1):
    assert sushi5_report_trj1.report_version == 5


def test_report_customer(sushi5_report_trj1):
    assert sushi5_report_trj1.institutional_identifier == "exampleLibrary"


def test_data(sushi5_report_trj1):
    publication = next(iter(sushi5_report_trj1))
    data = [month[2] for month in publication]
    assert data[0] == 14


def test_metric(sushi5_report_trj1):
    publication = next(iter(sushi5_report_trj1))
    metrics = [month[1] for month in publication]
    assert metrics[0] == "Total_Item_Requests"


def test_doi(sushi5_report_trj1):
    publication = next(iter(sushi5_report_trj1))
    assert publication.doi == "some.fake.doi"


@all_requests
def not_authorized(url_unused, request_unused):
    """Mocked SUSHI service."""
    path = os.path.join(os.path.dirname(__file__), "data", "not_authorized.json")
    with open(path, "r", encoding="utf-8") as datafile:
        return datafile.read()


def test_error_not_authorized():
    with pytest.raises(celus_pycounter.exceptions.Sushi5Error) as exception:
        with HTTMock(not_authorized):
            celus_pycounter.sushi5.get_sushi_stats_raw(url="https://example.com/sushi", release=5)
    exc = exception.value
    assert exc.message == "Requestor Not Authorized to Access Service"
    assert exc.severity == "Error"
    assert exc.code == 2000


def test_bk_data(sushi5_report_trb1):
    publication = next(iter(sushi5_report_trb1))
    data = [month[2] for month in publication]
    assert data[0] == 22
