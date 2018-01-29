from mhelper import MEnum


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
    SVG = 5
    HTML = 6
    CSV = 7
    DEBUG = 8
    VISJS = 9


class EOut( MEnum ):
    """
    Output mode.
    
    :data DEFAULT:   The default is:
                        If filename specified              = FILE
                        If output is HTML, SVG or VISJS    = OPEN
                        Other                              = NORMAL
    :data NORMAL:    Display in current UI
    :data STDOUT:    Write to STDOUT (regardless of current UI).
    :data CLIP:      Write to clipboard.
    :data FILE:      Write to file.
    :data FILEOPEN:  Write to file and open it.
    :data OPEN:      Write to a temporary file and open it.
    """
    DEFAULT = 0
    NORMAL = 1
    STDOUT = 2
    CLIP = 3
    FILE = 4
    OPEN = 5
    FILEOPEN = 6

BINARY_EXTENSION = ".groot"
DIALOGUE_FILTER = "Genomic n-rooted fusion graph (*.groot)"
DIALOGUE_FILTER_FASTA = "FASTA (*.fasta)"
DIALOGUE_FILTER_NEWICK = "Newick tree (*.newick)"
