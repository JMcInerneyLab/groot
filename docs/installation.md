Groot Installation
==================

Prerequisites
-------------

Groot runs under Python 3.6+ and should be installed using Pip.

* In addition to Python, you will also need some phylogenetic tools to conduct the actual analysis.
* Please download the the following, install, **and confirm that they work** from the command line before continuing to install Groot.

| Tool      | Purpose                | URL                                              |
|-----------|------------------------|--------------------------------------------------|
| Blast     | Gene similarity        | https://blast.ncbi.nlm.nih.gov/Blast.cgi         |
| Clann     | Supertree inference    | http://mcinerneylab.com/software/clann/          |
| Muscle    | Gene alignment         | https://www.ebi.ac.uk/Tools/msa/muscle/          |
| Paup      | Phylogeny inference    | http://phylosolutions.com/paup-test/             |
| Pip       | Installation manager   | https://pip.pypa.io/en/stable/installing/        |
| Python    | Interpreter            | https://www.python.org/downloads/                |
| Raxml     | Phylogeny inference    | https://sco.h-its.org/exelixis/software.html     |

Note: You can substitute all of these for your own preferred tools, or specify the data manually, but this list comprises a good "starter pack".

**Make sure to place your binaries in your system `PATH` so that they can be accessed by Groot.**


_Warning: For legacy reasons, MacOS and some Linux flavours come with an older version of Python 2.4 pre-installed, which was last updated in 2006. This isn't enough - you'll need to install Python 3.6 to use Groot__

System requirements
-------------------

Groot isn't very fussy, it will work from your Android phone, but if you want to use the GUI you'll need to be using a supported OS and desktop (Windows, Mac and Ubuntu+Kde or Ubuntu+Gnome are all good).


Installing Groot Using Pip
--------------------------

When all is ready, download Gʀᴏᴏᴛ using Pip, i.e. from the Windows Console...

```bash
$   pip install groot
```

...or, from a Bash terminal...

```bash
$   sudo pip install groot
```

If you don't have administrator access, you can use `virtualenv`:

```bash
[bash]$         virtualenv grootling
[bash]$         source grootling/bin/activate
[grootling]$    pip install groot
```

After the install completes, test that you can actually run Groot:

```bash
$   groot
```

If Groot fails to start then your `PATH` is incorrectly configured.
Use `python -m groot` instead, or see the [troubleshooting section on Groot not found](troubleshooting#groot-not-found). 


Starting and stopping Groot
---------------------------

You should be able to start Gʀᴏᴏᴛ in its _Command Line Interactive_ (CLI) mode straight from the command line:

```bash
$   groot
```

Groot operates in a number of UI modes, CLI mode is a scripted mode that acts like passing arguments from the command line,
for instance the following two scripts are the same:

```bash
[bash]$    groot
[groot]$   echo "hello world"
[groot]$   exit
```

```bash
[bash]$   groot echo "hello world"
```

Perhaps more intuitively, you can tell Groot to use Python instead:

```python
[bash]$             groot pyi
[python-groot]$     echo("hello world")
[python-groot]$     exit()
```

You can start Groot in _Graphical User Interface_ (GUI) mode by passing the `gui` argument:

```bash
$   groot gui
```

Finally, you can also use Gʀᴏᴏᴛ in your own applications via the python `import` command:

```python
$   import groot
```

For advanced functionality, see the [Iɴᴛᴇʀᴍᴀᴋᴇ documentation](https://bitbucket.org/mjr129/intermake).

Installation from source code
-----------------------------

Groot can be cloned using and installed in development mode by cloning the git repository.
Some technical knowledge is required.
If you are in doubt, use `pip` as described above.

```bash
git clone https://www.bitbucket.org/mjr129/groot.git
cd groot
pip install -e .
```

You will still require the other prerequisites!
