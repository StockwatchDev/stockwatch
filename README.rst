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

#. Create a folder that will be used to store files downloaded from De GIROand nothing
   else. We will refer to this as our STOCKWATCH_DIR hereafter
#. Create two subfolders in STOCKWATCH_DIR: Portfolio and Account

Downloading portfolio data from De Giro
=======================================

#. Log in with De Giro
#. Select the Portfolio tab (Dutch: Portefeuille)
#. Hit the Export button
#. In the dialog that appears, select the date for which you want to download the data
#. Click CSV - as a result, a file Portfolio.csv will be downloaded to your computer
#. Move the downloaded file to the STOCKWATCH_DIR/Portfolio folder
#. Use the selected date info (step 5) to rename the relocated file to
   yymmdd_Portfolio.csv
#. Repeat steps 4-8 for all dates that you want to visualize.

Downloading account data from De Giro
=======================================

#. Log in with De Giro
#. Select the Overviews tab (Dutch: Overzichten) and then the Account overview tab
   (Dutch: Rekeningoverzicht)
#. Select the period; make sure that it matches the period of the last Account download,
   that is, take the starting date of the period equal to the date following
   the end date of the last time that you downloaded Account info (see also step 7).
   If it is the first time that you are downloading Account info, then make sure that
   the period will include the first stock transaction of interest
#. Hit the Export button
#. Click CSV - as a result, a file Account.csv will be downloaded to your computer
#. Move the downloaded file to the STOCKWATCH_DIR/Account folder
#. Use the selected end date info (step 3) to rename the relocated file to
   yymmdd_Account.csv
#. Repeat steps 3-7 until you are at the current date.

Running and editing
===================

#. Create a virtual env shell using :code:`poetry shell`.
#. Start your prefered editor from this shell (ensure that the virtual env is still
   valid).
#. Run the stockwatch executable using:
   :code:`python src/stockwatch/stockwatch.py PATH/TO/STOCKWATCH_DIR` or to avoid
   adding the same path when running, export it in the `STOCKWATCH_PATH` environment
   variable.

Alternatively you can use :code:`poetry run python src/stockwatch/stockwatch.py` instead
of creating the virtual shell.

.. _python 3.10: https://www.python.org/downloads/
.. _poetry: https://python-poetry.org/docs/#installation
.. _Stockwatch repository: https://bitbucket.org/stockwatch-ws/stockwatch/src/develop/
