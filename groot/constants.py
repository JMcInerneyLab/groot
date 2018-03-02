from mhelper import MEnum, SwitchError


class EFormat( MEnum ):
    """
    :data NEWICK:       Newick format
    :data ASCII:        Simple ASCII diagram
    :data ETE_GUI:      Interactive diagram, provided by Ete. Is also available in CLI. Requires Ete.
    :data ETE_ASCII:    ASCII, provided by Ete. Requires Ete.
    :data SVG:          SVG graphic
    :data HTML:         HTML graphic
    :data CSV:          Excel-type CSV with headers, suitable for Gephi.
    :data DEBUG:        Show debug data. For internal use.
    """
    NEWICK = 1
    ASCII = 2
    ETE_GUI = 3
    ETE_ASCII = 4
    CSV = 7
    VISJS = 9
    TSV = 10
    
    
    def to_extension( self ):
        if self == EFormat.NEWICK:
            return ".nwk"
        elif self == EFormat.ASCII:
            return ".txt"
        elif self == EFormat.ETE_ASCII:
            return ".txt"
        elif self == EFormat.ETE_GUI:
            return ""
        elif self == EFormat.CSV:
            return ".csv"
        elif self == EFormat.TSV:
            return ".tsv"
        elif self == EFormat.VISJS:
            return ".html"
        else:
            raise SwitchError( "self", self )


BINARY_EXTENSION = ".groot"
DIALOGUE_FILTER = "Genomic n-rooted fusion graph (*.groot)"
DIALOGUE_FILTER_FASTA = "FASTA (*.fasta)"
DIALOGUE_FILTER_NEWICK = "Newick tree (*.newick)"
APP_NAME = "GROOT"