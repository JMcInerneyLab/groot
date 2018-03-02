Dual (Groot sample data set)
============================

Tree
----

                 A4
                   \ 
                    \
             A3      CL
               \    /  \
                \  /    \
         A1      CL      \
           \    /         \
            \  /           \
     A1      CL             \
       \    / \              \
        \  /   \     C1       \
        ROOT    \   /          \
                 \ /            \
        ROOT   FUSION    C2      \
        /  \    /  \    /         \      D1
       /    \  /    \  /           \    /
     B1      CL      CL      C3     \  /
            /  \       \    /      FUSION    D2
           /    \       \  /         | \    /
         B2      CL      CL      C4  |  \  /
                /  \       \    /    |   CL      D3
               /    \       \  /     |     \    /
             B3      CK      CL      |      \  /
                    /  \             |       CL      D4
                   /    \           /          \    /
                 B4      -----------            \  /
                                                 CL


Generation
----------

```
faketree tree A1 : tree -A2 : tree --A3 : tree ---A4 : tree B1 : tree -B2 : tree --B3 : tree ---B4 : tree C1 : tree -C2 : tree --C3 : tree ---C4 : tree D1 : tree -D2 : tree --D3 : tree ---D4 : random A1 : random B1 : random C1 : random D1 : branch A2 C1 : branch B2 C1 : branch A4 D1 : branch B4 D1 : composite C1 : composite D1 : apply : nodes dual.fasta
blast -query=dual.fasta -subject=dual.fasta -outfmt=6 > dual.blast
```