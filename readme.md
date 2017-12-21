Groot
=====
Gʀᴏᴏᴛ imports Bʟᴀꜱᴛ data and produces a genomic [N-Rooted Fusion Graph](https://doi.org/10.1093/molbev/mst228).

[](toc)

Installation
------------

Please download Gʀᴏᴏᴛ using [Pɪᴩ](https://packaging.python.org/tutorials/installing-packages), i.e. from Bᴀꜱʜ:

```bash
$   sudo pip install groot
```

You can then start Gʀᴏᴏᴛ in _Command Line Interactive_ (CLI) mode:

```bash
$   groot
```

_...or in _Graphical User Interface_ (GUI) mode:_

```bash
$   groot gui
```

You can also use Gʀᴏᴏᴛ in your own Python applications:

```python
$   import groot
```

For other modes, please see the `Iɴᴛᴇʀᴍᴀᴋᴇ` documentation.

If the `groot` command does not start Gʀᴏᴏᴛ then you have not set Pʏᴛʜᴏɴ up correctly.

Tutorial
--------

### Introduction ###

### Getting started ###

For this tutorial, we'll be using the CLI, because it's much easier to explain.

Start Gʀᴏᴏᴛ in CLI mode (if it isn't already):

```bash
$   groot
    >>> Empty model>
```

Once in Gʀᴏᴏᴛ, type `help` for help.

```bash
$  help
   ECO help
   INF   help................................

   You are in command-line mode.
   ...
```

### Introduction to the sample data ###
 
Gʀᴏᴏᴛ comes with a sample library, let's get started by seeing what's available:
 
```bash
$   file.sample
    ECO file.sample
    INF seqgen
        sera
        simple
        triptych
```

The _triptych_ sample contains a set genes which have undergone two recombination events "X" and "Y":

```bash
    ALPHA      BETA
      │         │
      └────┬────┘ X
           |
         DELTA         GAMMA
           │             │
           └──────┬──────┘ Y
                  |
               EPSILON
```

The final gene family, _EPSILON_, therefore looks something like this:

```
        __5'[ALPHA][BETA][GAMMA]3'__
```

Let's pretend we don't already know this, and use Gʀᴏᴏᴛ to analyse the triptych.

### Loading the sample ###

The `sample` command can be used to load the sample files automatically, but for sake of this tutorial, we will load the data manually.

Unless you can remember where you installed the files to earlier, you can find out where the sample is located by executing the following command:

```bash
$   sample triptych +view
    ECO sample name=triptych view=True
    INF import_directory "/blah/blah/blah/triptych"
```

The `+view` bit tells Gʀᴏᴏᴛ not to actually load the data, so we can do it ourselves. The _import_directory_ bit of the output tells us where the sample lives. Your path will look different to mine.

You can now load the files into Gʀᴏᴏᴛ:

```bash
$   import.blast /blah/blah/blah/triptych/triptych.blast
$   import.fasta /blah/blah/blah/triptych/triptych.fasta 
```

You should notice that at this point the prompt changes from _Empty model_ to _Unsaved model_.

Let's save our model with a better name:

```bash
$   save tri
    ECO file.save file_name=tri
    PRG  │ file_save...
    PRG  │ -Saving file...
    INF Saved model: /Users/martinrusilowicz/.intermake-data/groot/sessions/tri.groot
```

We didn't specify a path, or an extension, so you'll notice Gʀᴏᴏᴛ has added them for us.

Preparing your data
-------------------

Gʀᴏᴏᴛ follows a pretty-much linear workflow, execute the following command to find out where we're at:

```bash
$   status
    ECO print.status
    INF tri
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
```

It should be clear what we have to do next:

```bash
$   make.components
    ECO make.components
    PRG  │ make_components                                                                  │                                          │                         │ +00:00      ⏎
    PRG  │ -Component detection                                                             │ DONE                                     │                         │ +00:00      ⏎
    WRN There are components with just one sequence in them. Maybe you meant to use a tolerance higher than 0?
```

While not always the case, here we can see Gʀᴏᴏᴛ has identified a problem.
We can confirm this manually:

```bash
$   print.components
    ECO print.components
    INF ┌─────────────────────────────────────────────────────────────────────────┐
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
```

Our components are messed up; Gʀᴏᴏᴛ has found 16 components, which is excessive, and many of these only contain one sequence. We can use a higher tolerance on the `make.components` to allow some differences between the similarity regions identified by Bʟᴀꜱᴛ. The default of zero will almost always be too low. Try the command again, but specify a higher tolerance.

```bash
$   make.components tolerance=10
    ECO make.components tolerance=10
    PRG  │ make_components                                                                  │                                          │                         │ +00:00      ⏎
    PRG  │ -Component detection                                                             │ DONE                                     │                         │ +00:00      ⏎
```

No error this time.  let's see what we have:

```bash
$   print.components
    ECO print.components
    INF ┌─────────────────────────────────────────────────────────────────────────┐
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
```

At a glance it looks better.
We can see each of the gene families (`A`, `B`, `C`, `D`, `E`) have been grouped into a component, but when you have arbitrary gene names things won't be so obvious, and that's where the GUI can be helpful.
 
What next? Let's make a basic tree. For this we'll need the alignments.

```bash
$   make.alignments
```

You can checkout your alignments by entering `print.alignments`:

```bash
$   print.alignments
```

Everything looks okay, so invoke the tree-generation:

```bash
$   make.tree
```

Tree generation can take a while, and we probably don't want to do it again, so maker sure to save our model:

The tree-generating step in particular can take a while! Remember to save your model when it's done.

```bash
$   save
    ECO file.save
    PRG  │ file_save
    PRG  │ -Saving file
    INF Saved model: /Users/martinrusilowicz/.intermake-data/groot/sessions/tri.groot
```

When all the trees are generated, we'll want to get a consensus.

```bash
$   make.consensus
```

This finally leaves us in a position to create the NRFG.
Note that the above commands all execute external tools, by default Mᴜꜱᴄʟᴇ, Rᴀxᴍʟ and Pᴀᴜᴩ respectively, although these can be changed.



Creating the NRFG
-----------------

TODO

Program architecture
--------------------

Gʀᴏᴏᴛ uses a simple MVC architecture:
* The model:
    * The dynamic model (`lego_model.py`):
        * Sequences
        * Edges
            * Subsequences
        * Components
            * Subsequences
    * The static model:
        * Algorithms (`algorithms/`)
* The abstract view (`gui_view.py`):
    * Sequence views
        * Subsequence views
    * Edge views
    * Component views
    * Algorithm views
* The concrete views:
    * The CLI (Iɴᴛᴇʀᴍᴀᴋᴇ: `command_line.py`)
    * The GUI (`frm_main.py`)
* The controller:
    * Controller superclass (Iɴᴛᴇʀᴍᴀᴋᴇ: `environment.py`)
    * Controller subclass (`extensions/`)
    

Troubleshooting
---------------

Please see the [Iɴᴛᴇʀᴍᴀᴋᴇ](https://www.bitbucket.org/mjr129/intermake) troubleshooting section.

Image copyrights
----------------

Freepik

Installation from source
------------------------

You will need to clone the following repositories using Git:

```bash
git clone https://www.bitbucket.org/mjr129/intermake.git
git clone https://www.bitbucket.org/mjr129/mhelper.git
git clone https://www.bitbucket.org/mjr129/editorium.git
git clone https://www.bitbucket.org/mjr129/stringcoercion.git
git clone https://www.bitbucket.org/mjr129/groot.git
```

_...or, if not using Git, download the source directly from Bitbucket, e.g. https://www.bitbucket.org/mjr129/intermake_

Install the root of each repository in development mode via:

```bash
pip install -e .
```

_...or, if not using Pip, add the repository root to your `PYTHONPATH` environment variable._

You will also need to download and install the `requirements.txt` listed in each repository:

```bash
pip install -r requirements.txt 
```

_...or, if not using Pip, check the `requirements.txt` file and download and install the packages from their respective authors manually._

For convenience, you can create an alias for Gʀᴏᴏᴛ by adding the following to your `~/.bash_profile` on Uɴɪx:

```bash
$   alias groot="python -m groot"
```

_...or, for Wɪɴᴅᴏᴡꜱ, create an executable `.bat` file on your Desktop:_

```bash
$   python -m groot %*
```

You should then be able to run the projects as normal.

Meta-data
---------

```ini
language= python3
author= martin rusilowicz
date= 2017
keywords= blast, genomics, genome, gene, nrgf, graphs, intermake
host= bitbucket
type=application,application-gui,application-cli
```
