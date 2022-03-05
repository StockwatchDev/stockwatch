=====================
README for Stockwatch
=====================

Stockwatch is an application (in development) for visualizing and analyzing a stock portfolio.
The portfolio is loaded by reading csv files that have been downloaded from De Giro.

Installation for development
============================

#. Make sure that you have `python 3.10`_ installed, preferably with as little extra packages as possible.
#. Make sure that you have `poetry`_ installed
#. Clone the `Stockwatch repository`_
#. Open a command prompt, go to the repo directory and run :code:`poetry install`. This command will create
   a virtual environment and install all needed dependencies.

.. _python 3.10: https://www.python.org/downloads/
.. _poetry: https://python-poetry.org/docs/#installation
.. _Stockwatch repository: https://bitbucket.org/stockwatch-ws/stockwatch/src/develop/

Running and editing
===================

#. Create a virtual env shell using :code:`poetry shell`.
#. Start your prefered editor from this shell (ensure that the virtual env is still valid).
#. Run the stockwatch executable using: :code:`python src/stockwatch/stockwatch.py`.

Alternatively you can use :code:`poetry run python src/stockwatch/stockwatch.py` instead of creating the
virtual shell.

