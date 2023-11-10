"""Test parsing of COUNTER 4 MR1 report"""


def test_metric_tsv(mr1_report_tsv):
    assert mr1_report_tsv.metric == "Multimedia Full Content Unit Requests"


def test_type_tsv(mr1_report_tsv):
    assert mr1_report_tsv.report_type == u"MR1"


def test_data_tsv(mr1_report_tsv):
    assert mr1_report_tsv.as_generic() == [
        [
            "Multimedia Report 1 (R4)",
            "Number of Successful Multimedia Full Content Unit Requests by Month and Collection",
        ],
        ["MyAccountName"],
        ["11111"],
        ["Period covered by Report:"],
        ["2018-01-01 to 2018-12-31"],
        ["Date run:"],
        ["2020-11-10"],
        [
            "Collection",
            "Content Provider",
            "Platform",
            "Reporting Period Total",
            "Jan-2018",
            "Feb-2018",
            "Mar-2018",
            "Apr-2018",
            "May-2018",
            "Jun-2018",
            "Jul-2018",
            "Aug-2018",
            "Sep-2018",
            "Oct-2018",
            "Nov-2018",
            "Dec-2018",
        ],
        [
            "Total for all collections",
            "",
            "MyPlatform",
            "15",
            "0",
            "3",
            "0",
            "1",
            "10",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "1",
        ],
        [
            "ItemName1",
            "MyPublisher",
            "MyPlatform",
            "11",
            "0",
            "0",
            "0",
            "1",
            "10",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
        ],
        [
            "ItemName2",
            "MyPublisher",
            "MyPlatform",
            "4",
            "0",
            "3",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "1",
        ],
    ]
