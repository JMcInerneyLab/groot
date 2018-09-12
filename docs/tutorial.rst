========================================================
                     Groot Tutorial                     
========================================================

This tutorial concerns processing the sample "coleman" dataset in Gʀᴏᴏᴛ.

---------------------------------------------
               Getting started               
---------------------------------------------

Gʀᴏᴏᴛ has a pretty GUI wizard that will guide you through, but for this tutorial, we'll be using the CLI.
It's much easier to explain and we'll get to cover all the nice specifics.
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

.. note::

    The technical details of this workflow are already covered in the complementary paper_ and we won't be repeat these in the tutorial - we'll only be
    discussing how to perform it.

.. note::

    Gʀᴏᴏᴛ uses Intermake to read what you enter into the command line. See the `Intermake documentation`_ for exact syntax details and help. 

We'll assume you have Gʀᴏᴏᴛ installed and working as noted in `the installation guide`_, so start Gʀᴏᴏᴛ in CLI mode (if it isn't already):::

   ←    groot
        
   →    >>> Empty model>


Gʀᴏᴏᴛ's CLI has a simple interface.
Once Gʀᴏᴏᴛ has started, just type `help` for help::


   ←    help
   
   →    INF   help................................
        
        You are in command-line mode.
        ...

There are three groups of workflow commands in Gʀᴏᴏᴛ.
The ``create.`` commands are used to advance the workflow,
the ``drop.`` commands are used to go back a step,
and the ``print.`` commands are used to display information.
For instance, to create the alignments it's ``create.alignments``,
to view them it's ``print.alignments``, and to delete them and go back a step, it's ``drop.alignments``.

As an aside, there are also ``import.`` commands, which can be used in lieu of the ``create.`` commands to import data which is already known,
and ``file.`` commands used to load and save the model.

Type ``cmdlist`` to see all the commands now.

-------------------------------------------------------------
               Introduction to the sample data               
-------------------------------------------------------------

Gʀᴏᴏᴛ comes with a convenient sample library, get started by seeing what's available:::

    ←   file.sample
        
    →   INF seqgen
            sera
            simple
            triptych


.. note:: 

    The samples available will vary depending on which version of Gʀᴏᴏᴛ you are using.

The *triptych* sample contains a set of genes which have undergone two recombination events "X" and "Y":::

    ALPHA      BETA
      │         │
      └────┬────┘ X
           |
         DELTA         GAMMA
           │             │
           └──────┬──────┘ Y
                  |
               EPSILON


The final gene family, *EPSILON*, therefore looks something like this:::

    5'[ALPHA][BETA][GAMMA]3'

Let's pretend we don't already know this, and use Gʀᴏᴏᴛ to analyse the triptych.

------------------------------------------------
               Loading the sample               
------------------------------------------------

The `file.sample` command can be used to load the sample files automatically, but for the sake of providing a tutorial, we will be importing the data manually.
For reference, the ways of getting Gʀᴏᴏᴛ to do stuff with the minimal possible effort are listed in the table below.

+-------------------+-------------------------+--------------------------+
| Mode of operation | What it does            | How to get there         |
+-------------------+-------------------------+--------------------------+
| Wizard            | Does everything for you | Use the `wizard` command |
| GUI               | Shows you things        | Use the `gui` command    |
| Sample loader     | Loads samples           | Use the `sample` command |
+-------------------+-------------------------+--------------------------+

Unless you can remember where Pip installed the files to earlier, you can find out where the sample data is located by executing the following command:::

    ←   file.sample triptych +q
    
    →   INF import_directory "/blah/blah/blah/triptych"

The `+q` bit of our input tells Gʀᴏᴏᴛ not to actually load the data, so we can do it ourselves.
Gʀᴏᴏᴛ works out what you mean most of the time, so `+q` is equivalent to `true`, `+query`, `query=true`, `q=1`, etc.
The ``import_directory`` bit of the output tells us where the sample lives.
Write that down, and take note, your path will look different to mine!

You can now load the files into Gʀᴏᴏᴛ:::


    ←   import.blast /blah/blah/blah/triptych/triptych.blast
    
        import.fasta /blah/blah/blah/triptych/triptych.fasta

You should notice that at this point the prompt changes from *Empty model* to *Unsaved model*. Good times.

Unsaved model isn't very informative and serves as a reminder to *save our data*, so save our model with a more interesting name:::


    ←   save tri
        
    →   PRG  │ file_save...
        PRG  │ -Saving file...
        INF Saved model: /Users/martinrusilowicz/.intermake-data/groot/sessions/tri.groot

We didn't specify a path, or an extension, so you'll notice Gʀᴏᴏᴛ has added them for us.
Gʀᴏᴏᴛ uses directory in your home folder to store its data.
The directory is hidden by default to avoid bloating your home folder, but Gʀᴏᴏᴛ can remind you where it is (or change it!)
if you use the ``workspace`` command. 

-------------------------------------------------
               Preparing your data               
-------------------------------------------------

The linear workflow presented earlier can be shown in Gʀᴏᴏᴛ by, executing the ``status`` or ``print.status`` command:::

    ←   status
        
    →   INF tri
            /Users/martinrusilowicz/.intermake-data/groot/sessions/tri.groot
        
            Sequences
            Sequences:     55/55
            FASTA:         55/55
            Components:    0/55 - Consider running 'make.components'.
        
            Components
            Components:    0/0
            Alignments:    0/0
            Trees:         0/0
            Consensus:     0/0
            . . .

It should be clear what we have to do next:::


    ←   make.components
        
    →   PRG  │ make_components                                                                  │                                          │                         │ +00:00      ⏎
        PRG  │ -Component detection                                                             │ DONE                                     │                         │ +00:00      ⏎
        WRN There are components with just one sequence in them. Maybe you meant to use a tolerance higher than 0?

While not always the case, here, we can see Gʀᴏᴏᴛ has identified a problem. Well done Gʀᴏᴏᴛ.
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

Our components are messed up; Gʀᴏᴏᴛ has found 16 components, which is excessive, and many of these only contain one sequence.
Solve the problem by using a higher tolerance on the ``make.components`` command in order to allow some differences between the BLAST regions.
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
We can see each of the gene families (``A``, ``B``, ``C``, ``D``, ``E``) have been grouped into a component.

_Reminder: When you have arbitrary gene names things won't be so obvious, and that's where the GUI can be helpful!_
 
What next? Let's make a basic tree. For this we'll need the alignments.::

    ←   make.alignments

We didn't specify an algorithm so Gʀᴏᴏᴛ will choose one for us (probably MUSCLE_).
When complete, you can checkout your alignments by entering ``print.alignments``:::

    ←   print.alignments

Everything looks okay, so invoke tree-generation.
For the sake of this tutorial, we'll specify a Neighbour Joining tree, so we don't have to sit around all day.::

    ←   make.tree neighbor.joining

Neighbour Joining in Gʀᴏᴏᴛ requires PAUP_.
If you've not got PAUP then you'll get an error.
Type the following to see a list of what is available:::

    ←   help algorithms

In many circumstances tree generation can take a while, and you probably don't want to do it again if something goes wrong,
so make sure to save the model once you have your trees:::

    ←   save
    
    →   INF     Saved model: /Users/martinrusilowicz/.intermake-data/groot/sessions/tri.groot

This finally leaves us in a position to create the NRFG.


-----------------------------------------------
               Creating the NRFG               
-----------------------------------------------

We have a tree for each component now, but this isn't a graph, and the information in each tree probably conflicts.

Gʀᴏᴏᴛ has two methods of resolving this problem.

The first is by splitting and regrowing the tree, the second is by using peer reviewed tools such as CLANN_.
The first case can be useful in scrutinising your trees, but you almost certainly want to use the latter for your final NRFG.
  
A "split" defines a tree by what appears on the left and right of its edges.
Generate the list of all the possible splits:::

    ←   create.splits

And then find out which ones receive majority support in our trees:::

    ←   create.consensus

You can use ``print.consensus`` to check out your results.

Set the split data aside for the moment and generate the gene "subsets",
each subset is a portion of the original trees that is uncontaminated by a fusion event.::

    ←   create.subsets

Now we can combine these subsets with our consensus splits to make subgraphs - graphs of each subset that use only splits supported by our majority consensus.
We'll use CLANN for this like we talked about earlier.::

    ←   create.subgraphs clann

We can then create the NRFG by stitching these subgraphs back together.::

    ←   create.nrfg

Good good.
But the NRFG is not yet complete.
Stitching probably resulted in some trailing ends here and there, we need to trim these.::

    ←   create.clean

Finally, we can check the NRFG for errors.
If we have a graph with which to compare we could specify one here to see how things match up, but in most cases we won't, so just run:::

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

We didn't specify anything to compare to and our graph, being constructed from the sample data, should't have any problems, so our report will be pretty short.

Now you've done the tutorial, try using the GUI - it's a lot easier to check the workflow is progressing smoothly and you can view the trees and reports inline!


.. ***** REFERENCES AND DOCUMENT MARKUP FOLLOW *****

.. _`paper`: paper.md
.. _`the installation guide`: installation.md
.. _CLANN: http://mcinerneylab.com/software/clann/
.. _MUSCLE: https://www.ebi.ac.uk/Tools/msa/muscle/
.. _PAUP: http://evomics.org/resources/software/molecular-evolution-software/paup/
.. _`Intermake documentation`: http://software.rusilowicz.com/intermake
.. default_highlight:: bash
 
