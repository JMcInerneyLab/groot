====================================================================================================
                                       Troubleshooting Groot                                        
====================================================================================================

.. attention::

    * Please see the Intermake_ troubleshooting guide for general issues
    * Please report all bugs on the `official bitbucket page`_.

.. contents::

----------------------------------------------------------------------------------------------------
                                           Using the GUI                                            
----------------------------------------------------------------------------------------------------

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Screen goes black, images or windows disappear                           
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Groot`:t: has been coded for multiple platforms, however, one or more settings may need changing
for your particular platform. 

* In the GUI, go to *Windows* -> *Preferences* and change the following settings:
    * Set the *MDI mode* to **basic**.
    * Set *OpenGL* **off**
    * Set *shared contexts* **off**.
    * Turn the inbuilt browser **off**
* Restart `Groot`:t:

    
----------------------------------------------------------------------------------------------------
                                       Running the algorithms                                       
----------------------------------------------------------------------------------------------------

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Issues with Paup                                          
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Until the official release of version 5.0 of `Paup`:t:, you can download time-expiring test versions
    of `Paup`:t: here
    --http://phylosolutions.com/paup-test

There are some major issues in using the `Paup`:t: test versions of Paup from `Groot`:t::

* Paup is being updated: changes to `Paup`:t:'s API frequently break `Groot`:t:'s interface to it.
* Paup test versions have programmed obsolescence: `Groot`:t: cannot link to a known, working version of Paup. 
* Paup does not report obsolescence errors in its return code: `Groot`:t: cannot know whether your version is up to date.

If you are using a test version of `Paup`:t: then please make sure it is up to date.
If this still doesn't work, submit `Groot`:t: interface bugs on the Bitbucket web page.
Until these issues are resolved with `Paup`:t:, consider using a different phylogeny tool such as Raxml_.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Handling multi-fusion sources                                        
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Groot is able to detect and handle the following cases:

* A normal fusion case: ``A + B --> F``
* A "lossy fission" or a fusion case where one side is not present in the data ``A --> F``

It is currently *unable* to detect:

* An n-parted fusion, or a multi-fusion case where one or more intermediates are not present in the data, ``A + B + C --> F``

Groot may still be able to deal with this circumstance, providing you guide it in the direction by specifying the fusion event manually.


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Handling the spaceship and the triangle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

.. _extending: extending.rst
.. _Raxml: https://sco.h-its.org/exelixis/software.html
.. _official bitbucket page: https://bitbucket.org/mjr129/groot/issues
.. _Intermake: https://www.bitbucket.org/mjr129/intermake

