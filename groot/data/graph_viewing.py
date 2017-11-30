from intermake import Theme
from groot.algorithms.fuse import FusionPoint
from groot.data.graphing import MNode
from groot.data.lego_model import LegoSequence


def format_node( self: MNode, format_str ) -> str:
    """
    Describes the nodes.
    The following format strings are accepted:
    
    `t` -   type-based description:
                "seq:accession" for sequences
                "fus:fusion"    for fusions
                "cla:uid"       for nodes with neither sequences nor fusions ("clades")
    `f` -   fusion                      (or empty)
    `u` -   node     uid
    `c` -   sequence major component    (or empty)
    `m` -   sequence minor components   (or empty)
    `a` -   sequence accession          (or empty)
    `l` -   sequence length             (or empty)
    `<` -   following characters are verbatim
    `>` -   stop verbatim / skip
    `S` -   skip if not in sequence
    `F` -   skip if not in fusion
    `C` -   skip if not in clade
    `T` -   skip if in sequence
    `G` -   skip if in fusion
    `D` -   skip if in clade
    -   -   anything else is verbatim
    """
    ss = []
    verbatim = False
    skip = False
    
    uid = self.uid
    sequence = self.tag if isinstance(self.tag, LegoSequence) else None
    fusion = self.tag if isinstance(self.tag, FusionPoint) else None
    
    for x in format_str:
        if skip:
            if x == ">":
                skip = False
        elif verbatim:
            if x == ">":
                verbatim = False
            else:
                ss.append( x )
        elif x == "<":
            verbatim = True
        elif x == "S":
            skip = sequence is None
        elif x == "F":
            skip = fusion is None
        elif x == "C":
            skip = fusion is None
        elif x == "T":
            skip = sequence is not None
        elif x == "G":
            skip = fusion is not None
        elif x == "D":
            skip = fusion is not None
        elif x == "t":
            if sequence:
                ss.append( "seq:{}".format( sequence.accession ) )
            elif fusion:
                ss.append( "fus:{}:{}".format( fusion.opposite_component, fusion.count ) )
            else:
                ss.append( "cla:{}".format( uid ) )
        elif x == "u":
            if sequence:
                ss.append( "seq:{}".format( sequence.accession ) )
            elif fusion:
                ss.append( "fus:{}:{}".format( fusion.opposite_component, fusion.count ) )
            else:
                ss.append( "~" )
        elif x == "f":
            if fusion:
                
                ss.append( Theme.BOLD + str( fusion ) + Theme.RESET )
        elif x == "u":
            ss.append( uid )
        elif x == "c":
            if sequence and sequence.component:
                ss.append( str( sequence.component ) )
        elif x == "m":
            if sequence:
                minor_components = sequence.minor_components()
                
                if minor_components:
                    for minor_component in sorted( minor_components, key = str ):
                        ss.append( str( minor_component ) )
        elif x == "a":
            if sequence:
                ss.append( sequence.accession )
        elif x == "l":
            if sequence:
                ss.append( sequence.length )
        else:
            ss.append( x )
    
    return "".join( str( x ) for x in ss ).strip()
