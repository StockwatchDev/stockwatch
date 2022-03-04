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

Downloading data from De Giro
=============================

#. If not done before, create a folder where you want to store your portfolio files
#. Substitute the path of this folder in the file src\\stockwatch.py
#. Log in with De Giro
#. Select the Portfolio tab (Dutch: Portefeuille)
#. Hit the Export button
#. In the dialog that appears, select the date for which you want to download the data
#. Click CSV - as a result, a file Portfolio.csv will be downloaded to your computer
#. Move the downloaded file to the folder for storing portfolio files
#. Use the selected date info (step 6) to rename the relocated file to 
   yymmdd_Portfolio.csv
#. Repeat steps 5-9 for all dates that you want to visualize.

.. _python 3.10: https://www.python.org/downloads/
.. _poetry: https://python-poetry.org/docs/#installation
.. _Stockwatch repository: https://bitbucket.org/stockwatch-ws/stockwatch/src/develop/
