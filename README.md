# Stockwatch

Stockwatch is an application (in development) for visualizing and analyzing a stock
portfolio. The portfolio is loaded by reading csv files that have been downloaded from
De Giro.

[TOC]

## Installation for development

1. Make sure that you have [python 3.10] installed, preferably with as little extra
   packages as possible.
2. Make sure that you have [poetry] installed
3. Clone the [Stockwatch repo]
4. Open a command prompt, go to the repo directory and run `poetry install`. This
   command will create a virtual environment and install all needed dependencies.

## Importing files downloaded from De Giro

1. Create a folder that will be used to store files downloaded from De GIRO and nothing
   else. We will refer to this as our STOCKWATCH\_DIR hereafter
2. Create three subfolders in STOCKWATCH\_DIR: *portfolio*, *account* and *indices*
3. The STOCKWATCH\_DIR path can be defined in the environment variable STOCKWATCH\_PATH
   to be picked up by the different scripts, or be put as last positional commandline
   argument

## Download data manually

The data used for the analysis in the stockwatch application can be downloaded manually.
There is also an automatic scraper created for the portfolio data, which can be found
[here](#markdown-header-scraping-the-porfolio-data-from-de-giro)

### Portfolio data (stock positions)

1. Log in with De Giro
2. Select the Portfolio tab (Dutch: Portefeuille)
3. Hit the Export button
4. In the dialog that appears, select the date for which you want to download the data
5. Click CSV - as a result, a file Portfolio.csv will be downloaded to your computer
6. Move the downloaded file to the STOCKWATCH\_DIR/portfolio folder
7. Use the selected date info (step 5) to rename the relocated file to
   yymmdd\_Portfolio.csv
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

## Running and editing

1. Create a virtual env shell using `poetry shell`.
2. Start your preferred editor from this shell (ensure that the virtual env is still
   valid).
3. Run the stockwatch executable using: `python -m stockwatch --dash`
4. For help with the arguments use `python -m stockwatch --help`.

Alternatively you can use `poetry run python -m stockwatch` instead
of creating the virtual shell.

## Scraping the porfolio data from De Giro

Alternatively the portfolio data can be scraped with the scraping application
in this repo. Note that this application can easily break if De Giro updates
it's website, unfortunately it is therefore not guaranteed to work. If the
script breaks please raise an issue in the repo with the error output.

1. First login at DeGiro using your preferred browser.
2. Open the devtools window (F12 on firefox, and Chrome)
3. In the *network* tab, Search for a GET request to trader.degiro.nl
4. Search for the *intAccount* integer, and the *sessionId* string to
   input in the scraping application. In [Firefox] it can be found under
   *Headers*, whereas in [Chrome], and [Edge] it can be found under *Payload*.
5. Run the scraping application using
   `python3 src/stockwatch/scraping/run.py accountId sessionId`
   the start and end date can be configured using the `--start-date YYYY-MM-DD`
   and `--end-date YYYY-MM-DD` commandline arguments. The script will put all
   the files in the STOCKWATCH\_DIR/portfolio folder.

## Running the tests

To run all the static-code analysis, and unit-tests the [tox] framework is
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
