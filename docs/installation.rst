====================================================================================================
                                         Groot Installation                                         
====================================================================================================

----------------------------------------------------------------------------------------------------
                                           Prerequisites                                            
----------------------------------------------------------------------------------------------------

`Groot`:t: runs under Python 3.6+ and should be installed using `Pip`:t:.

* In addition to `Python`:t:, you will also need some phylogenetic tools to conduct the actual
  analysis.
* Please download the the following, install, *and confirm that they run* from the command line
  before continuing to install Groot.

=========== ======================== ================================================== 
Tool        Purpose                  URL                                               
=========== ======================== ==================================================
Blast       Gene similarity          https://blast.ncbi.nlm.nih.gov/Blast.cgi          
Clann       Supertree inference      http://mcinerneylab.com/software/clann/           
Muscle      Gene alignment           https://www.ebi.ac.uk/Tools/msa/muscle/           
Paup        Phylogeny inference      http://phylosolutions.com/paup-test/              
Pip         Installation manager     https://pip.pypa.io/en/stable/installing/         
Python      Interpreter              https://www.python.org/downloads/                 
Raxml       Phylogeny inference      https://sco.h-its.org/exelixis/software.html      
=========== ======================== ==================================================

.. note::

    You can substitute all of these for your own preferred tools, or specify the data manually, but
    this list comprises a good "starter pack".

.. note::

    Make sure to place your binaries in your system PATH_ so that they can be accessed by Groot.

.. warning::

    For legacy reasons, `MacOS`:t: and some `Linux`:t: flavours come with an older version of
    `Python 2.4`:t: pre-installed, which was last updated in 2006.
    This isn't enough - you'll need to install `Python 3.6`:t: to use Groot.

----------------------------------------------------------------------------------------------------
                                        System requirements                                         
----------------------------------------------------------------------------------------------------

`Groot`:t: isn't very fussy, it will work from your `Android`:t: phone (albeit slowly) but if you
want to use the GUI you'll need to be using a supported OS and desktop (`Windows`:t:, `Mac`:t: and
`Ubuntu`:t:+`Kde`:t: or `Ubuntu`:t:+`Gnome`:t: are all good). See the troubleshooting_ guide if you get into problems.


----------------------------------------------------------------------------------------------------
                                     Installing Groot Using Pip                                     
----------------------------------------------------------------------------------------------------

When all is ready, download `Groot`:t: using `Pip`:t:, i.e. from the `Windows`:t: console... ::

    [console]$   pip install groot

...or, from a `Bash`:t: terminal... ::


    [bash]$   sudo pip install groot

If you don't have administrator access, you can use `virtualenv`:t:::


    [bash]$             virtualenv grootling
    [bash]$             source grootling/bin/activate
    [bash/grootling]$   pip install groot

After the install completes, test that you can actually run `Groot`:t:::


    [bash]$   groot


.. note::

    If `Groot`:t: fails to start then your ``PATH`` is incorrectly configured.
    Use ``python -m groot`` instead, or see the
    `troubleshooting section on Groot not found<troubleshooting.rst#groot-not-found>`_.


----------------------------------------------------------------------------------------------------
                                    Starting and stopping Groot                                     
----------------------------------------------------------------------------------------------------

You should be able to start `Groot`:t: in its *Command Line Interactive* (CLI) mode straight from the
command line::

    [bash]$   groot

Groot operates in a number of UI modes, CLI mode is a scripted mode that acts like passing arguments
from the command line, for instance the following two scripts are the same::


    [bash]$    groot
    [groot]$   echo "hello world"
    [groot]$   exit

(and)::

    [bash]$   groot echo "hello world"

Perhaps more intuitively, you can use `Groot`:t: from `Python`:t: instead::

    [bash]$             groot pyi
    [python-groot]$     echo("hello world")
    [python-groot]$     exit()

You can start `Groot`:t: in a *Graphical User Interface* (GUI) mode by passing the `gui` argument::

    [bash]$   groot gui


Finally, you can also use `Groot`:t: in your own applications via the python ``import`` command::

    [bash]$     python
    [python]$   import groot

For advanced functionality, see the `Intermake documentation`_.

----------------------------------------------------------------------------------------------------
                                   Installation from source code                                    
----------------------------------------------------------------------------------------------------

`Groot`:t: can be cloned using and installed in development mode by cloning the `Git`:t: repository.
Some technical knowledge is required - if you are in doubt, use `Pip`:t: as described above.::

    [bash]$     git clone https://www.bitbucket.org/mjr129/groot.git
    [bash]$     cd groot
    [bash]$     pip install -e .


.. warning::

    When installing from source you will still need to manually install the other prerequisites
    first!





.. ********** REFERENCES **********

.. _PATH: https://en.wikipedia.org/wiki/PATH_(variable)
.. _`Intermake documentation`: http://software.rusilowicz.com/intermake
.. _troubleshooting: troubleshooting.rst
