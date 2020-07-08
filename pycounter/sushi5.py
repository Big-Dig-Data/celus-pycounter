"""COUNTER 5 SUSHI support."""

import collections
import datetime
import logging
import warnings

import pendulum
import requests

import pycounter.exceptions
from pycounter.helpers import convert_date_run
import pycounter.report

DEPRECATED_KEYS = {"requestor_email", "requestor_name", "customer_name"}

logger = logging.getLogger(__name__)


def _dates_from_filters(filters):
    """Convert report filters to start and end date

    Args:
        filters: a list of dicts containing SUSHI report filters

    Returns: tuple of start, end dates as datetime.date

    """

    converted_filters = {
        filter_["Name"]: datetime.datetime.strptime(filter_["Value"], "%Y-%m-%d").date()
        for filter_ in filters
        if filter_["Name"].lower() in ("begin_date", "end_date")
    }

    # Test whether both ranges are present
    if len({e.lower() for e in converted_filters}) != 2:
        raise ValueError("filters must include a Begin_Date and End_Date")

    def update_case_insensitive(name):
        if name not in converted_filters:
            # pick the first case insensitive choice
            key = [e for e in converted_filters if name.lower() == e.lower()][0]
            converted_filters[name] = converted_filters[key]

    # make sure that Begin_date and End_Date are set
    update_case_insensitive("Begin_Date")
    update_case_insensitive("End_Date")

    return converted_filters["Begin_Date"], converted_filters["End_Date"]


def _get_identifiers(item):
    """Pull identifiers from an item into a dict."""
    identifiers = {"eissn": "", "issn": "", "doi": "", "prop_id": "", "isbn": ""}
    for identifier in item["Item_ID"]:
        if identifier["Type"] == "Print_ISSN":
            identifiers["issn"] = identifier["Value"]
        elif identifier["Type"] == "Online_ISSN":
            identifiers["eissn"] = identifier["Value"]
        elif identifier["Type"] == "ISBN":
            identifiers["isbn"] = identifier["Value"]
        elif identifier["Type"] == "DOI":
            identifiers["doi"] = identifier["Value"]
        elif identifier["Type"] == "Proprietary_ID":
            identifiers["prop_id"] = identifier["Value"]

    return identifiers


def raw_to_full(raw_report):
    """Convert a raw report to CounterReport.

    :param raw_report: raw report as dict decoded from JSON
    :return: a :class:`pycounter.report.CounterReport`
    """
    # pylint: disable=too-many-locals
    header = raw_report["Report_Header"]
    period = _dates_from_filters(header["Report_Filters"])
    date_run = header.get("Created")
    report = pycounter.report.CounterReport(
        period=period,
        report_version=int(header.get("Release", raw_report.get("Release", 5))),
        report_type=header["Report_ID"],
        customer=header.get("Institution_Name", ""),
        institutional_identifier=header.get("Customer_ID", ""),
        metric=None,  # COUNTER 5 reports usually contain multiple metrics
        date_run=pendulum.parse(date_run) if date_run else datetime.datetime.now(),
    )

    for item in raw_report["Report_Items"]:
        publisher_name = item.get("Publisher", "")
        platform = item.get("Platform", "")
        title = item["Title"]

        identifiers = _get_identifiers(item)

        metrics_data = collections.OrderedDict()

        for perform_item in item["Performance"]:
            item_date = convert_date_run(perform_item["Period"]["Begin_Date"])
            for inst in perform_item["Instance"]:
                usage = inst["Count"]
                metrics_data.setdefault(inst["Metric_Type"], []).append(
                    (item_date, int(usage))
                )

        if report.report_type == "TR_J1":
            report.pubs.append(
                pycounter.report.CounterJournal(
                    title=title,
                    platform=platform,
                    publisher=publisher_name,
                    period=report.period,
                    metric="Total_Item_Requests",
                    issn=identifiers["issn"],
                    eissn=identifiers["eissn"],
                    doi=identifiers["doi"],
                    proprietary_id=identifiers["prop_id"],
                    month_data=metrics_data["Total_Item_Requests"],
                )
            )
        elif report.report_type == "TR_J2":
            for metric, data in metrics_data.items():
                report.pubs.append(
                    pycounter.report.CounterJournal(
                        title=title,
                        platform=platform,
                        publisher=publisher_name,
                        period=report.period,
                        metric=metric,
                        issn=identifiers["issn"],
                        eissn=identifiers["eissn"],
                        doi=identifiers["doi"],
                        proprietary_id=identifiers["prop_id"],
                        month_data=data,
                    )
                )
        elif report.report_type.startswith("TR_B"):
            report.pubs.append(
                pycounter.report.CounterBook(
                    title=title,
                    platform=platform,
                    publisher=publisher_name,
                    period=report.period,
                    metric="Total_Item_Requests",
                    issn=identifiers["issn"],
                    isbn=identifiers["isbn"],
                    doi=identifiers["doi"],
                    proprietary_id=identifiers["prop_id"],
                    month_data=metrics_data["Total_Item_Requests"],
                )
            )
        else:
            raise pycounter.exceptions.UnknownReportTypeError

    return report


def get_sushi_stats_raw(
    wsdl_url=None,
    start_date=None,
    end_date=None,
    requestor_id=None,
    customer_reference=None,
    report="TR_J1",
    release=5,
    sushi_dump=False,
    verify=True,
    url=None,
    api_key=None,
    **kwargs
):
    """Get SUSHI stats for a given site in dict (decoded from JSON) format.

    :param wsdl_url: (Deprecated; for backward compatibility with COUNTER 4 SUSHI
        code. Use `url` instead.) URL to API endpoint for this provider

    :param start_date: start date for report (must be first day of a month)

    :param end_date: end date for report (must be last day of a month)

    :param requestor_id: requestor ID as defined by SUSHI protocol

    :param customer_reference: customer reference number as defined by SUSHI
        protocol

    :param report: report type, values defined by SUSHI protocol

    :param release: COUNTER release (only 5 is supported in this module)

    :param sushi_dump: produces dump of JSON to DEBUG logger

    :param verify: bool: whether to verify SSL certificates

    :param url: str: URL to endpoint for this provider

    :param api_key: str: API key for SUSHI provider (not used by all vendors; see
        vendor instructions to determine if this is needed)

    """
    _check_params(kwargs, release)
    if url is None and wsdl_url:  # pragma: no cover
        warnings.warn(
            DeprecationWarning(
                "wsdl_url argument to get_sushi_stats"
                "_raw is deprecated; use url instead"
            )
        )
        url = wsdl_url
    url_params = {"url": url, "report": report}
    req_params = {
        "customer_id": customer_reference,
        "begin_date": start_date,
        "end_date": end_date,
        "requestor_id": requestor_id,
    }
    if api_key:
        req_params["api_key"] = api_key

    response = requests.get(
        "{url}/reports/{report}".format(**url_params),
        params=req_params,
        headers={"User-Agent": "pycounter/%s" % pycounter.__version__},
        verify=verify,
    )

    if sushi_dump:  # pragma: no cover
        logger.debug(
            "SUSHI DUMP: request: %s \n\n response: %s",
            vars(response.request),
            response.content,
        )

    response_data = response.json()

    if "Exceptions" in response_data["Report_Header"]:
        raise pycounter.exceptions.Sushi5Error(
            message=response_data["Report_Header"]["Exceptions"][0]["Message"],
            severity=response_data["Report_Header"]["Exceptions"][0]["Severity"],
            code=response_data["Report_Header"]["Exceptions"][0]["Code"],
        )

    return response_data


def _check_params(kwargs, release):
    """Warn about unnecessary/wrong params to get_sushi_stats_raw."""
    if release != 5:  # pragma: no cover
        raise pycounter.exceptions.SushiException(
            "The sushi5 module only supports release 5"
        )
    deprecated_args = set(kwargs) & DEPRECATED_KEYS
    if deprecated_args:  # pragma: no cover
        warnings.warn(
            DeprecationWarning(
                "The argument(s) %s are no longer used for SUSHI "
                "requests in COUNTER 5." % ", ".join(deprecated_args)
            )
        )
    unknown_args = set(kwargs) - DEPRECATED_KEYS
    if unknown_args:  # pragma: no cover
        warnings.warn(
            pycounter.exceptions.SushiWarning(
                "The arguments %s are not known for "
                "SUSHI requests in COUNTER 5." % ", ".join(deprecated_args)
            )
        )
