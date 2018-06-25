Groot
=====

Gʀᴏᴏᴛ uses genomic data to produce an [N-Rooted Fusion Graph](https://doi.org/10.1093/molbev/mst228).

```text
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

[](toc)


Installation
------------

### Prerequisites ###
Groot runs under Python 3.6 and should be installed using Pip.
* In addition to Python, you will also need some phylogenetic tools to conduct the actual analysis.
* Please download the the following, install, **and confirm that they work** from the command line before continuing to install Groot.

| Tool      | Purpose                | URL                                              |
|-----------|------------------------|--------------------------------------------------|
| Blast     | gene similarity        | https://blast.ncbi.nlm.nih.gov/Blast.cgi         |
| Clann     | supertree inference    | http://mcinerneylab.com/software/clann/          |
| Muscle    | gene alignment         | https://www.ebi.ac.uk/Tools/msa/muscle/          |
| Paup      | phylogeny inference    | http://phylosolutions.com/paup-test/             |
| Pip       | installation manager   | https://pip.pypa.io/en/stable/installing/        |
| Python    | interpreter            | https://www.python.org/downloads/                |
| Raxml     | phylogeny inference    | https://sco.h-its.org/exelixis/software.html     |

Note: You can substitute all of these for your own preferred tools, or specify the data manually, but this list comprises a good "starter pack". 

_Warning: For legacy reasons, MacOS and some Linux flavours come with an older version of Python 2.4 pre-installed, which was last updated in 2006. This isn't enough - you'll still need to install Python 3.6 to use Groot__

### System requirements ###

Groot isn't very fussy, it will even work from your Android phone, but if you want to use the GUI you'll need to be using a supported OS and desktop (Windows, Mac and Ubuntu+Kde or Ubuntu+Gnome are all good).

### Installing Groot ###

When all is ready, download Gʀᴏᴏᴛ using Pip, i.e. from the Windows Console...

```bash
$   pip install groot
```

...or, from a Bash terminal...

```bash
$   sudo pip install groot
```

After the install completes, test that you can actually run Groot:

```bash
$   groot
```

If Groot fails to start see the troubleshooting section on [Groot not found](#groot-not-found). 


### Starting and stopping Groot ###

You should be able to start Gʀᴏᴏᴛ in its _Command Line Interactive_ (CLI) mode straight from the command line:

```bash
$   groot
```

_...You can start Groot in _Graphical User Interface_ (GUI) mode by passing the `gui` argument:_

```bash
$   groot gui
```

You can also use Gʀᴏᴏᴛ in your own Python applications:

```python
$   import groot
```

Or use Python's own interactive prompt (PYI):

```python
$   groot pyi
```

To exit Groot's command line (CLI), press `CTRL+C`,  or use the exit command:

```bash
$   exit
```

To exit Python (PYI) you'll need to add brackets:

```python
$   exit()
```

To exit the GUI, you can just close the window :)

For advanced functionality, please see the [Iɴᴛᴇʀᴍᴀᴋᴇ documentation](https://bitbucket.org/mjr129/intermake).

Tutorial
--------

### Getting started ###

Groot has a nice GUI wizard that will guide you through, but for this tutorial, we'll be using the CLI.
It's much easier to explain and we'll get to cover all the specific details.
The workflow we'll be following looks like this:

0. Load FASTA data
0. Make similarity matrix
0. Make major components
0. Make minor components
0. Make alignments
0. Make trees
0. Make fusions
0. Candidate splits
0. Viable splits
0. Subsets
0. Pregraphs
0. Subgraphs
0. Fuse
0. Clean
0. Check

_Note: The technical details of this workflow are already covered in the complementary [paper]() and we won't be repeat these in the tutorial - we'll only be discussing how to perform it._

We'll assume you have Gʀᴏᴏᴛ installed and working as above, so start Gʀᴏᴏᴛ in CLI mode (if it isn't already):

```bash
$   groot
    >>> Empty model>
```

Groot's CLI has a simple interface. Once Gʀᴏᴏᴛ has started, just type `help` for help.

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

As an aside, there are also `import.` commands, which can be used in lieu of the `create.` commands to import data which is already known, and `file.` commands used to load and save the model.

Type `cmdlist` to see all the commands now.

### Introduction to the sample data ###

Gʀᴏᴏᴛ comes with a convenient sample library, get started by seeing what's available:
 
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

```text
        __5'[ALPHA][BETA][GAMMA]3'__
```

Let's pretend we don't already know this, and use Gʀᴏᴏᴛ to analyse the triptych.

### Loading the sample ###

The `file.sample` command can be used to load the sample files automatically, but for the sake of providing a tutorial, we will be importing the data manually.
For reference, the ways of getting Groot to do stuff with the minimal possible effort are listed in the table below.

| Mode of operation | What it does            | How to get there         |
|-------------------|-------------------------|--------------------------|
| Wizard            | Does everything for you | Use the `wizard` command |
| GUI               | Shows you things        | Use the `gui` command    |
| Sample loader     | Loads samples           | Use the `sample` command |

Unless you can remember where Pip installed the files to earlier, you can find out where the sample data is located by executing the following command:

```bash
$   file.sample triptych +q
    
#   INF import_directory "/blah/blah/blah/triptych"
```

The `+q` bit of our input tells Gʀᴏᴏᴛ not to actually load the data, so we can do it ourselves.
Groot works out what you mean most of the time, so `+q` is equivalent to `true`, `+query`, `query=true`, `q=1`, etc.
The _import_directory_ bit of the output tells us where the sample lives.
Write that down, and take note, your path will look different to mine!

You can now load the files into Gʀᴏᴏᴛ:

```bash
$   import.blast /blah/blah/blah/triptych/triptych.blast
$   import.fasta /blah/blah/blah/triptych/triptych.fasta 
```

You should notice that at this point the prompt changes from _Empty model_ to _Unsaved model_. Good times.

Unsaved model isn't very informative and serves as a reminder to _save our data_, so save our model with a more interesting name:

```bash
$   save tri
    
#   PRG  │ file_save...
    PRG  │ -Saving file...
    INF Saved model: /Users/martinrusilowicz/.intermake-data/groot/sessions/tri.groot
```

We didn't specify a path, or an extension, so you'll notice Gʀᴏᴏᴛ has added them for us.
Groot uses directory in your home folder to store its data.
The directory is hidden by default to avoid bloating your home folder, but Groot can remind you where it is (or change it!) if you use the `workspace` command. 

Preparing your data
-------------------

The linear workflow presented earlier can be shown in groot by, executing the `status` or `print.status` command:

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

While not always the case, here, we can see Gʀᴏᴏᴛ has identified a problem. Well done Groot.
We can confirm this manually too:

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
Solve the problem by using a higher tolerance on the `make.components` command in order to allow some differences between the BLAST regions.
The default of zero will almost always be too low.
Try the command again, but specify a higher tolerance this time.

```bash
$   make.components tolerance=10
    
#   PRG  │ make_components                                                                  │                                          │                         │ +00:00      ⏎
    PRG  │ -Component detection                                                             │ DONE                                     │                         │ +00:00      ⏎
```

No error this time. let's see what we have:

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
We can see each of the gene families (`A`, `B`, `C`, `D`, `E`) have been grouped into a component.

_Reminder: When you have arbitrary gene names things won't be so obvious, and that's where the GUI can be helpful!_
 
What next? Let's make a basic tree. For this we'll need the alignments.

```bash
$   make.alignments
```

We didn't specify an algorithm so Groot will choose one for us (probably MUSCLE). When complete, you can checkout your alignments by entering `print.alignments`:

```bash
$   print.alignments
```

Everything looks okay, so invoke tree-generation. For the sake of this tutorial, we'll specify a Neighbour Joining tree, so we don't have to sit around all day.

```bash
$   make.tree neighbor.joining
```

In many circumstances tree generation can take a while, and you probably don't want to do it again if something goes wrong, so make sure to save our model:

```bash
$   save

#   PRG  │ file_save
    PRG  │ -Saving file
    INF Saved model: /Users/martinrusilowicz/.intermake-data/groot/sessions/tri.groot
```

This finally leaves us in a position to create the NRFG.


Creating the NRFG
-----------------

We have a tree for each component now, but this isn't a graph, and the information in each tree probably conflicts.

Groot has two methods of resolving this problem.

The first is by splitting and regrowing the tree, the second is by using peer reviewed tools such as CLANN. The first case can be useful in scrutinising your trees, but you almost certainly want to use the latter for your final NRFG.
  
A "split" defines a tree by what appears on the left and right of its edges.
Generate the list of all the possible splits:

```bash
$   create.splits
``` 

And then find out which ones receive majority support in our trees:

```bash
$   create.consensus
```

You can use `print.consensus` to check out your results.

Set the split data aside for the moment and generate the gene "subsets", each subset is a portion of the original trees that is uncontaminated by a fusion event.

```bash
$   create.subsets
```

Now we can combine these subsets with our consensus splits to make subgraphs - graphs of each subset that use only splits supported by our majority consensus. We'll use CLANN for this like we talked about earlier.

```bash
$   create.subgraphs clann
```  

We can then create the NRFG by stitching these subgraphs back together.

```bash
$   create.nrfg
```

Good good.
But the NRFG is not yet complete.
Stitching probably resulted in some trailing ends here and there, we need to trim these.

```bash
$   create.clean
```

Finally, we can check the NRFG for errors.
If we have a graph with which to compare we could specify one here to see how things match up, but in most cases we won't, so just run:  

```bash
$   create.checks
```

And we're all done!

To print out your final graph:

```bash
$   print.tree nrfg.clean cyjs open
```

This says:
* `print.tree` print the tree
* called `nrfg.clean`
* using Cytoscape.JS (`cyjs`)
* and `open` the result using the default browser

You can also use `print.report` to print out your final summary in much the same way.

```
$   print.report final.report open
```

We didn't specify anything to compare to and our graph, being constructed from the sample data, should't have any problems, so our report will be pretty short.

Now you've done the tutorial, try using the GUI - it's a lot easier to check the workflow is progressing smoothly and you can view the trees and reports inline!


Program architecture
--------------------

Gʀᴏᴏᴛ uses a simple MVC-like architecture:

* The model:
    * The dynamic model (`data`):
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
* The controller (`extensions`)
* The view:
    * CLI (Iɴᴛᴇʀᴍᴀᴋᴇ library)
    * GUI (`frontends/gui`)
    
Extending
---------

You can incorporate your own extensions into Groot.

### Creating the modules ###

Algorithms should be written into a Python package or module.

Inside your modules, register Groot algorithms using the `@xyz.register` decorators:
```python
from groot import tree_algorithms

@tree_algorithms.register()
def my_algorithm( . . . )
    . . .
```

The `groot_ex` package contains the default set of algorithms, you can use this as a template for your own.

New Groot commands can also be registered using Intermake.
```python
from intermake import command

@command()
def my_command( . . . ):
    . . .
```

The groot core commands can be found in the main `groot` package, inside the `extensions` subfolder.
See the Intermake documentation for more details.

### Registering the modules ###

Once created, you need to register your package with Groot.
From the BASH command line:

```
groot import my_algorithms +persist
```

This says:
* Start `groot`, `import` the module `my_algorithms` and `+persist` this setting for the next time I start Groot.


Image credits
-------------

Icons by:

* Good Ware
* Freepik
* Maxim Basinski
* Those Icons
* Pixel perfect
* Google
* Smash Icons

Available at [flaticon.com](http://www.flaticon.com).


Installation from source
------------------------

Groot can be cloned using and installed in development mode:

```bash
git clone https://www.bitbucket.org/mjr129/groot.git
cd groot
pip install -e .
```

You will still require the other prerequisites!

Terminology
-----------

List of terms used in Groot. 

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

* Data may be conventional or imputed, concrete or abstract, but Groot doesn't care.

Data formats
------------

Groot endeavours to use one, simple, popular, standard format for each data type.
The following formats are thus used:

* Sequences: FASTA
* Similarities: BLAST format 6 TSV
* Trees: Newick
* Networks: CSV edge table
* Scripts: Python
* Internal data: Pickle

The Groot test suite
--------------------

Groot comes with the ability to generate random test cases.

To create and run tests, use `groot create.test n`, where `n` specifies the test case (denoted by the expected number of components).

All tests trees should be recoverable (mutations permitting) by Groot using the default settings, with the exclusion of the specific instances of test case 4, noted below.

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
 
Troubleshooting
---------------

Troubleshooting and bugs
------------------------

* Please report all bugs on the official bitbucket page at [https://bitbucket.org/mjr129/groot/issues].
* Please also see the [Iɴᴛᴇʀᴍᴀᴋᴇ](https://www.bitbucket.org/mjr129/intermake) documentation for handling technical issues.


### Groot not found ###

If you see the Groot command prompt that's great, it works, but if you get a message like `groot not found` then Python probably doesn't have its PATH configured correctly.
You might be able to start Groot using `python -m groot`, but it's probably best to consult the Python documentation at this time and fix the issue before continuing.

You probably need to add the Python binaries to your path, using a command something like:

```bash
export PATH=$PATH:/opt/local/Library/Frameworks/Python.framework/Versions/3.6/bin
```

Check out [this StackOverflow post](https://stackoverflow.com/questions/35898734/pip-installs-packages-successfully-but-executables-not-found-from-command-line?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa) as a starting point.


### Screen goes black, images or windows disappear ###

Groot has been coded for multiple platforms, however, one or more settings may need changing for your particular platform. 
* In the GUI, go to `Windows` -> `Preferences` and change the following settings:
    * Set the _MDI mode_ to **basic**.
    * Set _OpenGL_ **off**
    * Set _shared contexts_ **off**.
    * Turn the inbuilt browser **off**
* Restart GROOT

### Multi-fusion sources ###

Groot is able to detect and handle the following cases:

* A normal fusion case: `A + B --> F`
* A "lossy fission" or a fusion case where one side is not present in the data `A --> F`

It is currently unable to detect:

* An n-parted fusion, or a multi-fusion case where one or more intermediates are not present in the data, A + B + C --> F

Groot may still be able to deal with this circumstance, providing you guide it in the direction by specifying the fusion event manually.


### The spaceship and the triangle ###

There are a couple of cases that Groot will suffer from.

The first is the spaceship (Figure 1, below) which is a specific variant of Case 4 (above) in which _A1=A2_ and _B1=B2_.
If two fusion events (_C_ and _D_) occur at the same time, this isn't distinguishable from the normal case of one fusion event (_X_) that later diverges into two lineages (_C_ and _D_) (Figure 2).
However, if you know (or wish to pretend) that this is the case, you can specify the Groot components manually, rather than letting Groot infer them.

The second problematic case is the triangle (Figure 3), which is also a specific variant of Case 4 in which _A1=A2_ and _B1≠B2_.
This scenario _initially_ looks like the spaceship (Figure 1).
However, things become apparent once Groot runs down to the NRFG stage, since the fusion will be malformed (Figure 4), with 3 origins, one output (_CD_) but only 2 input components (_A_, _B_).
At the present time, Groot doesn't remedy this situation automatically and you'll need to rectify the problem yourself.
From your Figure-4-like result, write down or export the sequences in each of your lineages _A_, _B_, _C_ and _D_.
Then, go back to the component stage and specify your components manually: _A_, _B_, _C_ and _D_.

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
date        = 2017,2018
keywords    = blast, genomics, genome, gene, nrgf, graphs, intermake
host        = bitbucket,git,mcinerneylab-git,pypi
type        = application,application-gui,application-cli
```
