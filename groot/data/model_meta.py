from typing import Optional, Dict, Tuple

from groot.constants import LegoStage, STAGES
from groot.data.exceptions import NotReadyError, InUseError
from groot.data.model_interfaces import INamed, IHasFasta, INamedGraph
from groot.frontends.gui.gui_view_support import EMode
from groot.data.model_core import LegoComponent
from mgraph import MGraph
from mhelper import TTristate

_LegoModel_ = "LegoModel"

class _ComponentAsFasta( INamed, IHasFasta ):
    def __init__( self, component: LegoComponent, is_aligned: bool ):
        self.component = component
        self.is_aligned = is_aligned
    
    
    def to_fasta( self ) -> str:
        if self.is_aligned:
            return self.component.get_aligned_fasta()
        else:
            return self.component.get_unaligned_fasta()
    
    
    def __str__( self ):
        return self.name
    
    
    def on_get_name( self ):
        return "{}::{}".format( self.component, "aligned" if self.is_aligned else "unaligned" )


class _ComponentAsGraph( INamedGraph ):
    def on_get_graph( self ) -> Optional[MGraph]:
        if self.unrooted:
            return self.component.tree_unrooted
        else:
            return self.component.tree
    
    
    def on_get_name( self ) -> str:
        return "{}_{}".format( self.component, "unrooted" if self.unrooted else "tree" )
    
    
    def __init__( self, component: "LegoComponent", unrooted = False ):
        self.component = component
        self.unrooted = unrooted
    
    
    def visualisable_info( self ):
        x = self.component.visualisable_info()
        x.name = str( self )
        return x
    
    
    def to_fasta( self ):
        return self.component.get_aligned_fasta()
    
    
    def __str__( self ):
        return self.name


class LegoViewOptions:
    """
    Options on the lego view
    
    :attr y_snap:                      Snap movements to the Y axis (yes | no | when no alt)
    :attr x_snap:                      Snap movements to the X axis (yes | no | when no alt)
    :attr move_enabled:                Allow movements (yes | no | when double click)
    :attr view_piano_roll:             View piano roll (yes | no | when selected)
    :attr view_names:                  View sequence names (yes | no | when selected)
    :attr view_positions:              View domain positions (yes | no | when selected)
    :attr view_components:             View domain components (yes | no | when selected)
    :attr mode:                        Edit mode
    :attr domain_function:             Domain generator
    :attr domain_function_parameter:   Parameter passed to domain generator (domain_function dependent)
    :attr domain_positions:            Positions of the domains on the screen - maps (id, site) --> (x, y)
    """
    
    
    def __init__( self ):
        self.y_snap: TTristate = None
        self.x_snap: TTristate = None
        self.move_enabled: TTristate = None
        self.view_piano_roll: TTristate = None
        self.view_names: TTristate = True
        self.view_positions: TTristate = None
        self.view_components: TTristate = None
        self.mode = EMode.SEQUENCE
        self.domain_positions: Dict[Tuple[int, int], Tuple[int, int]] = { }


class ModelStatus:
    def __init__( self, model: _LegoModel_, stage: LegoStage ):
        self.model: _LegoModel_ = model
        self.stage: LegoStage = stage
    
    
    def assert_drop( self ):
        if self.is_none:
            raise NotReadyError( "Cannot drop «{}» stage because this data does not yet exist.".format( self.stage ) )
        
        for stage in STAGES:
            if stage.requires == self:
                raise InUseError( "Cannot drop «{}» stage the following stage, «{}» is relying on that data. Perhaps you meant to drop that stage first?".format( self.stage, stage ) )
    
    
    def assert_create( self ):
        if self.is_complete:
            raise NotReadyError( "Cannot create «{}» stage because this data already exists.".format( self.stage ) )
        
        if self.stage.requires is not None:
            req = self.model.get_status( self.stage.requires )
            
            if req.is_not_complete:
                raise NotReadyError( "Cannot create «{}» because the preceding stage «{}» is not complete. Perhaps you meant to complete that stage first?".format( self.stage, self.stage.requires ) )
    
    
    @property
    def requisite_complete( self ) -> bool:
        return self.stage.requires is None or ModelStatus( self.model, self.stage.requires ).is_complete
    
    
    def __bool__( self ):
        return self.is_complete
    
    
    def __str__( self ):
        if self.is_complete:
            return self.get_headline_text() or "(complete)"
        if self.is_partial:
            return "(partial) " + self.get_headline_text()
        else:
            return "(no data)"
    
    
    def get_headline_text( self ):
        return self.stage.headline( self.model ) if self.stage.headline is not None else ""
    
    
    @property
    def is_none( self ):
        return not self.is_partial
    
    
    @property
    def is_partial( self ):
        return any( self.get_elements() )
    
    
    @property
    def is_hot( self ):
        """
        A stage is hot if it's not already complete but is ready to go (i.e. the preceding stage is complete).
        If the stage is flagged `hot` it's assumed the stage is always ready to go.
        If the stage is flagged `cold` then it's never hot (i.e. it is assumed to be an optional part of the workflow).
        """
        if self.is_partial:
            return False
        
        if self.stage.cold:
            return False
        
        if self.stage.hot or self.stage.requires is None:
            return True
        
        pre = self.model.get_status( self.stage.requires )
        
        return pre.is_complete
    
    
    def get_elements( self ):
        r = self.stage.status( self.model )
        if r is None:
            return ()
        return r
    
    
    @property
    def is_not_complete( self ):
        return not self.is_complete
    
    
    @property
    def is_complete( self ):
        has_any = False
        
        for element in self.get_elements():
            if element:
                has_any = True
            else:
                return False
        
        return has_any