====================================================================================================
                                        |app_name| Tutorial                                         
====================================================================================================

This tutorial concerns processing the sample "coleman" dataset in |app_name|.

----------------------------------------------------------------------------------------------------
                                          Getting started                                           
----------------------------------------------------------------------------------------------------

|app_name| has a beautiful GUI wizard that will guide you through, but for this tutorial, we'll be
using the Python interactive interface. Whilst not visually appealing, this interface is much easier
to explain and we'll get to cover all the nice specifics.

The workflow we'll be following looks like this:

#. Load FASTA data
#. Make similarity matrix
#. Make major components
#. Make minor components
#. Make alignments
#. Make trees
#. Make fusions
#. Candidate splits
#. Viable splits
#. Subsets
#. Pregraphs
#. Subgraphs
#. Fuse
#. Clean
#. Check

The technical details of this workflow are already covered in the complementary paper_ and we
won't be repeating them here, but we'll cover how to use them and what output you should expect. 

We'll assume you have |app_name| installed and working as noted in `the installation guide`_,
so start |app_name| in Python Interactive mode (if it isn't already):::

   ←    groot pyi
        
   →    GROOT 0.0.0.40 Python Interactive
   
        groot>

.. note::
 
    Groot has other flavours of UI available - a graphical user interface, a command line
    interactive mode, a python scripted mode, and a mode for Jupyter notebooks. See
    the `Intermake documentation`_ for more details.

Once |app_name| has started, type :func:`help` for help::


   ←    help()
   
   →    Welcome to groot. You are in Python interactive (PYI) mode.
        ...

There are five groups of workflow commands in |app_name|:

* The ``create_…`` commands are used to create data and advance the workflow
* The ``drop_…`` commands are used to go back a step,
* The ``print_…`` commands are used to display information
* The ``set_…`` and ``import_…`` commands are used to specify data manually or from a file.

For instance, to create the alignments it's :func:``create_alignments``,
to view them it's :func:``print_alignments``, and to delete them and go back a step, it's
:func:``drop_alignments``.
If you already had some alignments, you could use :func:``set_alignments`` or
:func:``import_alignments`` to read these in.

In addition to the workflow commands, there are the ``file_…`` commands which can be used to save and
load your progress on the workflow itself.

Use the :func:``cmdlist`` command to see all the |app_name| commands now::

    ←   cmdlist()

----------------------------------------------------------------------------------------------------
                                  Introduction to the sample data                                   
----------------------------------------------------------------------------------------------------

|app_name| comes with a convenient sample library, get started by seeing what's available:::

    ←   file_sample()
        
    →   seqgen
        sera
        simple
        triptych


.. note:: 

    The samples available will vary depending on which version of |app_name| you are using.

The *coleman* sample contains the dataset we will be working with.
The lego diagram depicting the fusion event looks something like this::

         [ALPHA]     [BETA]-----[GAMMA]
         |     |     |    |
         [ALPHA]-----[BETA]


Here we have three domains, ``ALPHA``, ``BETA`` and ``GAMMA``.
``[ALPHA]`` and ``[BETA]-[GAMMA]`` are our input gene families, the final gene family
``[ALPHA]-[BETA]`` is our fusion family. ``[GAMMA]`` is a domain not involved in the fusion event.

Let's pretend we don't already know any of this, and use |app_name| to analyse the fusion.

----------------------------------------------------------------------------------------------------
                                         Loading the sample                                         
----------------------------------------------------------------------------------------------------

The :func:`file_sample` command can be used to load the sample files automatically, but for the sake
of providing a tutorial, we will be importing the data manually.

.. note::

    |Groot| has several Wizards, which can perform the whole or part of the workflow for you. Use
    :func:`cmdlist` for more details. 

Unless you can remember where Pip installed the files to earlier, you can find out where the sample
data is located by executing the :func:`file_sample` command:::

    ←   file_sample("coleman", query=True)
    
    →   import_directory "/blah/blah/blah/triptych"

The ``query=True`` bit of our input tells |app_name| not to actually load the data and just tells
us where it lives, so we can load it ourselves. The ``import_directory`` bit of the output tells us
the answer.
Write that down, and take note, your path will look different to mine!

You can now load the files into |app_name| using :func:`import_genes`:::

    ←   import_genes("/blah/blah/blah/triptych/triptych.fasta")
    
    →   Imported Fasta from /Users/martinrusilowicz/work/apps/groot_data/coleman/F21/sequences.fasta.

You should notice that at this point the prompt changes from *Empty model* to *Unsaved model*.
Unsaved model isn't very informative and serves as a reminder to *save our data*, so save our model
with a more interesting name using :func:`file_save`:::


    ←   file_save("coleman")
        
    →   Saved model to /Users/martinrusilowicz/.intermake-data/groot/sessions/coleman.groot.

We didn't specify a path, or an extension, so you'll notice |app_name| has added them for us.
|app_name| uses directory in your home folder to store its data.
The directory is hidden by default to avoid bloating your home folder, but |app_name| can remind you
where it is (or change it!) if you use the :func:`workspace` command. 

----------------------------------------------------------------------------------------------------
                                        Preparing your data                                         
----------------------------------------------------------------------------------------------------

The linear workflow presented earlier can be shown in |app_name| by, executing the
:func:`print_status` command:::

    ←   print_status()
        
    →   Coleman
    
        | 0. File:             | /Users/martinrusilowicz/.intermake-data/groot/sessions/coleman.groot |
        | 1. Data:             | (partial) 25 of 25 sequences with site data. 0 edges                 |
        | 2. Fasta:            | 25 of 25 sequences with site data                                    |
        | 3. Blast:            | (no data) - Consider running create_blast                            |
        | 4. Major:            | (no data)                                                            |
        | 5. Minor:            | (no data|

It should be clear what we have to do next: use the :func:`create_similarities` command to run BLAST:::

    ←   create_similarities()
        
    →   Coleman




    ←   make.components
        
    →   PRG  │ make_components                                                                  │                                          │                         │ +00:00      ⏎
        PRG  │ -Component detection                                                             │ DONE                                     │                         │ +00:00      ⏎
        WRN There are components with just one sequence in them. Maybe you meant to use a tolerance higher than 0?

While not always the case, here, we can see |app_name| has identified a problem.
Well done |app_name|.
We can confirm this manually too:::

    ←   print.components
        
    →   INF ┌─────────────────────────────────────────────────────────────────────────┐
            │ major elements of components                                            │
            ├──────────────────────────────┬──────────────────────────────────────────┤
            │ component                    │ major elements                           │
            ├──────────────────────────────┼──────────────────────────────────────────┤
            │ α                            │ Aa, Ab, Ad, Ae, Af, Ag, Ah, Ai           │
            │ β                            │ Ak, Al                                   │
            │ γ                            │ Ba, Bb, Bd, Be                           │
            │ δ                            │ Bf, Bi, Bj, Bl                           │
            │ ϵ                            │ Bg, Bh                                   │
            │ ζ                            │ Ca, Cb, Cd, Ce, Cf, Cg, Ch, Ci, Cj, Ck,  │
            │                              │ Cl                                       │
            │ η                            │ Da, Db                                   │
            │ θ                            │ Dd, Df, Dg, Dh, Di, Dj, Dk, Dl           │
            │ ι                            │ Ea, Eg, Eh                               │
            │ κ                            │ Ef, Ei, Ej, Ek, El                       │
            │ λ                            │ Aj                                       │
            │ μ                            │ Bk                                       │
            │ ν                            │ De                                       │
            │ ξ                            │ Eb                                       │
            │ ο                            │ Ed                                       │
            │ π                            │ Ee                                       │
            └──────────────────────────────┴──────────────────────────────────────────┘

Our components are messed up; |app_name| has found 16 components, which is excessive, and many of these
only contain one sequence.
Solve the problem by using a higher tolerance on the ``make.components`` command in order to allow
some differences between the BLAST regions.
The default of zero will almost always be too low.
Try the command again, but specify a higher tolerance this time.::


    ←   make.components tolerance=10
        
    →   PRG  │ make_components                                                                  │                                          │                         │ +00:00      ⏎
        PRG  │ -Component detection                                                             │ DONE                                     │                         │ +00:00      ⏎

No error this time. let's see what we have:::

    ←   print.components
        
    →   INF ┌─────────────────────────────────────────────────────────────────────────┐
            │ major elements of components                                            │
            ├──────────────────────────────┬──────────────────────────────────────────┤
            │ component                    │ major elements                           │
            ├──────────────────────────────┼──────────────────────────────────────────┤
            │ α                            │ Aa, Ab, Ad, Ae, Af, Ag, Ah, Ai, Aj, Ak,  │
            │                              │ Al                                       │
            │ β                            │ Ba, Bb, Bd, Be, Bf, Bg, Bh, Bi, Bj, Bk,  │
            │                              │ Bl                                       │
            │ γ                            │ Ca, Cb, Cd, Ce, Cf, Cg, Ch, Ci, Cj, Ck,  │
            │                              │ Cl                                       │
            │ δ                            │ Da, Db, Dd, De, Df, Dg, Dh, Di, Dj, Dk,  │
            │                              │ Dl                                       │
            │ ϵ                            │ Ea, Eb, Ed, Ee, Ef, Eg, Eh, Ei, Ej, Ek,  │
            │                              │ El                                       │
            └──────────────────────────────┴──────────────────────────────────────────┘

At a glance it looks better.
We can see each of the gene families (``A``, ``B``, ``C``, ``D``, ``E``) have been grouped into a
component.

_Reminder: When you have arbitrary gene names things won't be so obvious, and that's where the GUI
can be helpful!_
 
What next? Let's make a basic tree. For this we'll need the alignments.::

    ←   make.alignments

We didn't specify an algorithm so |app_name| will choose one for us (probably MUSCLE_).
When complete, you can checkout your alignments by entering ``print.alignments``:::

    ←   print.alignments

Everything looks okay, so invoke tree-generation.
For the sake of this tutorial, we'll specify a Neighbour Joining tree, so we don't have to sit
around all day.::

    ←   make.tree neighbor.joining

Neighbour Joining in |app_name| requires PAUP_.
If you've not got PAUP then you'll get an error.
Type the following to see a list of what is available:::

    ←   help algorithms

In many circumstances tree generation can take a while, and you probably don't want to do it again
if something goes wrong,
so make sure to save the model once you have your trees:::

    ←   save
    
    →   INF     Saved model: /Users/martinrusilowicz/.intermake-data/groot/sessions/tri.groot

This finally leaves us in a position to create the NRFG.


----------------------------------------------------------------------------------------------------
                                         Creating the NRFG                                          
----------------------------------------------------------------------------------------------------

We have a tree for each component now, but this isn't a graph, and the information in each tree
probably conflicts.

|app_name| has two methods of resolving this problem.

The first is by splitting and regrowing the tree, the second is by using peer reviewed tools such
as CLANN_.
The first case can be useful in scrutinising your trees, but you almost certainly want to use the
latter for your final NRFG.
  
A "split" defines a tree by what appears on the left and right of its edges.
Generate the list of all the possible splits:::

    ←   create.splits

And then find out which ones receive majority support in our trees:::

    ←   create.consensus

You can use ``print.consensus`` to check out your results.

Set the split data aside for the moment and generate the gene "subsets",
each subset is a portion of the original trees that is uncontaminated by a fusion event.::

    ←   create.subsets

Now we can combine these subsets with our consensus splits to make subgraphs - graphs of each subset
that use only splits supported by our majority consensus.
We'll use CLANN for this like we talked about earlier.::

    ←   create.subgraphs clann

We can then create the NRFG by stitching these subgraphs back together.::

    ←   create.nrfg

Good good.
But the NRFG is not yet complete.
Stitching probably resulted in some trailing ends here and there, we need to trim these.::

    ←   create.clean

Finally, we can check the NRFG for errors.
If we have a graph with which to compare we could specify one here to see how things match up, but
in most cases we won't, so just run:::

    ←   create.checks

And we're all done!

To print out your final graph:::

    ←   print.tree nrfg.clean cyjs open

This says:

* ``print`` the ``.tree``
* called ``nrfg.clean``
* using Cytoscape.JS (``cyjs``)
* and ``open`` the result (using the default application)

You can also use ``print.report`` to print out your final summary in much the same way.::

    ←   print.report final.report open

We didn't specify anything to compare to and our graph, being constructed from the sample data,
should't have any problems, so our report will be pretty short.

Now you've done the tutorial, try using the GUI - it's a lot easier to check the workflow is
progressing smoothly and you can view the trees and reports inline!


.. ***** REFERENCES AND DOCUMENT MARKUP FOLLOW *****

.. |app_name| replace:: :t:`Groot`
.. _`paper`: paper.md
.. _`the installation guide`: installation.md
.. _CLANN: http://mcinerneylab.com/software/clann/
.. _MUSCLE: https://www.ebi.ac.uk/Tools/msa/muscle/
.. _PAUP: http://evomics.org/resources/software/molecular-evolution-software/paup/
.. _`Intermake documentation`: http://software.rusilowicz.com/intermake
.. default_highlight:: bash
 
