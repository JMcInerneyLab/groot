Groot
=====
Gʀᴏᴏᴛ imports Bʟᴀꜱᴛ data and produces a genomic [N-Rooted Fusion Graph](https://doi.org/10.1093/molbev/mst228).

Gʀᴏᴏᴛ:
* Is accessible. Gʀᴏᴏᴛ has **command line, friendly GUI and Python library** capabilities.
* Is understandable. Gʀᴏᴏᴛ follows a simple MVC architecture with **heavily documented source code**.
* **Is free**. Users are invited to call upon the library or modify the source code to suit their own needs.


[](toc)

Installation
------------

Please make sure you have Python (3.6+) and Pɪᴩ installed first!
If you'd like to visualise trees please download vis.js also.

* Python: https://www.python.org/downloads/
* Pip: https://pip.pypa.io/en/stable/installing/


Then download Gʀᴏᴏᴛ using Pip, i.e. from Bᴀꜱʜ:

```bash
$   sudo pip install groot
```

You should then be able to start Gʀᴏᴏᴛ in its _Command Line Interactive_ (CLI) mode:

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

For advanced functionality, please see the [Iɴᴛᴇʀᴍᴀᴋᴇ documentation](https://bitbucket.org/mjr129/intermake).

_**If the `groot` command does not start Gʀᴏᴏᴛ then you have not got Pʏᴛʜᴏɴ set up correctly**_

Tutorial
--------

### Getting started ###

Groot has a nice GUI wizard that will guide you through, but for this tutorial, we'll be using the CLI.
It's much easier to explain and we get to cover all the specific details.
The workflow we'll be following looks like this:

0. Load FASTA data       
0. Load BLAST data       
0. Make components
0. Make alignments       
0. Make trees            
0. Make fusions          
0. Candidate splits  
0. Viable splits     
0. Subsets               
0. Subgraphs             
0. Stitch                
0. Clean                 
0. Check

We'll assume you have Gʀᴏᴏᴛ installed and working, so start Gʀᴏᴏᴛ in CLI mode (if it isn't already):

```bash
$   groot
    >>> Empty model>
```

Once in Gʀᴏᴏᴛ, type `help` for help.

```bash
$  help
   
#  INF   help................................

   You are in command-line mode.
   ...
```

There are three groups of workflow commands in Groot, the `make.` commands, used to advance the workflow, the `drop.` commands, used to go back a step, and the `print.` commands, used to display information. For instance, to create the NRFG it's `make.nrfg`, to view it it's `print.nrfg`, and to delete it and go back a step, it's `drop.nrfg`. Type `cmdlist` to see all the commands.

### Introduction to the sample data ###
 
Gʀᴏᴏᴛ comes with a sample library, get started by seeing what's available:
 
```bash
$   file.sample
    
    INF seqgen
        sera
        simple
        triptych
```

The _triptych_ sample contains a set of genes which have undergone two recombination events "X" and "Y":

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

The `sample` command can be used to load the sample files automatically, but for the sake of providing a tutorial, we will load the data manually.

Unless you can remember where Pip installed the files to earlier, you can find out where the sample is located by executing the following command:

```bash
$   sample triptych +query
    
#   INF import_directory "/blah/blah/blah/triptych"
```

The `+query` bit tells Gʀᴏᴏᴛ not to actually load the data, so we can do it ourselves.
The _import_directory_ bit of the output tells us where the sample lives.
Write that down.
Remember, your path will look different to mine.

You can now load the files into Gʀᴏᴏᴛ:

```bash
$   import.blast /blah/blah/blah/triptych/triptych.blast
$   import.fasta /blah/blah/blah/triptych/triptych.fasta 
```

You should notice that at this point the prompt changes from _Empty model_ to _Unsaved model_.

Unsaved model isn't very informative, so save our model with a more interesting name:

```bash
$   save tri
    
#   PRG  │ file_save...
    PRG  │ -Saving file...
    INF Saved model: /Users/martinrusilowicz/.intermake-data/groot/sessions/tri.groot
```

We didn't specify a path, or an extension, so you'll notice Gʀᴏᴏᴛ has added them for us.

Preparing your data
-------------------

Gʀᴏᴏᴛ follows a linear workflow, execute the `status` command to find out where we're at:

```bash
$   status
    
#   INF tri
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
```

It should be clear what we have to do next:

```bash
$   make.components
    
#   PRG  │ make_components                                                                  │                                          │                         │ +00:00      ⏎
    PRG  │ -Component detection                                                             │ DONE                                     │                         │ +00:00      ⏎
    WRN There are components with just one sequence in them. Maybe you meant to use a tolerance higher than 0?
```

While not always the case, here, we can see Gʀᴏᴏᴛ has identified a problem.
We can confirm this manually:

```bash
$   print.components
    
#   INF ┌─────────────────────────────────────────────────────────────────────────┐
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

Our components are messed up; Gʀᴏᴏᴛ has found 16 components, which is excessive, and many of these only contain one sequence.
Solve the problem by using a higher tolerance on the `make.components` to allow some differences between the BLAST regions.
The default of zero will almost always be too low.
Try the command again, but specify a higher tolerance.

```bash
$   make.components tolerance=10
    
#   PRG  │ make_components                                                                  │                                          │                         │ +00:00      ⏎
    PRG  │ -Component detection                                                             │ DONE                                     │                         │ +00:00      ⏎
```

No error this time.  let's see what we have:

```bash
$   print.components
    
#   INF ┌─────────────────────────────────────────────────────────────────────────┐
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

Everything looks okay, so invoke tree-generation:

```bash
$   make.tree
```

Tree generation can take a while, and we probably don't want to do it again, so maker sure to save our model:

```bash
$   save

#   ECO file.save
    PRG  │ file_save
    PRG  │ -Saving file
    INF Saved model: /Users/martinrusilowicz/.intermake-data/groot/sessions/tri.groot
```

When all the trees are generated, we'll want to get a consensus.
Groot uses its own internal consensus generator.
We can zoom to the NRFG by using the `create.nrfg` command,  

```bash
$   make.consensus
```

This finally leaves us in a position to create the NRFG.

Note that the above commands all execute external tools, by default Mᴜꜱᴄʟᴇ, Rᴀxᴍʟ and Pᴀᴜᴩ respectively, although all of these can be changed.

Creating the NRFG
-----------------

We have a tree for each component now, but this isn't a graph, and the information in each tree probably conflicts.
We can use "splits" to resolve the conflicts.
A "split" defines a tree by what appears on the left and right of its edges.
This provides a quick and easy method of generating a consensus between our trees.
Generate the list of all the possible splits:

```bash
$   make.splits
``` 

And then find out which ones receive majority support in our trees:

```bash
$   make.consensus
```

We set the split data aside for the moment and generate the gene "subsets", each subset is a portion of the original trees that is uncontaminated by a fusion event.

```bash
$   make.subsets
```

Now we can combine these subsets with our consensus splits to make subgraphs - graphs of each subset that use only splits supported by our majority consensus.

```bash
$   make.subgraphs
```  

We can then create the NRFG by stitching these subgraphs back together.

```bash
$   make.nrfg
```

Good times. But the NRFG is not yet complete. Stitching probably resulted in some trailing ends, we need to trim these.

```bash
$   make.clean
```

Finally, we can check the NRFG for errors.

```bash
$   make.checks
```

And we're all done!

Now you've done the tutorial, try using the GUI - it's a lot easier to check the workflow is progressing smoothly and view large trees.


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

Image credits
-------------

Freepik
Smashicons
Google

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

Terminology
-----------

List of terms used in Groot. 
Legacy terms and aliases are listed on the right because some of these are still used in the Groot source code (if not shown to the user in the program).

| Term         | Description                                                                                   | Legacy name(s)
|--------------|-----------------------------------------------------------------------------------------------|--------------------
| Fusion event | An event in the evolution in which 2 genes join                                               | Event
| Fusion point | The realisation of a fusion event within an individual tree                                   | Point
| Splits       | The set of edges found within all trees                                                       | Candidate splits
| Consensus    | A subset of splits supported by the majority-rule consensus                                   | Consensus splits, viable splits
| NRFG         | The N-rooted fusion graph                                                                     | Stitched graph, sewed graph, fusion graph
| Genes        | The input genes or sequences                                                                  | Sequences
| Domains      | Part of a gene (conventional or imputed, Groot doesn't care)                                  | Subsequences
| Sites        | The site data for the genes (FASTA)                                                           | FASTA data
| Edges        | How the genes are connected (BLAST)                                                           | BLAST data
| Subgraphs    | Stage of NRFG creation representing a part of the evolution free of fusions                   | Minigraphs
| Subsets      | The predecessors to the subgraphs - a set of genes free of fusion events                      | Gene subsets
| Split        | An edge of a tree represented as the left and right leaf-sets                                 | Edge (of a tree)

Meta-data
---------

```ini
language    = python3
author      = martin rusilowicz
date        = 2017
keywords    = blast, genomics, genome, gene, nrgf, graphs, intermake
host        = bitbucket
type        = application,application-gui,application-cli
```
