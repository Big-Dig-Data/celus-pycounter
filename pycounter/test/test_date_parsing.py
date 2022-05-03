import os

import pytest

import pycounter


class TestDateParsing:

    @pytest.mark.parametrize(['infile'], [
        ('BR1-missing-months.csv',), ('BR1-ok-months.csv',)
    ])
    def test_with_header_before(self, infile):
        """
        Test that when the C4 header refers to months that are not present in the data,
        that the actual months are not messed up.

        In the file at hand, the header says 'Period covered by report: 2020-01 to 2021-12',
        but data are there only for 2021-01 to 2021-12. Pycounter must not report the data as
        being from 2020 when they are from 2021
        """
        report = pycounter.report.parse(
            os.path.join(os.path.dirname(__file__), f"data/{infile}")
        )
        assert report.year == 2021
        for journal in report:
            months = {str(start) for start, metric, value in journal}
            assert months == {f'2021-{m:02d}-01' for m in range(1, 13)}



