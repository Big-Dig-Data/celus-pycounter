celus-pycounter
===============

celus-pycounter makes working with `COUNTER <http://www.projectcounter.org/>`_
usage statistics in Python easy, including fetching statistics with NISO
`SUSHI <http://www.niso.org/workrooms/sushi>`_.

A simple command-line client for fetching JR1 reports from SUSHI servers
and outputting them as tab-separated COUNTER 4 reports is included.

Developed by the `Health Sciences Library System <http://www.hsls.pitt.edu>`_ 
of the `University of Pittsburgh <http://www.pitt.edu>`_  to support importing
usage data into our in-house Electronic Resources Management (ERM) system.

Forked by `Big Dig Data s.r.o. <https://www.bigdigdata.com/>`

Licensed under the `MIT <https://choosealicense.com/licenses/mit/>`_ license.
See the file LICENSE for details.


Installing
----------
From `pypi <https://pypi.org/project/celus-pycounter/>`_:

    pip install celus-pycounter

From inside the source distribution:

    pip install [-e] .

(use -e if you plan to work on the source itself, so your changes are used in your installation.
Probably do all of this in a virtualenv. `The PyPA <https://packaging.python.org/tutorials/installing-packages/>`_
has a good explanation of how to get started.)


COUNTER 5 Note
--------------

In this release, reports are output in COUNTER 4 format with COUNTER 5 data,
which is wrong, and probably not a valid apples-to-apples comparison since, for example,
TR_J1 excludes Gold Open Access counts that would be included in JR1, and also has
HTML and PDF columns that will always be 0 because these are no longer reported.

Before the 3.0 release, it should be capable of producing actual COUNTER 5 reports,
probably with an API for getting COUNTER 4 style data compatible with scripts that
were making assumptions about the data received to pass it into another system.

Usage
-----

Parsing COUNTER reports (currently supports 4 in .csv, .tsv,
or .xlsx files, reports JR1, JR2, DB1, DB2, BR1, BR2, and BR3) and COUNTER 5::

    >>> import celus_pycounter.report
    >>> report = celus_pycounter.report.parse("COUNTER4_2015.tsv")  # filename or path to file
    >>> print(report.metric)
    FT Article Requests
    >>> for journal in report:
    ...     print(journal.title)
    Sqornshellous Swamptalk
    Acta Mattressica
    >>> for stat in report.pubs[0]:
    ...     print(stat)
    (datetime.date(2015, 1, 1), 'FT Article Requests', 120)
    (datetime.date(2015, 2, 1), 'FT Article Requests', 42)
    (datetime.date(2015, 3, 1), 'FT Article Requests', 23)
    
Fetching SUSHI data::

    >>> import celus_pycounter.sushi
    >>> import datetime
    >>> report = celus_pycounter.sushi.get_report(wsdl_url='http://www.example.com/SushiService',
    ...     start_date=datetime.date(2015,1,1), end_date=datetime.date(2015,1,31),
    ...     requestor_id="myreqid", customer_reference="refnum", report="JR1",
    ...     release=4)
    >>> for journal in report:
    ...     print(journal.title)
    Sqornshellous Swamptalk
    Acta Mattressica

Output of report as TSV::

    >>> report.write_tsv("/tmp/counterreport.tsv")


Development
-----------
Our code is automatically styled using black. To install the pre-commit hook:

    pip install pre-commit

    pre-commit install

