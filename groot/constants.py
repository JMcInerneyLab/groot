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
    BLAST_1 = auto()
    FASTA_2 = auto()
    COMPONENTS_3 = auto()
    DOMAINS_4 = auto()
    ALIGNMENTS_5 = auto()
    TREES_6 = auto()
    FUSIONS_7 = auto()
    POINTS_7b = auto()
    SPLITS_8 = auto()
    CONSENSUS_9 = auto()
    SUBSETS_10 = auto()
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


class LegoStageCollection:
    def __init__( self ):
        from groot.frontends.gui.forms.resources import resources
        self.FILE_0 = LegoStage( "File",
                                 EWorkflow.NONE,
                                 status = lambda m: m.file_name,
                                 headline = lambda m: m.file_name,
                                 icon = resources.save_file,
                                 requires = None )
        self.DATA_0 = LegoStage( "Data",
                                 EWorkflow.NONE,
                                 icon = resources.sequence,
                                 status = lambda m: itertools.chain( (bool( m.edges ),), (bool( x.site_array ) for x in m.sequences) ),
                                 headline = lambda m: "{} of {} sequences with site data. {} edges".format( m.sequences.num_fasta, m.sequences.__len__(), m.edges.__len__() ),
                                 requires = None )
        self.BLAST_1 = LegoStage( "Blast",
                                  EWorkflow.BLAST_1,
                                  icon = resources.edge,
                                  status = lambda m: (bool( m.edges ),),
                                  headline = lambda m: "{} edges".format( m.edges.__len__() ),
                                  requires = None )
        self.FASTA_2 = LegoStage( "Fasta",
                                  EWorkflow.FASTA_2,
                                  icon = resources.sequence,
                                  headline = lambda m: "{} of {} sequences with site data".format( m.sequences.num_fasta, m.sequences.__len__() ),
                                  requires = None,
                                  status = lambda m: [bool( x.site_array ) for x in m.sequences] )
        self.COMPONENTS_3 = LegoStage( "Components",
                                       EWorkflow.COMPONENTS_3,
                                       icon = resources.compartmentalise,
                                       status = lambda m: (bool( m.components ),),
                                       headline = lambda m: "{} components".format( m.components.count ),
                                       requires = self.FASTA_2 )
        self.DOMAINS_4 = LegoStage( "Domains",
                                    EWorkflow.DOMAINS_4,
                                    icon = resources.domain,
                                    status = lambda m: (bool( m.user_domains ),),
                                    headline = lambda m: "{} domains".format( len( m.user_domains ) ),
                                    requires = self.FASTA_2 )
        self.ALIGNMENTS_5 = LegoStage( "Alignments",
                                       EWorkflow.ALIGNMENTS_5,
                                       icon = resources.align_left,
                                       status = lambda m: (bool( x.alignment ) for x in m.components),
                                       headline = lambda m: "{} of {} components aligned".format( m.components.num_aligned, m.components.count ),
                                       requires = self.COMPONENTS_3 )
        self.TREES_6 = LegoStage( "Trees",
                                  EWorkflow.TREES_6,
                                  icon = resources.black_tree,
                                  status = lambda m: (bool( x.tree ) for x in m.components),
                                  headline = lambda m: "{} of {} components have a tree".format( m.components.num_trees, m.components.count ),
                                  requires = self.ALIGNMENTS_5 )
        self.FUSIONS_7 = LegoStage( "Fusions",
                                    EWorkflow.FUSIONS_7,
                                    icon = resources.fuse,
                                    status = lambda m: (bool( m.fusion_events ),),
                                    headline = lambda m: "{} fusion events and {} fusion points".format( m.fusion_events.__len__(), m.fusion_events.num_points ) if m.fusion_events else "(None)",
                                    requires = self.TREES_6 )
        
        self.POINTS_7b = LegoStage( "Points",
                                    EWorkflow.NONE,
                                    icon = resources.fuse,
                                    status = lambda m: (bool( m.fusion_events ),),
                                    headline = lambda m: "",
                                    requires = self.TREES_6 )
        self.SPLITS_8 = LegoStage( "Splits",
                                   EWorkflow.SPLITS_8,
                                   status = lambda m: (bool( m.nrfg.splits ),),
                                   icon = resources.split,
                                   headline = lambda m: "{} splits".format( m.nrfg.splits.__len__() ) if m.nrfg.splits else "(None)",
                                   requires = self.FUSIONS_7 )
        self.CONSENSUS_9 = LegoStage( "Consensus",
                                      EWorkflow.CONSENSUS_9,
                                      icon = resources.consensus,
                                      status = lambda m: (bool( m.nrfg.consensus ),),
                                      headline = lambda m: "{} of {} splits are viable".format( m.nrfg.consensus.__len__(), m.nrfg.splits.__len__() ) if m.nrfg.consensus else "(None)",
                                      requires = self.SPLITS_8 )
        self.SUBSETS_10 = LegoStage( "Subsets",
                                     EWorkflow.SUBSETS_10,
                                     status = lambda m: (bool( m.nrfg.subsets ),),
                                     icon = resources.subset,
                                     headline = lambda m: "{} subsets".format( m.nrfg.subsets.__len__() ) if m.nrfg.subsets else "(None)",
                                     requires = self.CONSENSUS_9 )
        self.SUBGRAPHS_11 = LegoStage( "Subgraphs",
                                       EWorkflow.SUBGRAPHS_11,
                                       status = lambda m: (bool( m.nrfg.minigraphs ),),
                                       icon = resources.minigraph,
                                       headline = lambda m: "{} of {} subsets have a graph".format( m.nrfg.minigraphs.__len__(), m.nrfg.subsets.__len__() ) if m.nrfg.minigraphs else "(None)",
                                       requires = self.SUBSETS_10 )
        self.FUSED_12 = LegoStage( "Fused",
                                   EWorkflow.FUSED_12,
                                   status = lambda m: (bool( m.nrfg.fusion_graph_unclean ),),
                                   icon = resources.stitch,
                                   headline = lambda m: "Subgraphs fused" if m.nrfg.fusion_graph_unclean else "(None)",
                                   requires = self.SUBGRAPHS_11 )
        self.CLEANED_13 = LegoStage( "Cleaned",
                                     EWorkflow.CLEANED_13,
                                     icon = resources.clean,
                                     status = lambda m: (bool( m.nrfg.fusion_graph_clean ),),
                                     headline = lambda m: "NRFG clean" if m.nrfg.fusion_graph_clean else "(None)",
                                     requires = self.FUSED_12 )
        self.CHECKED_14 = LegoStage( "Checked",
                                     EWorkflow.CHECKED_14,
                                     icon = resources.check,
                                     status = lambda m: (bool( m.nrfg.report ),),
                                     headline = lambda m: "NRFG checked" if m.nrfg.report else "(None)",
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
MINIGRAPH_PREFIX = "m:"
COMPONENT_PREFIX = "c:"
