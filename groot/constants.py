from enum import auto
from typing import Callable, Optional, Iterable, Iterator
import itertools

from mhelper import MEnum, SwitchError, string_helper, ResourceIcon


class EIntent( MEnum ):
    VIEW = 1
    CREATE = 2
    DROP = 3


class EWorkflow( MEnum ):
    """
    Enumeration of the workflow stages.
    """
    NONE = auto()
    FASTA_1 = auto()
    BLAST_2 = auto()
    COMPONENTS_3 = auto()
    DOMAINS_4 = auto()
    ALIGNMENTS_5 = auto()
    TREES_6 = auto()
    FUSIONS_7 = auto()
    POINTS_7b = auto()
    SPLITS_8 = auto()
    CONSENSUS_9 = auto()
    SUBSETS_10 = auto()
    PREGRAPHS_11 = auto()
    SUBGRAPHS_11 = auto()
    FUSED_12 = auto()
    CLEANED_13 = auto()
    CHECKED_14 = auto()
    
    
    def __str__( self ):
        return string_helper.capitalise_first( self.name.split( "_" )[0].lower() )


class LegoStage:
    # noinspection PyUnresolvedReferences
    def __init__( self, name: str,
                  workflow: EWorkflow,
                  icon: ResourceIcon,
                  headline: Callable[[], str],
                  requires: Optional["LegoStage"],
                  status: Callable[["LegoModel"], Iterable[bool]] ):
        self.name = name
        self.workflow = workflow
        self.icon = icon
        self.headline = headline
        self.requires = requires
        self.status = status
    
    
    def visualisers( self, intent: EIntent ):
        from groot.frontends.gui import gui_workflow
        for visualiser in gui_workflow.VISUALISERS:
            if self in visualiser.intents[intent]:
                yield visualiser
    
    
    def __str__( self ):
        return self.name


class LegoStageCollection:
    def __init__( self ):
        from groot.frontends.gui.forms.resources import resources
        
        self.FILE_0 = LegoStage( "File",
                                 EWorkflow.NONE,
                                 status = lambda m: m.file_name,
                                 headline = lambda m: m.file_name,
                                 icon = resources.black_file,
                                 requires = None )
        self.DATA_0 = LegoStage( "Data",
                                 EWorkflow.NONE,
                                 icon = resources.black_gene,
                                 status = lambda m: itertools.chain( (bool( m.edges ),), (bool( x.site_array ) for x in m.sequences) ),
                                 headline = lambda m: "{} of {} sequences with site data. {} edges".format( m.sequences.num_fasta, m.sequences.__len__(), m.edges.__len__() ),
                                 requires = None )
        self.FASTA_1 = LegoStage( "Blast",
                                  EWorkflow.BLAST_2,
                                  icon = resources.black_edge,
                                  status = lambda m: (bool( m.edges ),),
                                  headline = lambda m: "{} edges".format( m.edges.__len__() ),
                                  requires = None )
        self.BLAST_2 = LegoStage( "Fasta",
                                  EWorkflow.FASTA_1,
                                  icon = resources.black_gene,
                                  headline = lambda m: "{} of {} sequences with site data".format( m.sequences.num_fasta, m.sequences.__len__() ),
                                  requires = None,
                                  status = lambda m: [bool( x.site_array ) for x in m.sequences] )
        self.COMPONENTS_3 = LegoStage( "Components",
                                       EWorkflow.COMPONENTS_3,
                                       icon = resources.black_component,
                                       status = lambda m: (bool( m.components ),),
                                       headline = lambda m: "{} components".format( m.components.count ),
                                       requires = self.FASTA_1 )
        self.DOMAINS_4 = LegoStage( "Domains",
                                    EWorkflow.DOMAINS_4,
                                    icon = resources.black_domain,
                                    status = lambda m: (bool( m.user_domains ),),
                                    headline = lambda m: "{} domains".format( len( m.user_domains ) ),
                                    requires = self.FASTA_1 )
        self.ALIGNMENTS_5 = LegoStage( "Alignments",
                                       EWorkflow.ALIGNMENTS_5,
                                       icon = resources.black_alignment,
                                       status = lambda m: (bool( x.alignment ) for x in m.components),
                                       headline = lambda m: "{} of {} components aligned".format( m.components.num_aligned, m.components.count ),
                                       requires = self.COMPONENTS_3 )
        self.OUTGROUPS_5b = LegoStage( "Outgroups",
                                       EWorkflow.NONE,
                                       icon = resources.black_outgroup,
                                       status = lambda m: (any( x.is_positioned for x in m.sequences ),),
                                       headline = lambda m: "{} outgroups".format( sum( x.is_positioned for x in m.sequences ) ),
                                       requires = self.DATA_0 )
        self.TREES_6 = LegoStage( "Trees",
                                  EWorkflow.TREES_6,
                                  icon = resources.black_tree,
                                  status = lambda m: (bool( x.tree ) for x in m.components),
                                  headline = lambda m: "{} of {} components have a tree".format( m.components.num_trees, m.components.count ),
                                  requires = self.ALIGNMENTS_5 )
        self.FUSIONS_7 = LegoStage( "Fusions",
                                    EWorkflow.FUSIONS_7,
                                    icon = resources.black_fusion,
                                    status = lambda m: (bool( m.fusion_events ),),
                                    headline = lambda m: "{} fusion events and {} fusion points".format( m.fusion_events.__len__(), m.fusion_events.num_points ) if m.fusion_events else "(None)",
                                    requires = self.TREES_6 )
        
        self.POINTS_7b = LegoStage( "Points",
                                    EWorkflow.NONE,
                                    icon = resources.black_fusion,
                                    status = lambda m: (bool( m.fusion_events ),),
                                    headline = lambda m: "",
                                    requires = self.TREES_6 )
        self.SPLITS_8 = LegoStage( "Splits",
                                   EWorkflow.SPLITS_8,
                                   status = lambda m: (bool( m.splits ),),
                                   icon = resources.black_split,
                                   headline = lambda m: "{} splits".format( m.splits.__len__() ) if m.splits else "(None)",
                                   requires = self.FUSIONS_7 )
        self.CONSENSUS_9 = LegoStage( "Consensus",
                                      EWorkflow.CONSENSUS_9,
                                      icon = resources.black_consensus,
                                      status = lambda m: (bool( m.consensus ),),
                                      headline = lambda m: "{} of {} splits are viable".format( m.consensus.__len__(), m.splits.__len__() ) if m.consensus else "(None)",
                                      requires = self.SPLITS_8 )
        self.SUBSETS_10 = LegoStage( "Subsets",
                                     EWorkflow.SUBSETS_10,
                                     status = lambda m: (bool( m.subsets ),),
                                     icon = resources.black_subset,
                                     headline = lambda m: "{} subsets".format( m.subsets.__len__() ) if m.subsets else "(None)",
                                     requires = self.CONSENSUS_9 )
        self.PREGRAPHS_11 = LegoStage( "Pregraphs",
                                       EWorkflow.PREGRAPHS_11,
                                       status = lambda m: (bool( x.pregraphs ) for x in m.subsets),
                                       icon = resources.black_pregraph,
                                       headline = lambda m: "{} pregraphs".format( sum( len( x.pregraphs ) for x in m.subsets ) ),
                                       requires = self.SUBSETS_10 )
        self.SUBGRAPHS_11 = LegoStage( "Subgraphs",
                                       EWorkflow.SUBGRAPHS_11,
                                       status = lambda m: (bool( m.subgraphs ),),
                                       icon = resources.black_subgraph,
                                       headline = lambda m: "{} of {} subsets have a graph".format( m.subgraphs.__len__(), m.subsets.__len__() ) if m.subgraphs else "(None)",
                                       requires = self.PREGRAPHS_11 )
        self.FUSED_12 = LegoStage( "Fused",
                                   EWorkflow.FUSED_12,
                                   status = lambda m: (bool( m.fusion_graph_unclean ),),
                                   icon = resources.black_nrfg,
                                   headline = lambda m: "Subgraphs fused" if m.fusion_graph_unclean else "(None)",
                                   requires = self.SUBGRAPHS_11 )
        self.CLEANED_13 = LegoStage( "Cleaned",
                                     EWorkflow.CLEANED_13,
                                     icon = resources.black_clean,
                                     status = lambda m: (bool( m.fusion_graph_clean ),),
                                     headline = lambda m: "NRFG clean" if m.fusion_graph_clean else "(None)",
                                     requires = self.FUSED_12 )
        self.CHECKED_14 = LegoStage( "Checked",
                                     EWorkflow.CHECKED_14,
                                     icon = resources.black_check,
                                     status = lambda m: (bool( m.report ),),
                                     headline = lambda m: "NRFG checked" if m.report else "(None)",
                                     requires = self.CLEANED_13 )
    
    
    def __iter__( self ) -> Iterator[LegoStage]:
        for v in self.__dict__.values():
            if isinstance( v, LegoStage ):
                yield v
    
    
    def __getitem__( self, item: EWorkflow ) -> LegoStage:
        for stage in self:
            if stage.workflow == item:
                return stage


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
