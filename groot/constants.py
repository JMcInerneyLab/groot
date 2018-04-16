import itertools
from typing import Callable, Iterable, Iterator, Optional

from mhelper import MEnum, ResourceIcon, SwitchError


class EIntent( MEnum ):
    VIEW = 1
    CREATE = 2
    DROP = 3


_LegoModel_ = "LegoModel"


class LegoStage:
    def __init__( self, name: str,
                  icon: ResourceIcon,
                  headline: Callable[[], str],
                  requires: Optional["LegoStage"],
                  status: Callable[[_LegoModel_], Iterable[bool]],
                  hot = False,
                  cold = False ):
        self.name = name
        self.icon = icon
        self.headline = headline
        self.requires = requires
        self.status = status
        self.hot = hot
        self.cold = cold
        self.index = len( LegoStageCollection.INSTANCE )
    
    
    def visualisers( self, intent: EIntent ):
        from groot.frontends.gui import gui_workflow
        for visualiser in gui_workflow.VISUALISERS:
            if self in visualiser.intents[intent]:
                yield visualiser
    
    
    def __str__( self ):
        return self.name


class LegoStageCollection:
    INSTANCE = None
    
    
    def __init__( self ):
        LegoStageCollection.INSTANCE = self
        from groot.frontends.gui.forms.resources import resources
        
        self._FILE_0 = LegoStage( "File",
                                  status = lambda m: m.file_name,
                                  headline = lambda m: m.file_name,
                                  icon = resources.black_file,
                                  requires = None )
        self._DATA_0 = LegoStage( "Data",
                                  icon = resources.black_gene,
                                  status = lambda m: itertools.chain( (bool( m.edges ),), (bool( x.site_array ) for x in m.sequences) ),
                                  headline = lambda m: "{} of {} sequences with site data. {} edges".format( m.sequences.num_fasta, m.sequences.__len__(), m.edges.__len__() ),
                                  requires = None )
        self.FASTA_1 = LegoStage( "Blast",
                                  icon = resources.black_edge,
                                  status = lambda m: (bool( m.edges ),),
                                  headline = lambda m: "{} edges".format( m.edges.__len__() ),
                                  requires = None )
        self.BLAST_2 = LegoStage( "Fasta",
                                  icon = resources.black_gene,
                                  headline = lambda m: "{} of {} sequences with site data".format( m.sequences.num_fasta, m.sequences.__len__() ),
                                  requires = None,
                                  status = lambda m: [bool( x.site_array ) for x in m.sequences] )
        self.MAJOR_3 = LegoStage( "Major",
                                  icon = resources.black_major,
                                  status = lambda m: (bool( m.components ),),
                                  headline = lambda m: "{} components".format( m.components.count ),
                                  requires = self.FASTA_1 )
        self.MINOR_3 = LegoStage( "Minor",
                                  icon = resources.black_minor,
                                  status = lambda m: (bool( x.minor_subsequences ) for x in m.components),
                                  headline = lambda m: "{} minor sequences".format( sum( len( x.minor_subsequences ) for x in m.components ) ),
                                  requires = self.MAJOR_3 )
        self.DOMAINS_4 = LegoStage( "Domains",
                                    icon = resources.black_domain,
                                    status = lambda m: (bool( m.user_domains ),),
                                    headline = lambda m: "{} domains".format( len( m.user_domains ) ),
                                    requires = self.FASTA_1 )
        self.ALIGNMENTS_5 = LegoStage( "Alignments",
                                       icon = resources.black_alignment,
                                       status = lambda m: (bool( x.alignment ) for x in m.components),
                                       headline = lambda m: "{} of {} components aligned".format( m.components.num_aligned, m.components.count ),
                                       requires = self.MINOR_3 )
        self.OUTGROUPS_5b = LegoStage( "Outgroups",
                                       icon = resources.black_outgroup,
                                       status = lambda m: (any( x.is_positioned for x in m.sequences ),),
                                       headline = lambda m: "{} outgroups".format( sum( x.is_positioned for x in m.sequences ) ),
                                       requires = self._DATA_0 )
        self.TREES_6 = LegoStage( "Trees",
                                  icon = resources.black_tree,
                                  status = lambda m: (bool( x.tree ) for x in m.components),
                                  headline = lambda m: "{} of {} components have a tree".format( m.components.num_trees, m.components.count ),
                                  requires = self.ALIGNMENTS_5 )
        self.FUSIONS_7 = LegoStage( "Fusions",
                                    icon = resources.black_fusion,
                                    status = lambda m: (bool( m.fusion_events ),),
                                    headline = lambda m: "{} fusion events and {} fusion points".format( m.fusion_events.__len__(), m.fusion_events.num_points ) if m.fusion_events else "(None)",
                                    requires = self.TREES_6 )
        
        self._POINTS_7b = LegoStage( "Points",
                                     icon = resources.black_fusion,
                                     status = lambda m: (bool( m.fusion_events ),),
                                     headline = lambda m: "",
                                     requires = self.TREES_6 )
        self.SPLITS_8 = LegoStage( "Splits",
                                   status = lambda m: (bool( m.splits ),),
                                   icon = resources.black_split,
                                   headline = lambda m: "{} splits".format( m.splits.__len__() ) if m.splits else "(None)",
                                   requires = self.FUSIONS_7 )
        self.CONSENSUS_9 = LegoStage( "Consensus",
                                      icon = resources.black_consensus,
                                      status = lambda m: (bool( m.consensus ),),
                                      headline = lambda m: "{} of {} splits are viable".format( m.consensus.__len__(), m.splits.__len__() ) if m.consensus else "(None)",
                                      requires = self.SPLITS_8 )
        self.SUBSETS_10 = LegoStage( "Subsets",
                                     status = lambda m: (bool( m.subsets ),),
                                     icon = resources.black_subset,
                                     headline = lambda m: "{} subsets".format( m.subsets.__len__() ) if m.subsets else "(None)",
                                     requires = self.CONSENSUS_9 )
        self.PREGRAPHS_11 = LegoStage( "Pregraphs",
                                       status = lambda m: (bool( x.pregraphs ) for x in m.subsets),
                                       icon = resources.black_pregraph,
                                       headline = lambda m: "{} pregraphs".format( sum( len( x.pregraphs ) for x in m.subsets ) ),
                                       requires = self.SUBSETS_10 )
        self.SUBGRAPHS_11 = LegoStage( "Subgraphs",
                                       status = lambda m: (bool( m.subgraphs ),),
                                       icon = resources.black_subgraph,
                                       headline = lambda m: "{} of {} subsets have a graph".format( m.subgraphs.__len__(), m.subsets.__len__() ) if m.subgraphs else "(None)",
                                       requires = self.PREGRAPHS_11 )
        self.FUSED_12 = LegoStage( "Fused",
                                   status = lambda m: (bool( m.fusion_graph_unclean ),),
                                   icon = resources.black_nrfg,
                                   headline = lambda m: "Subgraphs fused" if m.fusion_graph_unclean else "(None)",
                                   requires = self.SUBGRAPHS_11 )
        self.CLEANED_13 = LegoStage( "Cleaned",
                                     icon = resources.black_clean,
                                     status = lambda m: (bool( m.fusion_graph_clean ),),
                                     headline = lambda m: "NRFG clean" if m.fusion_graph_clean else "(None)",
                                     requires = self.FUSED_12 )
        self.CHECKED_14 = LegoStage( "Checked",
                                     icon = resources.black_check,
                                     status = lambda m: (bool( m.report ),),
                                     headline = lambda m: "NRFG checked" if m.report else "(None)",
                                     requires = self.CLEANED_13 )
    
    
    def __iter__( self ) -> Iterator[LegoStage]:
        for k, v in self.__dict__.items():
            if not k.startswith( "_" ):
                if isinstance( v, LegoStage ):
                    yield v
    
    
    def __len__( self ):
        return sum( 1 for _ in iter( self ) )


STAGES = LegoStageCollection()


class EFormat( MEnum ):
    """
    Output formats.
    Note some output formats only work for DAGs (trees).
    File extensions are listed, which control how the file is opened if the `open` file specifier is passed to the export functions.
    
    :data NEWICK      : Newick format. DAG only. (.NWK)
    :data ASCII       : Simple ASCII diagram. (.TXT)
    :data ETE_GUI     : Interactive diagram, provided by Ete. Is also available in CLI. Requires Ete. DAG only. (No output file)
    :data ETE_ASCII   : ASCII, provided by Ete. Requires Ete. DAG only. (.TXT)
    :data CSV         : Excel-type CSV with headers, suitable for Gephi. (.CSV)
    :data VISJS       : Vis JS (.HTML)
    :data TSV         : Tab separated value (.TSV)
    :data SVG         : HTML formatted SVG graphic (.HTML)
    :data CYJS        : Cytoscape JS (.HTML)
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
