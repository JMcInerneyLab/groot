Groot
=====
Gʀᴏᴏᴛ imports Bʟᴀꜱᴛ data and produces a genomic [N-Rooted Fusion Graph](https://doi.org/10.1093/molbev/mst228).

```
\         /       /
 A       B       C       <-Roots
  \     /       /
   \   /       /
    \ /       /
     AB      /           <-Fusion product
      \     /
       \   /
        \ /
        ABC              <-Fusion product
          \
```

Gʀᴏᴏᴛ aims to be

* Accessible. Gʀᴏᴏᴛ has **command line, friendly GUI and Python library** capabilities.
* Understandable. Gʀᴏᴏᴛ follows a simple workflow with MVC architecture and **heavily documented source code**.
* Free. Users are invited to call upon the library or modify the source code to suit their own needs.

[](toc)

Installation
------------

Please make sure you have Python (3.6+) and Pɪᴩ installed first!

* Python: https://www.python.org/downloads/
* Pip: https://pip.pypa.io/en/stable/installing/

_Warning: MacOS and some Linux flavours come with an older version of Python 2.4 pre-installed, you'll need to install Python 3.6 for Groot__   


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
It's much easier to explain and we get to cover all the specifics.
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
0. Fuse                  
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
   
   INF   help................................

   You are in command-line mode.
   ...
```

There are three groups of workflow commands in Groot.
The `create.` commands are used to advance the workflow,
the `drop.` commands are used to go back a step,
and the `print.` commands are used to display information.
For instance, to create the alignments it's `create.alignments`,
to view them it's `print.alignments`, and to delete them and go back a step, it's `drop.alignments`.
Type `cmdlist` to see all the commands.

### Introduction to the sample data ###
 
Gʀᴏᴏᴛ comes with a sample library, get started by seeing what's available:
 
```bash
$   file.sample
    
    INF seqgen
        sera
        simple
        triptych
```

_Note: The samples available will vary depending on which version of Groot you are using._

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

The `sample` command can be used to load the sample files automatically, but for the sake of providing a tutorial, we will be importing the data manually.
For reference, the ways of getting Groot to do stuff with the minimal possible effort are listed in the table below.

| Mode of operation | What it does            | How to get there         |
|-------------------|-------------------------|--------------------------|
| Wizard            | Does everything for you | Use the `wizard` command |
| GUI               | Shows you things        | Use the `gui` command    |
| Sample loader     | Loads samples           | Use the `sample` command |

Unless you can remember where Pip installed the files to earlier, you can find out where the sample is located by executing the following:

```bash
$   sample triptych +q
    
#   INF import_directory "/blah/blah/blah/triptych"
```

The `+q` bit of our input tells Gʀᴏᴏᴛ not to actually load the data, so we can do it ourselves.
Groot works out what you mean most of the time, so `+q` is equivalent to `true`, `+query`, `query=true`, `q=1`, etc.
The _import_directory_ bit of the output tells us where the sample lives.
Write that down, and take note, your path will look different to mine.

You can now load the files into Gʀᴏᴏᴛ:

```bash
$   import.blast /blah/blah/blah/triptych/triptych.blast
$   import.fasta /blah/blah/blah/triptych/triptych.fasta 
```

You should notice that at this point the prompt changes from _Empty model_ to _Unsaved model_.

Unsaved model isn't very informative and serves as a reminder to _save our data_, so save our model with a more interesting name:

```bash
$   save tri
    
#   PRG  │ file_save...
    PRG  │ -Saving file...
    INF Saved model: /Users/martinrusilowicz/.intermake-data/groot/sessions/tri.groot
```

We didn't specify a path, or an extension, so you'll notice Gʀᴏᴏᴛ has added them for us.
Groot uses directory in your home folder to store its data.
The directory is hidden by default to avoid bloating your home folder, but you can find out where it is (or change it!) using the `workspace` command. 

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

Now you've done the tutorial, try using the GUI - it's a lot easier to check the workflow is progressing smoothly and you can view the trees properly!


Program architecture
--------------------

Gʀᴏᴏᴛ uses a simple MVC-like architecture:

* The model:
    * The dynamic model (`data/lego_model.py`):
        * Sequences
        * Subsequences
        * Edges
        * Components
        * etc. 
    * The static model (`algorithms/`):
        * Tree algorithms
        * Alignment algorithms
        * Supertree algorithms
        * etc. 
* The controller (`extensions/`)
* The views (`extensions`):
    * CLI (Iɴᴛᴇʀᴍᴀᴋᴇ: `command_line.py`)
    * GUI (`frontends/gui/frm_main.py`)
    
Extending
---------

You can incorporate your own extensions into Groot.

### Algorithms

To register algorithms use:
```python
@tree_algorithms.register()
def my_algorithm( . . . )
    . . .
```

The `groot_ex` package contains the default set of algorithms, you can use this as a template for your own.


### Commands

To register new Groot commands.
```python
@command()
def my_command( . . . ):
    . . .
```


The groot core commands can be found in the main `groot` package, under the `extensions` subfolder.
See the Intermake documentation for more details.

### Registering

To add your own algorithm package to groot use the `import` command, e.g. from the CLI:

```
import my_algorithms +persist
```

You can also call this statement from Python, allowing your package to register itself with Groot.
    

Troubleshooting
---------------

***Please see the [Iɴᴛᴇʀᴍᴀᴋᴇ](https://www.bitbucket.org/mjr129/intermake) troubleshooting section***

### Screen goes black, images or windows disappear ###

Go to `Windows` -> `Preferences` -> `View` and turn the MDI mode to `basic`.


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

| Term          | Description                                                                                   |
|---------------|-----------------------------------------------------------------------------------------------|
| Fusion event  | An event in the evolution in which 2 genes join                                               |
| Fusion point  | The realisation of a fusion event within an individual tree                                   |
| Splits        | The set of edges found within all trees                                                       |
| Consensus     | A subset of splits supported by the majority-rule consensus                                   |
| NRFG          | The N-rooted fusion graph                                                                     | 
| Fused graph   | The N-rooted fusion graph without redundancies removed                                        |
| Cleaned graph | The N-rooted fusion graph with redundancies removed                                           |
| Genes         | The input sequences*                                                                          |
| Domains       | Part of a gene*                                                                               |
| Sites         | The site data for the genes (FASTA)                                                           |
| Edges         | How the genes are connected (BLAST)                                                           |
| Subgraphs     | Stage of NRFG creation representing a part of the evolution free of fusions                   |
| Subsets       | The predecessors to the subgraphs - a set of genes free of fusion events                      |
| Split         | An edge of a tree represented as the left and right leaf-sets                                 |

* Data may be conventional or imputed, concrete or abstract, Groot doesn't care.

Data formats
------------

Groot endeavours to use one, simple, popular, standard format for each data type.
The following formats are supported:

* Sequences: FASTA
* Similarities: BLAST format 6 TSV
* Trees: Newick
* Networks: CSV
* Scripts: Python
* Internal data: Pickle

The Groot test suite
--------------------

Groot comes with the ability to generate random test cases.
To create and run them, use `groot create.test n`, where `n` specifies the test case (denoted by the expected number of components).
All tests trees should be recoverable by Groot using the default settings, with the exclusion of the specific instances of test case 4, noted below.

### Case 1: Single fusion ###
```
 A-------->
  \     a0
   \a1
    \
     -->C--->
    /
   /b1
  /     b0
 B-------->
```

### Case 4: Repeated fusions ###
```
 A------------------->
  \       \       a0
   \a1     \a2
    \       \
     -->C    -->D
    /       /
   /a2     /b2
  /       /       b0
 B------------------->
```

As the test cases are randomly generated, this may result in _a1=a2_ and/or _b1=b2_, giving the _triangle_ or _spaceship_ problems listed below. 

### Case 5: Fusion cascade ###

```
 A
  \
   -->C
  /    \
 B      -->E
       /
      D
```

### Case 7: Fusion web ###

```
 A
  \
   -->C
  /    \
 B      \
         -->G
 D      /
  \    /
   -->F
  /
 E
```
 

Handling the spaceship and the triangle
--------------------------------------

There are a couple of cases that Groot will suffer from.

The first is the spaceship (Figure 1, below) which is a specific variant of Case 4 (above) in which A1=A2 and B1=B2.
If two fusion events (C and D) occur at the same time, this isn't distinguishable from the normal case of one fusion event (X) that later diverges into two lineages (C and D) (Figure 2).
However, if you know (or wish to pretend) that this is the case, you should specify the Groot components manually, rather than letting Groot infer them.

The second problematic case is the triangle (Figure 3), which is also a specific variant of Case 4 in which A1=A2 and B1≠B2.
This scenario _initially_ looks like the spaceship (Figure 1).
However, things become apparent once Groot runs down to the NRFG stage, since the fusion will be malformed (Figure 4), with 3 origins, one output ("CD") but only 2 input components (A, B).
At the present time, Groot doesn't remedy this situation automatically and you'll need to rectify the problem yourself.
From your Figure-4-like result, write down or export the sequences in each of your lineages A, B, C and D.
Then, go back to the component stage and specify your components manually: A, B, C and D.

```
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
```
_NB. Figures require a utf8 compliant browser_


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
