===============================================================
                     Troubleshooting Groot                     
===============================================================

* Please report all bugs on the `official bitbucket page`_.
* Please also see the Intermake_ documentation for handling technical issues.


---------------
Groot not found
---------------

If you see the Groot command prompt that's great, it works, but if you get a message like ``groot not found`` then
Python probably doesn't have its PATH configured correctly.
You might be able to start Groot using ``python -m groot``, but it's probably best to consult the Python documentation
at this time and fix the issue before continuing.
You probably need to add the Python binaries to your path, using a command something like:::

    export PATH=$PATH:/opt/local/Library/Frameworks/Python.framework/Versions/3.6/bin

Check out `this StackOverflow post`_ as a starting point.


----------------------------------------------
Screen goes black, images or windows disappear
----------------------------------------------

Groot has been coded for multiple platforms, however, one or more settings may need changing for your particular platform. 

* In the GUI, go to *Windows* -> *Preferences* and change the following settings:
    * Set the *MDI mode* to **basic**.
    * Set *OpenGL* **off**
    * Set *shared contexts* **off**.
    * Turn the inbuilt browser **off**
* Restart GROOT

------------------
Obtaining binaries
------------------

Binaries are not available, installation `using Pip`_ is the recommended method.
For deployment on systems without an internet connection, you can create your own binaries using PyInstaller_.::

    $   cd groot
    $   pyinstaller groot/__main__.py

----------------
Issues with Paup
----------------

    Until the official release of version 5.0 of PAUP*, you can download time-expiring test versions of PAUP* here
    --http://phylosolutions.com/paup-test

There are some major issues in using the Paup test versions of Paup from Groot:

* Paup is being updated: changes to Paup's API frequently break Groot's interface to it.
* Paup test versions have programmed obsolescence: Groot cannot link to a known, working version of Paup. 
* Paup does not report obsolescence errors in its return code: Groot cannot know whether your version is up to date.

If you are using a test version of Paup then please make sure it is up to date.
If this still doesn't work, submit Groot interface bugs on the Bitbucket web page.
Until these issues are resolved with Paup, consider using a different phylogeny tool such as Raxml_.


--------------------
Multi-fusion sources
--------------------

Groot is able to detect and handle the following cases:

* A normal fusion case: ``A + B --> F``
* A "lossy fission" or a fusion case where one side is not present in the data ``A --> F``

It is currently *unable* to detect:

* An n-parted fusion, or a multi-fusion case where one or more intermediates are not present in the data, ``A + B + C --> F``

Groot may still be able to deal with this circumstance, providing you guide it in the direction by specifying the fusion event manually.


------------------------------
The spaceship and the triangle
------------------------------

There are a couple of cases that Groot will suffer from.

The first is the spaceship (Figure 1, below) which is a specific variant of Case 4 (above) in which ``A1=A2`` and ``B1=B2``.
If two fusion events (``C`` and ``D``) occur at the same time, this isn't distinguishable from the normal case of one fusion
event (``X``) that later diverges into two lineages (``C`` and ``D``) (Figure 2).
However, if you know (or wish to pretend) that this is the case, you can specify the Groot components manually, rather than
letting Groot infer them.

The second problematic case is the triangle (Figure 3), which is also a specific variant of Case 4 in which ``A1=A2`` and ``B1≠B2``.
This scenario *initially* looks like the spaceship (Figure 1).
However, things become apparent once Groot runs down to the NRFG stage, since the fusion will be malformed (Figure 4), with 3 origins,
one output (``CD``) but only 2 input components (``A``, ``B``).
At the present time, Groot doesn't remedy this situation automatically and you'll need to rectify the problem yourself.
From your Figure-4-like result, write down or export the sequences in each of your lineages ``A``, ``B``, ``C`` and ``D``.
Then, go back to the component stage and specify your components manually: ``A``, ``B``, ``C`` and ``D``.


::

    A───────┬────>
            │\
            │ ───────────┐
            │            │
            C─────>      D──────────>
            │            │
            │ ───────────┘
            │/
    B───────┴────>

Figure 1. The spaceship

::

    A───────┬────>
            │
            │ C─────>
            │/
            X
            │\
            │ D─────>
            │
    B───────┴────>

Figure 2. Normal case

::

    A─────┬──────>
          │\
          │ \
          │  ────────────D─────>
          │              │
          C─────>        │
          │              │
          │              │
          │              │
    B─────┴──────────────┴───>

Figure 3. The triangle

::

    A─────┬──────>
          │
          │
          └──────────   D
                     \ /
                      X
                     /│\
          ┌────────── | C
          │           |
    B─────┴───────────┴───>

Figure 4. The failed triangle

.. ***** REFERENCES AND FURTHER RST MARKUP FOLLOW *****

.. _PyInstaller: https://www.pyinstaller.org/

.. _Raxml: https://sco.h-its.org/exelixis/software.html

.. _using Pip: installation.md

.. _official bitbucket page: https://bitbucket.org/mjr129/groot/issues

.. _Intermake: https://www.bitbucket.org/mjr129/intermake

.. _this StackOverflow post: https://stackoverflow.com/questions/35898734/pip-installs-packages-successfully-but-executables-not-found-from-command-line?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

