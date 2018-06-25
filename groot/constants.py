import itertools
from typing import Callable, Iterable, Iterator, Tuple, cast

from mhelper import MEnum, ResourceIcon, SwitchError, MFlags





_Model_ = "Model"


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
        
        self._FILE_0 = Stage( "File",
                              status = lambda m: M( m ).file_name,
                              headline = lambda m: M( m ).file_name,
                              icon = resources.black_file,
                              requires = () )
        self._DATA_0 = Stage( "Data",
                              icon = resources.black_gene,
                              status = lambda m: itertools.chain( (bool( M( m ).edges ),), (bool( x.site_array ) for x in M( m ).genes) ),
                              headline = lambda m: "{} of {} sequences with site data. {} edges".format( M( m ).genes.num_fasta, M( m ).genes.__len__(), M( m ).edges.__len__() ),
                              requires = () )
        self.FASTA_1 = Stage( "Fasta",
                              icon = resources.black_gene,
                              headline = lambda m: "{} of {} sequences with site data".format( M( m ).genes.num_fasta, M( m ).genes.__len__() ),
                              requires = (),
                              status = lambda m: [bool( x.site_array ) for x in M( m ).genes] )
        self.BLAST_2 = Stage( "Blast",
                              icon = resources.black_edge,
                              status = lambda m: (bool( M( m ).edges ),),
                              headline = lambda m: "{} edges".format( M( m ).edges.__len__() ),
                              requires = () )
        self.MAJOR_3 = Stage( "Major",
                              icon = resources.black_major,
                              status = lambda m: (M( m ).components.has_major_gene_got_component( x ) for x in M( m ).genes),
                              headline = lambda m: "{} sequences assigned to {} components".format( sum( 1 for x in M( m ).genes if M( m ).components.has_major_gene_got_component( x ) ), M( m ).components.count ),
                              requires = (self.FASTA_1,) )
        self.MINOR_3 = Stage( "Minor",
                              icon = resources.black_minor,
                              status = lambda m: (bool( x.minor_domains ) for x in M( m ).components),
                              headline = lambda m: "{} minor sequences".format( sum( (len( x.minor_domains ) if x.minor_domains else 0) for x in M( m ).components ) ),
                              requires = (self.MAJOR_3,) )
        self.DOMAINS_4 = Stage( "Domains",
                                icon = resources.black_domain,
                                status = lambda m: (bool( M( m ).user_domains ),),
                                headline = lambda m: "{} domains".format( len( M( m ).user_domains ) ),
                                requires = (self.FASTA_1,) )
        self.ALIGNMENTS_5 = Stage( "Alignments",
                                   icon = resources.black_alignment,
                                   status = lambda m: (bool( x.alignment ) for x in M( m ).components),
                                   headline = lambda m: "{} of {} components aligned".format( M( m ).components.num_aligned, M( m ).components.count ),
                                   requires = (self.MINOR_3,) )
        self.OUTGROUPS_5b = Stage( "Outgroups",
                                   icon = resources.black_outgroup,
                                   status = lambda m: (any( x.is_positioned for x in M( m ).genes ),),
                                   headline = lambda m: "{} outgroups".format( sum( x.is_positioned for x in M( m ).genes ) ),
                                   requires = (self._DATA_0,) )
        self.TREES_6 = Stage( "Trees",
                              icon = resources.black_tree,
                              status = lambda m: (bool( x.tree ) for x in M( m ).components),
                              headline = lambda m: "{} of {} components have a tree".format( M( m ).components.num_trees, M( m ).components.count ),
                              requires = (self.ALIGNMENTS_5,) )
        self.FUSIONS_7 = Stage( "Fusions",
                                icon = resources.black_fusion,
                                status = lambda m: (bool( M( m ).fusions ),),
                                headline = lambda m: "{} fusion events and {} fusion points".format( M( m ).fusions.__len__(), M( m ).fusions.num_points ) if M( m ).fusions else "(None)",
                                requires = (self.TREES_6,) )
        
        self._POINTS_7b = Stage( "Points",
                                 icon = resources.black_fusion,
                                 status = lambda m: (bool( M( m ).fusions ),),
                                 headline = lambda m: "",
                                 requires = (self.TREES_6,) )
        self.SPLITS_8 = Stage( "Splits",
                               status = lambda m: (bool( M( m ).splits ),),
                               icon = resources.black_split,
                               headline = lambda m: "{} splits".format( M( m ).splits.__len__() ) if M( m ).splits else "(None)",
                               requires = (self.FUSIONS_7,) )
        self.CONSENSUS_9 = Stage( "Consensus",
                                  icon = resources.black_consensus,
                                  status = lambda m: (bool( M( m ).consensus ),),
                                  headline = lambda m: "{} of {} splits are viable".format( M( m ).consensus.__len__(), M( m ).splits.__len__() ) if M( m ).consensus else "(None)",
                                  requires = (self.SPLITS_8,) )
        self.SUBSETS_10 = Stage( "Subsets",
                                 status = lambda m: (bool( M( m ).subsets ),),
                                 icon = resources.black_subset,
                                 headline = lambda m: "{} subsets".format( M( m ).subsets.__len__() ) if M( m ).subsets else "(None)",
                                 requires = (self.CONSENSUS_9,) )
        self.PREGRAPHS_11 = Stage( "Pregraphs",
                                   status = lambda m: (bool( x.pregraphs ) for x in M( m ).subsets),
                                   icon = resources.black_pregraph,
                                   headline = lambda m: "{} pregraphs".format( sum( (len( x.pregraphs ) if x.pregraphs else 0) for x in M( m ).subsets ) ),
                                   requires = (self.SUBSETS_10,) )
        self.SUBGRAPHS_11 = Stage( "Subgraphs",
                                   status = lambda m: (bool( M( m ).subgraphs ),),
                                   icon = resources.black_subgraph,
                                   headline = lambda m: "{} of {} subsets have a graph".format( M( m ).subgraphs.__len__(), M( m ).subsets.__len__() ) if M( m ).subgraphs else "(None)",
                                   requires = (self.PREGRAPHS_11,) )
        self.FUSED_12 = Stage( "Fused",
                               status = lambda m: (bool( M( m ).fusion_graph_unclean ),),
                               icon = resources.black_nrfg,
                               headline = lambda m: "Subgraphs fused" if M( m ).fusion_graph_unclean else "(None)",
                               requires = (self.SUBGRAPHS_11,) )
        self.CLEANED_13 = Stage( "Cleaned",
                                 icon = resources.black_clean,
                                 status = lambda m: (bool( M( m ).fusion_graph_clean ),),
                                 headline = lambda m: "NRFG clean" if M( m ).fusion_graph_clean else "(None)",
                                 requires = (self.FUSED_12,) )
        self.CHECKED_14 = Stage( "Checked",
                                 icon = resources.black_check,
                                 status = lambda m: (bool( M( m ).report ),),
                                 headline = lambda m: "NRFG checked" if M( m ).report else "(None)",
                                 requires = (self.CLEANED_13,) )
    
    
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
    
    :cvar NEWICK      : Newick format. DAG only. (.NWK)
    :cvar ASCII       : Simple ASCII diagram. (.TXT)
    :cvar ETE_GUI     : Interactive diagram, provided by Ete. Is also available in CLI. Requires Ete. DAG only. (No output file)
    :cvar ETE_ASCII   : ASCII, provided by Ete. Requires Ete. DAG only. (.TXT)
    :cvar CSV         : Excel-type CSV with headers, suitable for Gephi. (.CSV)
    :cvar VISJS       : Vis JS (.HTML)
    :cvar TSV         : Tab separated value (.TSV)
    :cvar SVG         : HTML formatted SVG graphic (.HTML)
    :cvar CYJS        : Cytoscape JS (.HTML)
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


BINARY_EXTENSION = ".groot"
DIALOGUE_FILTER = "Genomic n-rooted fusion graph (*.groot)"
DIALOGUE_FILTER_FASTA = "FASTA (*.fasta)"
DIALOGUE_FILTER_NEWICK = "Newick tree (*.newick)"
APP_NAME = "GROOT"
COMPONENT_PREFIX = "c:"
EXT_GROOT = ".groot"
EXT_FASTA = ".fasta"
EXT_BLAST = ".blast"
MCMD_FOLDER_NAME = "GROOT"
MCMD_FOLDER_NAME_EXTRA = "GROOT-EXTRA"
MCMD_FOLDER_NAME_TESTS = "GROOT-TESTS"
F_CREATE = "GROOT-CREATE"
F_DROP = "GROOT-DROP"
F_PRINT = "GROOT-PRINT"
F_SET = "GROOT-SET"
F_IMPORT = "GROOT-IMPORT"
F_FILE = "GROOT-FILE"


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
    SYSTEM = 0
    ASK = 1
    INBUILT = 2
