Seven Families
==============

FakeTree generated sequences for use as a Groot sample dataset.

Represents a 4-rooted fusion graph with three fusion events and one product family.

Sequences:

* Are DNA.
* Use a monatonic mutation rate of 10% per site, per branch.
* Have a ancestor sequence of 250 sites long.
* Employ no insertion/deletion operations.

The BLAST output is real and is taken from `blastn -subject seven.fasta -query seven.fasta -outfmt 6 >seven.blast`.

```
A
 \
  \
   ---C
  /    \
 /      \
B        \
          ---G
D        /
 \      /
  \    /
   ---F
  /
 /
E
```

Generation command
------------------

```
random.tree A_
random.tree B_
random.tree C_
random.tree D_
random.tree E_
random.tree F_
random.tree G_
random A_
random B_
random C_
random D_
random E_
random F_
random G_
branch A_z C_
branch B_z C_
branch D_z F_
branch E_z F_
branch C_z G_
branch F_z G_
composite C_
composite F_
composite G_
show
apply
leaves seven.fasta
```
