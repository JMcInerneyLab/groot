Troubleshooting Groot
=====================

* Please report all bugs on the official bitbucket page at [https://bitbucket.org/mjr129/groot/issues].
* Please also see the [Iɴᴛᴇʀᴍᴀᴋᴇ](https://www.bitbucket.org/mjr129/intermake) documentation for handling technical issues.


Groot not found
---------------

If you see the Groot command prompt that's great, it works, but if you get a message like `groot not found` then Python probably doesn't have its PATH configured correctly.
You might be able to start Groot using `python -m groot`, but it's probably best to consult the Python documentation at this time and fix the issue before continuing.

You probably need to add the Python binaries to your path, using a command something like:

```bash
export PATH=$PATH:/opt/local/Library/Frameworks/Python.framework/Versions/3.6/bin
```

Check out [this StackOverflow post](https://stackoverflow.com/questions/35898734/pip-installs-packages-successfully-but-executables-not-found-from-command-line?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa) as a starting point.


Screen goes black, images or windows disappear
----------------------------------------------

Groot has been coded for multiple platforms, however, one or more settings may need changing for your particular platform. 
* In the GUI, go to `Windows` -> `Preferences` and change the following settings:
    * Set the _MDI mode_ to **basic**.
    * Set _OpenGL_ **off**
    * Set _shared contexts_ **off**.
    * Turn the inbuilt browser **off**
* Restart GROOT

Obtaining binaries
------------------

Binaries are not available, installation [using Pip](#using-pip) is the recommended method.
For deployment on systems without an internet connection, you can create your own binaries using [PyInstaller](https://www.pyinstaller.org/).

```bash
$   cd groot
$   pyinstaller groot/__main__.py
```

Issues with Paup
----------------

> Until the official release of version 5.0 of PAUP*, you can download time-expiring test versions of PAUP* here
>
> http://phylosolutions.com/paup-test

There are some major issues in using the Paup test versions of Paup from Groot:

* Paup is being updated: changes to Paup's API frequently break Groot's interface to it.
* Paup has programmed obsolescence: Groot cannot link to a known, working version of Paup. 
* Paup does not report obsolescence errors in its return code: Groot cannot know whether your version is up to date.

If you are using a test version of Paup then please make sure it is up to date.
If this still doesn't work, submit Groot interface bugs on the Bitbucket web page.
Until these issues are resolved with Paup, consider using a different phylogeny tool such as [Raxml](https://sco.h-its.org/exelixis/software.html).


Multi-fusion sources
--------------------

Groot is able to detect and handle the following cases:

* A normal fusion case: `A + B --> F`
* A "lossy fission" or a fusion case where one side is not present in the data `A --> F`

It is currently unable to detect:

* An n-parted fusion, or a multi-fusion case where one or more intermediates are not present in the data, A + B + C --> F

Groot may still be able to deal with this circumstance, providing you guide it in the direction by specifying the fusion event manually.


The spaceship and the triangle
------------------------------

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