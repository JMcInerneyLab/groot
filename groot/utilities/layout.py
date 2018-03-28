"""
For creating a layout on the main view.
"""

from groot.frontends.gui.gui_view import LegoView_UserDomain


def align_about_domain( target_userdomain_view: LegoView_UserDomain ) -> None:
    """
    Repositions all domains in the same component to be in line with the specified domain.
    """
    model_view = target_userdomain_view.owner_sequence_view.owner_model_view
    
    target_components = set( target_userdomain_view.components )
    
    for sequence_view in model_view.sequence_views.values():
        l = sequence_view.get_sorted_userdomain_views()
        for userdomain_view in l:
            s = set( userdomain_view.components )
            if all( x in s for x in target_components ):
                userdomain_view.setX( target_userdomain_view.x() )
                userdomain_view.save_state()
                align_about( userdomain_view, relaxed = True )
                break


def align_about( userdomain_view: LegoView_UserDomain, left = True, right = True, relaxed = False ):
    """
    Aligns the elements of a sequence, fixing the position of the specified domain.
    
    :param userdomain_view:     Fixed domain
    :param left:                Align predecessors 
    :param right:               Align successors 
    :param relaxed:             Only align if not aligning would make the sequences out of order
    """
    if left:
        op = userdomain_view.sibling_previous
        
        while op:
            m = op.sibling_next.x() - op.rect.width()
            
            if not relaxed or op.x() > m:
                op.setX( m )
                op.save_state()
            
            op = op.sibling_previous
    
    if right:
        op = userdomain_view.sibling_next
        
        while op:
            m = op.sibling_previous.x() + op.sibling_previous.rect.width()
            
            if not relaxed or op.x() < m:
                op.setX( m )
                op.save_state()
            
            op = op.sibling_next
