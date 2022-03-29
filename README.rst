=====================
README for Stockwatch
=====================

Stockwatch is an application (in development) for visualizing and analyzing a stock
portfolio. The portfolio is loaded by reading csv files that have been downloaded from
De Giro.

Installation for development
============================

#. Make sure that you have `python 3.10`_ installed, preferably with as little extra
   packages as possible.
#. Make sure that you have `poetry`_ installed
#. Clone the `Stockwatch repository`_
#. Open a command prompt, go to the repo directory and run :code:`poetry install`. This
   command will create a virtual environment and install all needed dependencies.

Importing files downloaded from De Giro
=======================================

#. Create a folder that will be used to store files downloaded from De GIRO and nothing
   else. We will refer to this as our STOCKWATCH_DIR hereafter
#. Create three subfolders in STOCKWATCH_DIR: *portfolio*, *account* and *indices*
#. The STOCKWATCH_DIR path can be defined in the environment variable STOCKWATCH_PATH
   to be picked up by the different scripts, or be put as last positional commandline
   argument

Downloading portfolio data from De Giro
=======================================

#. Log in with De Giro
#. Select the Portfolio tab (Dutch: Portefeuille)
#. Hit the Export button
#. In the dialog that appears, select the date for which you want to download the data
#. Click CSV - as a result, a file Portfolio.csv will be downloaded to your computer
#. Move the downloaded file to the STOCKWATCH_DIR/portfolio folder
#. Use the selected date info (step 5) to rename the relocated file to
   yymmdd_Portfolio.csv
#. Repeat steps 4-8 for all dates that you want to visualize.

Downloading account data from De Giro
=======================================

#. Log in with De Giro
#. Select the Overviews tab (Dutch: Overzichten) and then the Account overview tab
   (Dutch: Rekeningoverzicht)
#. Select the period; make sure that it matches the period of the last account download,
   that is, take the starting date of the period equal to the date following
   the end date of the last time that you downloaded account info (see also step 7).
   If it is the first time that you are downloading account info, then make sure that
   the period will include the first stock transaction of interest
#. Hit the Export button
#. Click CSV - as a result, a file Account.csv will be downloaded to your computer
#. Move the downloaded file to the STOCKWATCH_DIR/account folder
#. Use the selected end date info (step 3) to rename the relocated file to
   yymmdd_Account.csv
#. Repeat steps 3-7 until you are at the current date.

Downloading historical stock data for index comparisons
=======================================================

#. Go to `Yahoo Finance`_
#. Search for the stock or index you want to compare to.
#. Select the `historical data` tab of the stock/index.
#. Some stocks/indexes are not available to download, so check that the `download` button
   is available.
#. Select the time period used for the comparison (extra data is not a problem).
#. Select Frequency: `daily` to ensure the comparison is accurate enough.
#. Download the csv file, and put this in the STOCKWATCH_DIR/indices folder, name it
   *index_name*.csv where `_` are replaced by spaces in the plot legends.
#. When redrawing the figures the new index should be picked up automatically.

Running and editing
===================

#. Create a virtual env shell using :code:`poetry shell`.
#. Start your prefered editor from this shell (ensure that the virtual env is still
   valid).
#. Run the stockwatch executable using: :code:`python -m stockwatch --dash`
#. For help with the arguments use :code:`python -m stockwatch --help`.

Alternatively you can use :code:`poetry run python -m stockwatch` instead
of creating the virtual shell.

Scraping the porfolio data from De Giro
=======================================

Alternatively the portfolio data can be scraped with the scraping application
in this repo. Note that this application can easily break if De Giro updates
it's website, unfortunately it is therefore not guaranteed to work. If the
script breaks please raise an issue in the repo with the error output.

#. First login at DeGiro using your preferred browser.
#. Open the devtools window (F12 on firefox, and Chrome)
#. In the *network* tab, Search for a GET request to trader.degiro.nl
#. Search for the *intAccount* integer, and the *sessionId* string to
   input in the scraping application. In `Firefox`_ it can be found under
   *Headers*, whereas in `Chrome`_, and `Edge`_ it can be found under *Payload*.
#. Run the scraping application using
   :code:`python3 src/stockwatch/scraping/run.py accountId sessionId`
   the start and end date can be configured using the :code:`--start-date YYYY-MM-DD`
   and :code:`--end-date YYYY-MM-DD` commandline arguments. The script will put all
   the files in the STOCKWATCH_DIR/portfolio folder.


.. _Firefox: ./figs/devtools_firefox.png
.. _Chrome: ./figs/devtools_chrome.png
.. _Edge: ./figs/devtools_edge.png
.. _python 3.10: https://www.python.org/downloads/
.. _poetry: https://python-poetry.org/docs/#installation
.. _Stockwatch repository: https://bitbucket.org/stockwatch-ws/stockwatch/src/develop/
.. _Yahoo Finance: https://finance.yahoo.com
