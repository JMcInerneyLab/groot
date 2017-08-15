# triptych

Contains five sequences:

## alpha.phy, beta.phy, gamma.phy
all 50 amino acids long, following the file "mytree.nwk"

## alphabeta.nwk, alphabeta.phy
combination of alpha/18 and beta/19

## alphabetagamma.nwk, alphabetagamma.phy
combination of alphabeta/18 and gamma/19

## final combinant gene (legodiagram script)
model MTREV
scale 0.25
tree mytree.nwk
length 50
create alpha
create beta
create gamma
combine alpha 18 beta 19 alphabeta
combine alphabeta 18 gamma 19 alphabetagamma
export truncated
blast truncated

## the tree
L
*--17
K  |
   *--18
J  |  |
*--16 |
I     |
      *--19
  H   |  |
  *---15 |
  G      |
         *---20
         |   |
         F   |
             *--21
      E      |  |
      *-----14  |
      D         |
                *----22 (root)
             B  |
             *--13
             A

all branch lengths are 1
