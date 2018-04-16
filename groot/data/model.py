from typing import List, FrozenSet, Sequence, Iterable, Iterator
from intermake.engine.environment import MENV, IVisualisable, UiInfo, EColour
from intermake_qt import resources as intermake_resources
from mhelper import string_helper, file_helper as FileHelper, NotFoundError

from groot.constants import LegoStage
from groot.data.model_meta import ModelStatus, LegoViewOptions
from groot.data.model_interfaces import ESiteType
from groot.data.model_core import FusionGraph, Subgraph, LegoReport, LegoFormation, LegoPregraph, LegoSplit, LegoSubset, LegoPoint, LegoSequence
from groot.data.model_collections import LegoUserGraphCollection, LegoSequenceCollection, LegoEdgeCollection, LegoFusionEventCollection, LegoUserDomainCollection, LegoComponentCollection


class LegoModel( IVisualisable ):
    """
    The model used by Groot.
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        Creates a new model with no data
        Use the `import_*` functions to add data from a file.
        """
        self.__incremental_id = 0
        self.sequences = LegoSequenceCollection( self )
        self.components = LegoComponentCollection( self )
        self.edges = LegoEdgeCollection( self )
        self.comments = ["MODEL CREATED AT {}".format( string_helper.current_time() )]
        self.__seq_type = ESiteType.UNKNOWN
        self.file_name = None
        self.fusion_events = LegoFusionEventCollection()
        self.ui_options = LegoViewOptions()
        self.user_domains = LegoUserDomainCollection( self )
        self.user_graphs = LegoUserGraphCollection( self )
        self.user_reports: List[LegoReport] = []
        self.splits: FrozenSet[LegoSplit] = frozenset()
        self.consensus: FrozenSet[LegoSplit] = frozenset()
        self.fusion_graph_unclean: FusionGraph = None
        self.fusion_graph_clean: FusionGraph = None
        self.report: LegoReport = None
        self.subsets: FrozenSet[LegoSubset] = frozenset()
        self.subgraphs: Sequence[Subgraph] = tuple()
        self.subgraphs_sources: Sequence[int] = tuple()
        self.subgraphs_destinations: Sequence[int] = tuple()
    
    
    def iter_pregraphs( self ) -> Iterable[LegoPregraph]:
        """
        Iterates through the model pregraphs.
        """
        for subset in self.subsets:  # type: LegoSubset
            if subset.pregraphs is not None:
                yield from subset.pregraphs
    
    
    @property
    def fusion_points( self ) -> Iterator[LegoPoint]:
        for event in self.fusion_events:
            for formation in event.formations:
                yield from formation.points
    
    
    def get_status( self, stage: LegoStage ) -> ModelStatus:
        return ModelStatus( self, stage )
    
    
    def has_any_tree( self ):
        return any( x.tree for x in self.components )
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self.name,
                       doc = str( self.__doc__ ),
                       type_name = "Model",
                       value = "{} sequences".format( len( self.sequences ) ),
                       colour = EColour.YELLOW,
                       icon = intermake_resources.folder,
                       extra = { "documentation"         : self.__doc__,
                                 "graphs"                : list( self.iter_graphs() ),
        
                                 "sequences"             : self.sequences,
                                 "components"            : self.components,
                                 "edges"                 : self.edges,
                                 "comments"              : self.comments,
                                 "site_type"             : self.site_type,
                                 "file_name"             : self.file_name,
                                 "fusion_events"         : self.fusion_events,
                                 "ui_options"            : self.ui_options,
                                 "user_domains"          : self.user_domains,
                                 "user_graphs"           : self.user_graphs,
                                 "splits"                : self.splits,
                                 "consensus"             : self.consensus,
                                 "fusion_graph_unclean"  : self.fusion_graph_unclean,
                                 "fusion_graph_clean"    : self.fusion_graph_clean,
                                 "report"                : self.report,
                                 "subsets"               : self.subsets,
                                 "pregraphs"             : self.iter_pregraphs(),
                                 "subgraphs"             : self.subgraphs,
                                 "subgraphs_sources"     : self.subgraphs_sources,
                                 "subgraphs_destinations": self.subgraphs_destinations,
        
                                 "results"               : MENV.host.last_results,
                                 "plugins"               : MENV.plugins.plugins() } )
    
    
    def __str__( self ):
        return self.name
    
    
    @property
    def name( self ) -> str:
        from groot.data import global_view
        if self is not global_view.current_model():
            return "Not the current model"
        
        if self.file_name:
            return FileHelper.get_filename_without_extension( self.file_name )
        elif self.sequences:
            return "Unsaved model"
        else:
            return "Empty model"
    
    
    @property
    def site_type( self ) -> ESiteType:
        """
        API
        Obtains the type of data in the model - protein, DNA or RNA.
        """
        if self.__seq_type != ESiteType.UNKNOWN:
            return self.__seq_type
        
        s = ESiteType.UNKNOWN
        
        for x in self.sequences:
            if x.site_array:
                for y in x.site_array:
                    if y not in "GAC":
                        if y == "T":
                            if s == ESiteType.UNKNOWN:
                                s = ESiteType.DNA
                        elif y == "U":
                            if s == ESiteType.UNKNOWN:
                                s = ESiteType.RNA
                        else:
                            s = ESiteType.PROTEIN
        
        self.__seq_type = s
        
        return s
    
    
    def _get_incremental_id( self ) -> int:
        """
        Obtains a unique identifier.
        """
        self.__incremental_id += 1
        return self.__incremental_id
    
    
    def _has_data( self ) -> bool:
        return bool( self.sequences )
    
    
    def find_sequence_by_accession( self, name: str ) -> LegoSequence:
        for x in self.sequences:
            if x.accession == name:
                return x
        
        raise NotFoundError( "There is no sequence with the accession «{}».".format( name ) )
    
    
    def find_sequence_by_legacy_accession( self, name: str ) -> LegoSequence:
        id = LegoSequence.read_legacy_accession( name )
        
        for x in self.sequences:
            if x.id == id:
                return x
        
        raise NotFoundError( "There is no sequence with the internal ID «{}».".format( id ) )
    
    
    def find_fusion_point_by_legacy_accession( self, name: str ) -> "LegoPoint":
        i_event, i_formation, i_point = LegoPoint.read_legacy_accession( name )
        
        for event in self.fusion_events:
            if event.index == i_event:
                for formation in event.formations:
                    if formation.index == i_formation:
                        for point in formation.points:
                            if point.index == i_point:
                                return point
        
        raise NotFoundError( "There is no fusion point with the internal ID «{}».".format( id ) )
    
    
    def find_fusion_formation_by_legacy_accession( self, name: str ) -> "LegoFormation":
        i_event, i_formation = LegoFormation.read_legacy_accession( name )
        
        for event in self.fusion_events:
            if event.index == i_event:
                for formation in event.formations:
                    if formation.index == i_formation:
                        return formation
        
        raise NotFoundError( "There is no fusion formation with the internal ID «{}».".format( id ) )
    
    
    def iter_graphs( self ):
        yield from (x.named_tree for x in self.components if x.tree is not None)
        yield from (x.named_tree_unrooted for x in self.components if x.tree_unrooted is not None)
        yield from self.subgraphs
        if self.fusion_graph_unclean:
            yield self.fusion_graph_unclean
        if self.fusion_graph_clean:
            yield self.fusion_graph_clean
        yield from self.user_graphs