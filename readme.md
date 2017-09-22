GROOT
=====
From a genomic BLAST to an n-rooted fusion graph

![Screen Shot 2017-01-19 at 12.16.08.png](https://bitbucket.org/repo/BLKbyp/images/3678596765-Screen%20Shot%202017-01-19%20at%2012.16.08.png)


Simple tutorial
---------------
We'll deal with this example using the command line interface, because it's much easier to explain.
When it comes to your own projects, the GUI has the same commands, but provides a much easier way to visually check everything is going smoothly.

Start GROOT.

```
$ python3 -m groot
```

Find out where the example is located

```
$ file.sample triptych +view
```

This will give you the path to the example files (`/blah/blah/blah`), load them manually:
```
$ import.blast /blah/blah/blah/triptych.blast
$ import.fasta /blah/blah/blah/triptych.fasta 
```

Be safe, save our model, call it `tri`

```
$ file.save tri
```

What do we need to do?

```
$ print.status
```

Should be clear.

```
$ make.components
```

This printed an error telling you that you have odd results. You can confirm this manually:

```
$ print.components
```

So try again

```
$ make.components tolerance=10
$ print.components
```

Should be much better. What next? Let's make a basic tree.

```
make.alignments
make.tree
```

We need a consensus tree too, so make one of those.

```
make.consensus
```

Now we can begin the NRFG steps.

```
print.fusions
```

It looks good.




* file -> new
    
Now import our Composite finder result

* file -> import
* change filetype to composites
* load `example.composites`

You'll see the composite gene.

* click the composite gene

You'll see a big red "X" over the sequence. That's because it hasn't got any sequence data - composite finder doesn't output the sequence data, so we'll have to load that too.
 
* file -> import
* change filetype to FASTA
* load `example.fasta`

Select your gene again.

* deselect the gene by clicking some white space
* click your composite gene again
This time you should see the sequence data.
We're still missing something though, composite finder only stores average alignments, the true alignments are still in our BLAST. Load that too.
 
* file -> import
* change filetype to BLAST
* load `example.blast`

Finally we're getting somewhere.
Our gene is a still a bit messy due to slight differences in start/end positions.
Let's clean things up:

* model -> compartmentalise

It should look a lot better now.
Let's generate a tree.
We have two components in our example, they'll be named `alpha` and `beta`.
Generate a tree for each one.

* model -> generate tree -> alpha -> ok
* model -> generate tree -> beta -> ok

Generating the trees may take some time.
Lets's take a look

* component
* click one of the alpha (red) sequences
* 'Data' window -> 'Newick'

You should see the tree in Newick format in the left window.
Let's produce an image from that.

* model -> fuse trees

The n-rooted fusion graph of the trees should appear.

This is the end of the example.

Image copyrights
----------------

Freepik
