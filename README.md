<h1 id="header">Stockwatch</h1>

[![Build Status](https://github.com/StockwatchDev/stockwatch/actions/workflows/stockwatch-tests.yml/badge.svg?branch=develop)](https://github.com/StockwatchDev/stockwatch/actions)
[![codecov](https://codecov.io/gh/StockwatchDev/stockwatch/branch/develop/graph/badge.svg)](https://app.codecov.io/gh/StockwatchDev/stockwatch)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)


Stockwatch is an application (in development) for visualizing and analyzing a stock
portfolio. The portfolio is loaded by reading csv files that have been downloaded from
De Giro.

# Installation for development

1. Make sure that you have [python 3.10] installed, preferably with as little extra
   packages as possible.
2. Make sure that you have [poetry] installed
3. Clone the [Stockwatch repo]
4. Open a command prompt, go to the repo directory and run `poetry install`. This
   command will create a virtual environment and install all needed dependencies.

# Downloading stock data

## Importing files downloaded from De Giro
For the application to be able to find the downloaded data, a certain folder structure
is required.

1. Create a folder that will be used to store files downloaded from De GIRO and nothing
   else. We will refer to this as our STOCKWATCH\_DIR hereafter
2. Create three subfolders in STOCKWATCH\_DIR: *portfolio*, *account* and *indices*
3. The STOCKWATCH\_DIR path can be defined in the environment variable STOCKWATCH\_PATH
   to be picked up by the different scripts, or be put as last positional commandline.
   For help on environment variables see: [Windows][WindowsEnv], [Linux][LinuxEnv].

## Scraping using the app

Currently the portfolio data can be scraped using the Dash application. This will
eventually be extended to all data. To scrape data using the webbrowser start the
Stockwatch app and navigate to the `scrape` tab, and follow these instructions:

1. Put in the username / password in the respective fields
2. Specify the start and end date that you're interested in.
3. Put in the Google Authenticator one-time password in the Time-based One Time
   Password (TOTP) field, note that the TOTP is only valid for a limited time.
4. Press import to start importing.

## Download data manually

The data used for the analysis in the stockwatch application can be downloaded manually.
There is also an automatic scraper for the portfolio data, more about this
[here](#markdown-header-scraping-the-porfolio-data-from-de-giro)

### Portfolio data (stock positions)

1. Log in with De Giro
2. Select the Portfolio tab (Dutch: Portefeuille)
3. Hit the Export button
4. In the dialog that appears, select the date for which you want to download the data
5. Click CSV - as a result, a file Portfolio.csv will be downloaded to your computer
6. Move the downloaded file to the STOCKWATCH\_DIR/portfolio folder
7. Use the selected date info (step 5) to rename the relocated file to
   yymmdd\_portfolio.csv
8. Repeat steps 4-8 for all dates that you want to visualize.

### Account data (transactions)

1. Log in with De Giro
2. Select the Overviews tab (Dutch: Overzichten) and then the Account overview tab
   (Dutch: Rekeningoverzicht)
3. Select the period; make sure that it matches the period of the last account download,
   that is, take the starting date of the period equal to the date following
   the end date of the last time that you downloaded account info (see also step 7).
   If it is the first time that you are downloading account info, then make sure that
   the period will include the first stock transaction of interest
4. Hit the Export button
5. Click CSV - as a result, a file Account.csv will be downloaded to your computer
6. Move the downloaded file to the STOCKWATCH\_DIR/account folder
7. Use the selected end date info (step 3) to rename the relocated file to
   yymmdd\_Account.csv
8. Repeat steps 3-7 until you are at the current date.

### Other indices

1. Go to [Yahoo Finance]
2. Search for the stock or index you want to compare to.
3. Select the `historical data` tab of the stock/index.
4. Some stocks/indexes are not available to download, so check that the `download` button
   is available.
5. Select the time period used for the comparison (extra data is not a problem).
6. Select Frequency: `daily` to ensure the comparison is accurate enough.
7. Download the csv file, and put this in the STOCKWATCH\_DIR/indices folder, name it
   *index_name*.csv where `_` are replaced by spaces in the plot legends.
8. When redrawing the figures the new index should be picked up automatically.

# Running and editing

1. Create a virtual env shell using `poetry shell`.
2. Run the stockwatch executable using: `python -m stockwatch`
3. For help with the arguments use `python -m stockwatch --help`.
4. Start your preferred editor from the poetry shell (this ensures that
   the virtual env is still valid).

Alternatively you can use `poetry run python -m stockwatch` instead
of creating the virtual shell.

# Running the tests

To run all the static-code analyses, and unit-tests the [tox] framework is
used. For running the all checks simply execute the `tox` command from
within the repo (while having a poetry shell, otherwise run `poetry run tox`).

[Firefox]: ./figs/devtools_firefox.png
[Chrome]: ./figs/devtools_chrome.png
[Edge]: ./figs/devtools_edge.png
[tox]: https://tox.wiki/en/latest/index.html
[python 3.10]: https://www.python.org/downloads/
[poetry]: https://python-poetry.org/docs/#installation
[Stockwatch repo]: https://bitbucket.org/stockwatch-ws/stockwatch/src/develop/
[Yahoo Finance]: https://finance.yahoo.com
[WindowsEnv]: https://docs.oracle.com/en/database/oracle/machine-learning/oml4r/1.5.1/oread/creating-and-modifying-environment-variables-on-windows.html#GUID-DD6F9982-60D5-48F6-8270-A27EC53807D0
[LinuxEnv]: https://unix.stackexchange.com/a/117470
