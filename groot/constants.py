import itertools
from typing import Callable, Iterable, Iterator, Tuple, cast

from mhelper import MEnum, ResourceIcon, SwitchError, MFlags


_Model_ = "Model"

# noinspection SpellCheckingInspection
DNA_BASES = "GACT"


class Stage:
    def __init__( self, name: str,
                  icon: ResourceIcon,
                  headline: Callable[[], str],
                  requires: Tuple["Stage", ...],
                  status: Callable[[_Model_], Iterable[bool]],
                  hot = False,
                  cold = False ):
        assert isinstance( requires, tuple )
        
        self.name = name
        self.icon = icon
        self.headline = headline
        self.requires = requires
        self.status = status
        self.hot = hot
        self.cold = cold
        self.index = len( StageCollection.INSTANCE )
    
    
    def __str__( self ):
        return self.name


def M( m: object ) -> _Model_:
    """
    Pass-through type-hint: casts `m` to a `Model`.
    """
    from groot.data.model import Model
    return cast( Model, m )


class StageCollection:
    INSTANCE = None
    
    
    def __init__( self ):
        StageCollection.INSTANCE = self
        from groot import resources
        
        self.FILE_1 = Stage( "File",
                             status = lambda m: M( m ).file_name,
                             headline = lambda m: M( m ).file_name,
                             icon = resources.black_file,
                             requires = () )
        self.SEQ_AND_SIM_ps = Stage( "Data",
                                     icon = resources.black_gene,
                                     status = lambda m: itertools.chain( (bool( M( m ).edges ),), (bool( x.site_array ) for x in M( m ).genes) ),
                                     headline = lambda m: "{} of {} sequences with site data. {} edges".format( M( m ).genes.num_fasta, M( m ).genes.__len__(), M( m ).edges.__len__() ),
                                     requires = () )
        self.SEQUENCES_2 = Stage( "Fasta",
                                  icon = resources.black_gene,
                                  headline = lambda m: "{} of {} sequences with site data".format( M( m ).genes.num_fasta, M( m ).genes.__len__() ),
                                  requires = (),
                                  status = lambda m: [bool( x.site_array ) for x in M( m ).genes] )
        self.SIMILARITIES_3 = Stage( "Blast",
                                     icon = resources.black_edge,
                                     status = lambda m: (bool( M( m ).edges ),),
                                     headline = lambda m: "{} edges".format( M( m ).edges.__len__() ),
                                     requires = () )
        self.MAJOR_4 = Stage( "Major",
                              icon = resources.black_major,
                              status = lambda m: (M( m ).components.has_major_gene_got_component( x ) for x in M( m ).genes),
                              headline = lambda m: "{} sequences assigned to {} components".format( sum( 1 for x in M( m ).genes if M( m ).components.has_major_gene_got_component( x ) ), M( m ).components.count ),
                              requires = (self.SEQUENCES_2, self.SIMILARITIES_3) )
        self.MINOR_5 = Stage( "Minor",
                              icon = resources.black_minor,
                              status = lambda m: (bool( x.minor_domains ) for x in M( m ).components),
                              headline = lambda m: "{} minor sequences".format( sum( (len( x.minor_domains ) if x.minor_domains else 0) for x in M( m ).components ) ),
                              requires = (self.MAJOR_4,) )
        self.DOMAINS_6 = Stage( "Domains",
                                icon = resources.black_domain,
                                status = lambda m: (bool( M( m ).user_domains ),),
                                headline = lambda m: "{} domains".format( len( M( m ).user_domains ) ),
                                requires = (self.SEQUENCES_2,) )
        self.ALIGNMENTS_7 = Stage( "Alignments",
                                   icon = resources.black_alignment,
                                   status = lambda m: (bool( x.alignment ) for x in M( m ).components),
                                   headline = lambda m: "{} of {} components aligned".format( M( m ).components.num_aligned, M( m ).components.count ),
                                   requires = (self.MINOR_5,) )
        self.OUTGROUPS_7b = Stage( "Outgroups",
                                   icon = resources.black_outgroup,
                                   status = lambda m: (any( x.is_positioned for x in M( m ).genes ),),
                                   headline = lambda m: "{} outgroups".format( sum( x.is_positioned for x in M( m ).genes ) ),
                                   requires = (self.SEQ_AND_SIM_ps,) )
        self.TREES_8 = Stage( "Trees",
                              icon = resources.black_tree,
                              status = lambda m: (x.tree is not None for x in M( m ).components),
                              headline = lambda m: "{} of {} components have a tree".format( M( m ).components.num_trees, M( m ).components.count ),
                              requires = (self.ALIGNMENTS_7,) )
        self.FUSIONS_9 = Stage( "Fusions",
                                icon = resources.black_fusion,
                                status = lambda m: (M( m ).fusions is not None,),
                                headline = lambda m: "{} fusion events and {} fusion points".format( M( m ).fusions.__len__(), M( m ).fusions.num_points ) if M( m ).fusions else "(None)",
                                requires = (self.TREES_8,) )
        self._POINTS_9b = Stage( "Points",
                                 icon = resources.black_fusion,
                                 status = lambda m: (M( m ).fusions is not None,),
                                 headline = lambda m: "",
                                 requires = (self.TREES_8,) )
        self.SPLITS_10 = Stage( "Splits",
                                status = lambda m: (M( m ).splits is not None,),
                                icon = resources.black_split,
                                headline = lambda m: "{} splits".format( M( m ).splits.__len__() ) if M( m ).splits else "(None)",
                                requires = (self.FUSIONS_9,) )
        self.CONSENSUS_11 = Stage( "Consensus",
                                   icon = resources.black_consensus,
                                   status = lambda m: (M( m ).consensus is not None,),
                                   headline = lambda m: "{} of {} splits are viable".format( M( m ).consensus.__len__(), M( m ).splits.__len__() ) if M( m ).consensus else "(None)",
                                   requires = (self.SPLITS_10,) )
        self.SUBSETS_12 = Stage( "Subsets",
                                 status = lambda m: (M( m ).subsets is not None,),
                                 icon = resources.black_subset,
                                 headline = lambda m: "{} subsets".format( M( m ).subsets.__len__() ) if M( m ).subsets else "(None)",
                                 requires = (self.FUSIONS_9,) )
        self.PREGRAPHS_13 = Stage( "Pregraphs",
                                   status = lambda m: () if M( m ).subsets is None else (True,) if len( M( m ).subsets ) == 0 else ((x.pregraphs is not None) for x in M( m ).subsets),
                                   icon = resources.black_pregraph,
                                   headline = lambda m: "{} pregraphs".format( sum( (len( x.pregraphs ) if x.pregraphs else 0) for x in M( m ).subsets ) ),
                                   requires = (self.SUBSETS_12,) )
        self.SUPERTREES_14 = Stage( "Subgraphs",
                                    status = lambda m: (M( m ).subgraphs is not None,),
                                    icon = resources.black_subgraph,
                                    headline = lambda m: "{} of {} subsets have a graph".format( M( m ).subgraphs.__len__(), M( m ).subsets.__len__() ) if M( m ).subgraphs else "(None)",
                                    requires = (self.PREGRAPHS_13,) )
        self.FUSE_15 = Stage( "Fused",
                              status = lambda m: (M( m ).fusion_graph_unclean is not None,),
                              icon = resources.black_nrfg,
                              headline = lambda m: "Subgraphs fused" if M( m ).fusion_graph_unclean else "(None)",
                              requires = (self.SUPERTREES_14,) )
        self.CLEAN_16 = Stage( "Cleaned",
                               icon = resources.black_clean,
                               status = lambda m: (M( m ).fusion_graph_clean is not None,),
                               headline = lambda m: "NRFG clean" if M( m ).fusion_graph_clean else "(None)",
                               requires = (self.FUSE_15,) )
        self.CHECKED_17 = Stage( "Checked",
                                 icon = resources.black_check,
                                 status = lambda m: (M( m ).report is not None,),
                                 headline = lambda m: "NRFG checked" if M( m ).report else "(None)",
                                 requires = (self.CLEAN_16,) )
    
    
    def __iter__( self ) -> Iterator[Stage]:
        for k, v in self.__dict__.items():
            if not k.startswith( "_" ):
                if isinstance( v, Stage ):
                    yield v
    
    
    def __len__( self ):
        return sum( 1 for _ in iter( self ) )


STAGES = StageCollection()


class EFormat( MEnum ):
    """
    Output formats.
    Note some output formats only work for DAGs (trees).
    File extensions are listed, which control how the file is opened if the `open` file specifier is passed to the export functions.
    
    :cvar NEWICK:      Newick format. DAG only. (.NWK)
    :cvar ASCII:       Simple ASCII diagram. (.TXT)
    :cvar ETE_GUI:     Interactive diagram, provided by Ete. Is also available in CLI. Requires Ete. DAG only. (No output file)
    :cvar ETE_ASCII:   ASCII, provided by Ete. Requires Ete. DAG only. (.TXT)
    :cvar CSV:         Excel-type CSV with headers, suitable for Gephi. (.CSV)
    :cvar VISJS:       Vis JS (.HTML)
    :cvar TSV:         Tab separated value (.TSV)
    :cvar SVG:         HTML formatted SVG graphic (.HTML)
    :cvar CYJS:        Cytoscape JS (.HTML)
    """
    NEWICK = 1
    ASCII = 2
    ETE_GUI = 3
    ETE_ASCII = 4
    CSV = 7
    VISJS = 9
    TSV = 10
    SVG = 11
    CYJS = 12
    COMPACT = 13
    _HTML = CYJS
    
    
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
        elif self == EFormat.CYJS:
            return ".html"
        elif self == EFormat.SVG:
            return ".html"
        elif self == EFormat.COMPACT:
            return ".edg"
        else:
            raise SwitchError( "self", self )


APP_NAME = "Groot" 

#
# File extensions
#
EXT_MODEL = ".{}".format( APP_NAME.lower() )
EXT_JSON = ".json"
EXT_FASTA = ".fasta"
EXT_BLAST = ".blast"

#
# Folder names
#
F_EXTRA = "{}-EXTRA".format( APP_NAME.upper() )
F_TESTS = "{}-TESTS".format( APP_NAME.upper() )
F_CREATE = "{}-CREATE".format( APP_NAME.upper() )
F_DROP = "{}-DROP".format( APP_NAME.upper() )
F_PRINT = "{}-PRINT".format( APP_NAME.upper() )
F_SET = "{}-SET".format( APP_NAME.upper() )
F_IMPORT = "{}-IMPORT".format( APP_NAME.upper() )
F_FILE = "{}-FILE".format( APP_NAME.upper() )


class EChanges( MFlags ):
    """
    Describes the changes after a command has been issued.
    These are returned by most of the GROOT user-commands.
    When the GUI receives an EChanges object, it updates the pertinent data.
    The CLI does nothing with the object.
    
    :cvar MODEL_OBJECT:     The model object itself has changed.
                            Implies FILE_NAME, MODEL_ENTITIES
    :cvar FILE_NAME:        The filename of the model has changed and/or the recent files list.
    :cvar MODEL_ENTITIES:   The entities within the model have changed.
    :cvar COMPONENTS:       The components within the model have changed.
    :cvar COMP_DATA:        Meta-data (e.g. trees) on the components have changed
    :cvar MODEL_DATA:       Meta-data (e.g. the NRFG) on the model has changed
    :cvar INFORMATION:      The text printed during the command's execution is of primary concern to the user.
    """
    __no_flags_name__ = "NONE"
    
    MODEL_OBJECT = 1 << 0
    FILE_NAME = 1 << 1
    MODEL_ENTITIES = 1 << 2
    COMPONENTS = 1 << 3
    COMP_DATA = 1 << 4
    MODEL_DATA = 1 << 5
    INFORMATION = 1 << 6
    DOMAINS = 1 << 7


class BROWSE_MODE:
    """
    GUI only: Which browser to use. 
    
    :cvar SYSTEM:   Always use system browser
    :cvar ASK:      Always ask
    :cvar INBUILT:  Always use inbuilt browser (requires Qt web engine is installed)
    """
    SYSTEM = 0
    ASK = 1
    INBUILT = 2


class EStartupMode( MEnum ):
    """
    GUI only:  Which screen shows when the GUI starts.
    """
    STARTUP = 0
    WORKFLOW = 1
    SAMPLES = 2
    NOTHING = 3


class EWindowMode( MEnum ):
    """
    GUI only: How sub-windows are displayed.
    
    This was introduced because MDI/TDI cause problems on some platforms.
    
    :cvar BASIC:    Basic overlapping windows.
    :cvar MDI:      Multiple document interface.
    :cvar TDI:      Tabbed document interface.
    """
    BASIC = 0
    MDI = 1
    TDI = 2


class EDomainNames( MEnum ):
    """
    How to display domain names.
    
    :cvar START_END:            Use the start and end positions
    :cvar START_LENGTH:         Use the start and the length
    :cvar START_END_LENGTH:     Use the start, end, and the length 
    """
    START_END = 1
    START_LENGTH = 2
    START_END_LENGTH = 3


class EGeneNames( MEnum ):
    """
    How to display gene names.
    
    :cvar DISPLAY:    Use the user-designated display name
    :cvar ACCESSION:  Always use the accession
    :cvar LEGACY:     Always use the PHYLIP compatible generated ID
    :cvar COMPONENT:  As `DISPLAY`, with the major component as a prefix. 
    """
    DISPLAY = 1
    ACCESSION = 2
    LEGACY = 3
    COMPONENT = 4


class EComponentGraph( MEnum ):
    """
    Selects which graph on a component to display.
    """
    UNROOTED = 1
    UNMODIFIED = 2
    ROOTED = 3


class EFusionNames( MEnum ):
    """
    How to display fusion names.
    
    :cvar ACCID:    Unique accession-like ID
    :cvar READABLE: Try and make a readable name (may not be unique)
    """
    ACCID = 1
    READABLE = 2


class EComponentNames( MEnum ):
    """
    How to display component names.
    
    :cvar ACCID: Unique accession-like ID
    :cvar FIRST: Name after first gene in component
    """
    ACCID = 1
    FIRST = 2
