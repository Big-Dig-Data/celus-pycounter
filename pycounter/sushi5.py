"""COUNTER 5 SUSHI support."""

import datetime
import logging
import time
import warnings

import pendulum
import requests

import pycounter.exceptions
from pycounter.helpers import convert_date_run
import pycounter.report


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
        if filter_["Name"] in ("Begin_Date", "End_Date")
    }
    try:
        return converted_filters["Begin_Date"], converted_filters["End_Date"]
    except KeyError:
        raise ValueError("filters must include a Begin_Date and End_Date")


def _raw_to_full(raw_report):
    """Convert a raw report to CounterReport.

    :param raw_report: raw report as dict decoded from JSON
    :return: a :class:`pycounter.report.CounterReport`
    """
    header = raw_report["Report_Header"]
    start_date, end_date = _dates_from_filters(header["Report_Filters"])
    date_run = header.get("Created")
    report_data = {
        "period": (start_date, end_date),
        "report_version": int(header["Release"]),
        "report_type": header["Report_ID"],
        "customer": header.get("Institution_Name", u""),
        "institutional_identifier": header.get("Customer_ID", u""),
        "date_run": pendulum.parse(date_run) if date_run else datetime.datetime.now(),
    }

    report = pycounter.report.CounterReport(**report_data)

    for item in raw_report["Report_Items"]:
        publisher_name = item.get("Publisher", u"")
        platform = item.get("Platform", u"")
        title = item["Title"]
        eissn = issn = doi = prop_id = u""
        # isbn = u""

        for identifier in item["Item_ID"]:
            if identifier["Type"] == "Print_ISSN":
                issn = identifier["Value"]
            elif identifier["Type"] == "Online_ISSN":
                eissn = identifier["Value"]
            # elif identifier["Type"] == "ISBN":
            #     isbn = identifier["Value"]
            elif identifier["Type"] == "DOI":
                doi = identifier["Value"]
            elif identifier["Type"] == "Proprietary_ID":
                prop_id = identifier["Value"]

        month_data = []

        for perform_item in item["Performance"]:
            item_date = convert_date_run(perform_item["Period"]["Begin_Date"])
            usage = None
            for inst in perform_item["Instance"]:
                if inst["Metric_Type"] == u"Total_Item_Requests":
                    usage = inst["Count"]
            if usage is not None:
                month_data.append((item_date, int(usage)))

        if report.report_type.startswith("TR_J"):
            report.pubs.append(
                pycounter.report.CounterJournal(
                    title=title,
                    platform=platform,
                    publisher=publisher_name,
                    period=report.period,
                    metric=report.metric,
                    issn=issn,
                    eissn=eissn,
                    doi=doi,
                    proprietary_id=prop_id,
                    month_data=month_data,
                )
            )

    return report


def get_sushi_stats_raw(
    wsdl_url=None,
    start_date=None,
    end_date=None,
    requestor_id=None,
    requestor_email=None,
    requestor_name=None,
    customer_reference=None,
    customer_name=None,
    report="TR_J1",
    release=5,
    sushi_dump=False,
    verify=True,
    url=None,
):
    """Get SUSHI stats for a given site in dict (decoded from JSON) format.

    :param wsdl_url: (Deprecated; for backward compatibility with COUNTER 4 SUSHI
    code. Use `url` instead.) URL to API endpoint for this provider

    :param start_date: start date for report (must be first day of a month)

    :param end_date: end date for report (must be last day of a month)

    :param requestor_id: requestor ID as defined by SUSHI protocol

    :param requestor_email: requestor email address, if required by provider

    :param requestor_name: Internationally recognized organization name

    :param customer_reference: customer reference number as defined by SUSHI
        protocol

    :param customer_name: Internationally recognized organization name

    :param report: report type, values defined by SUSHI protocol

    :param release: report release number (should generally be `4`.)

    :param sushi_dump: produces dump of XML to DEBUG logger

    :param verify: bool: whether to verify SSL certificates

    :param url: str: URL to endpoint for this provider

    """
    if url is None and wsdl_url:
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

    response = requests.get(
        "{url}/reports/{report}".format(**url_params),
        params=req_params,
        headers={"User-Agent": "pycounter/%s" % pycounter.__version__},
    )

    if sushi_dump:
        logger.debug(
            "SUSHI DUMP: request: %s \n\n response: %s",
            vars(response.request),
            response.content,
        )

    return response.json()


def get_report(*args, **kwargs):
    """Get a usage report from a COUNTER 5 (RESTful) SUSHI server.

    returns a :class:`pycounter.report.CounterReport` object.

    parameters: see get_sushi_stats_raw

    :param no_delay: don't delay in retrying Report Queued
    """
    no_delay = kwargs.pop("no_delay", False)
    delay_amount = 0 if no_delay else 60
    while True:
        try:
            raw_report = get_sushi_stats_raw(*args, **kwargs)
            return _raw_to_full(raw_report)
        except pycounter.exceptions.ServiceBusyError:
            print("Service busy, retrying in %d seconds" % delay_amount)
            time.sleep(delay_amount)
