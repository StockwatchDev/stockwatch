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

Downloading portfolio data from De Giro
=======================================

#. If not done before, create a folder where you want to store your portfolio files
#. Log in with De Giro
#. Select the Portfolio tab (Dutch: Portefeuille)
#. Hit the Export button
#. In the dialog that appears, select the date for which you want to download the data
#. Click CSV - as a result, a file Portfolio.csv will be downloaded to your computer
#. Move the downloaded file to the folder for storing portfolio files
#. Use the selected date info (step 5) to rename the relocated file to
   yymmdd_Portfolio.csv
#. Repeat steps 4-8 for all dates that you want to visualize.

Downloading account data from De Giro
=======================================

#. Log in with De Giro
#. Select the Overviews tab (Dutch: Overzichten) and then the Account overview tab
   (Dutch: Rekeningoverzicht)
#. Select the period; take the starting date equal to the date following the end date
   of the last time that you downloaded Account info (see also step 7), or equal to
   the starting date if you are downloading for the first time
#. Hit the Export button
#. Click CSV - as a result, a file Account.csv will be downloaded to your computer
#. Move the downloaded file to the folder for storing portfolio files
#. Use the selected end date info (step 3) to rename the relocated file to
   yymmdd_Account.csv
#. Repeat steps 3-7 until you are at the current date.

Running and editing
===================

#. Create a virtual env shell using :code:`poetry shell`.
#. Start your prefered editor from this shell (ensure that the virtual env is still
   valid).
#. Run the stockwatch executable using:
   :code:`python src/stockwatch/stockwatch.py PATH/TO/FOLDER/WITH/DATA` or to avoid
   adding the same path when running, export it in the `STOCKWATCH_DIR` environment
   variable.

Alternatively you can use :code:`poetry run python src/stockwatch/stockwatch.py` instead
of creating the virtual shell.

.. _python 3.10: https://www.python.org/downloads/
.. _poetry: https://python-poetry.org/docs/#installation
.. _Stockwatch repository: https://bitbucket.org/stockwatch-ws/stockwatch/src/develop/
