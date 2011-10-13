Using callPopPy on Windows
==========================

This information is additional to that in README - read that too!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

callPopPy is a Python script and requires the Python interpreter to 
run. Windows does not come with Python installed by default. Python
can be downloaded from 

http://www.python.org/getit/windows/

You should use the latest version in the 2.7 branch. Do not use 
version 3 as some of the libraries that callPopPy needs do not yet
work under version 3.

Dependencies
============

callPopPy depends on a number of third party libraries. These are
brief notes on what you'll need and where to find them:

twisted.internet
----------------

The version of twisted.internet appropriate to your version of 
Python can be grabbed as either an .msi or an .exe installer from

http://twistedmatrix.com/trac/wiki/Downloads

Just run the installer

zope.interface
--------------

twisted itself depends on zope.interface, which you'll find at

http://pypi.python.org/pypi/zope.interface

zope is distributed as an 'egg' file. The easiest way to install this
is to grab setuptools from

http://pypi.python.org/pypi/setuptools

which comes as a .exe installer. Run the installer. Assuming that your
Python installation is at c:\Python27 this will install a file at 
c:\Python27\Scripts\easy_install.exe

Drag and drop the '.egg' file on to this and zope should be installed.

starPy
------

Grap the source from

http://www.vrplumber.com/programming/starpy/

and unpack. From a command prompt go into the directory you unpacked it
to and run

> c:\Python27\python setup.py install

pygtk
-----

pygtk can be found at http://www.pygtk.org/

An 'all-in-one' installer is available as a .msi, containing several 
needed libraries. Grab this and run it.

pysqlite
--------

This is available as a .exe installer from
http://pypi.python.org/pypi/pysqlite/

Grab the installer and run it.

Running callPopPy
=================

Initially you should try running callPopPy from a command prompt. cd 
into the directory you have unpacked it too and run something like

> c:\Python27\python callpoppy

This way you'll see any messages about errors. Once you're sure it's
all working you may want to rename the file to callpoppy.pyw. You can 
then run it by double clicking on it. You can also create a shortcut 
in your startup folder to cause callPopPy to run at login.