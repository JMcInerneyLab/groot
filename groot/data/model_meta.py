from typing import Optional

from groot.constants import Stage, STAGES
from groot.data.exceptions import NotReadyError, InUseError
from groot.data.model_interfaces import INamed, IHasFasta, INamedGraph
from groot.data.model_core import Component
from mgraph import MGraph


_LegoModel_ = "LegoModel"


class _ComponentAsFasta( INamed, IHasFasta ):
    def __init__( self, component: Component, is_aligned: bool ):
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
    
    
    def __init__( self, component: "Component", unrooted = False ):
        self.component = component
        self.unrooted = unrooted
    
    
    
    
    def to_fasta( self ):
        return self.component.get_aligned_fasta()
    
    
    def __str__( self ):
        return self.name


class ModelStatus:
    def __init__( self, model: _LegoModel_, stage: Stage ):
        assert isinstance( stage, Stage ), stage
        self.model: _LegoModel_ = model
        self.stage: Stage = stage
    
    
    def assert_drop( self ):
        if self.is_none:
            raise NotReadyError( "Cannot drop «{}» stage because this data does not yet exist.".format( self.stage ) )
        
        self.assert_not_in_use( "drop" )
    
    
    def assert_not_in_use( self, method ):
        for dependant_stage in STAGES:
            if self.stage in dependant_stage.requires:
                dependant_status: ModelStatus = self.model.get_status( dependant_stage )
                
                if dependant_status.is_partial:
                    raise InUseError( "Cannot {} «{}» because at least one subsequent stage, «{}», is relying on the current data. Perhaps you meant to drop that stage first?".format( method, self.stage, dependant_stage ) )
        
        return False
    
    
    def assert_import( self ):
        """
        Asserts that data for this stage can be imported.
        
        Ideally, this means we can skip earlier parts of the model, however at the present time, this is the same as `assert_create`,
        because stages only mark their immediate prerequisites and assume that all their prerequisites have themselves been met.
        """
        self.assert_create()
    
    
    def assert_set( self ):
        self.assert_create()
    
    
    def assert_create( self ):
        if self.is_complete:
            raise NotReadyError( "Cannot create «{}» stage because this data already exists.".format( self.stage ) )
        
        self.assert_not_in_use( "create" )
        
        for required_stage in self.stage.requires:
            required_status = self.model.get_status( required_stage )
            
            if required_status.is_not_complete:
                raise NotReadyError( "Cannot create «{}» because the preceding stage «{}» is not complete. Perhaps you meant to complete that stage first?".format( self.stage, required_stage ) )
    
    
    @property
    def requisite_complete( self ) -> bool:
        for requisite in self.stage.requires:
            if not ModelStatus( self.model, requisite ).is_complete:
                return False
        
        return True
    
    
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
        A stage is hot if it's not already complete but is ready to go (i.e. the preceding stage(s) are complete).
        If the stage is flagged `hot` it's assumed the stage is always ready to go.
        If the stage is flagged `cold` then it's never hot (i.e. it is assumed to be an optional part of the workflow).
        """
        if self.is_partial:
            return False
        
        if self.stage.cold:
            return False
        
        if self.stage.hot or not self.stage.requires:
            return True
        
        for req in self.stage.requires:
            if self.model.get_status( req ).is_not_complete:
                return False
        
        return True
    
    
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
