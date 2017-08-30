from collections import defaultdict
from typing import Set, List

from ete3 import Tree, TreeNode

from legoalign.LegoModels import LegoModel, LegoComponent
from mhelper import ArrayHelper
from mhelper.LogHelper import Logger
from legoalign.algorithms import tree


__LOG = Logger("fusion", False)


class FusionEvent:
    def __init__(self, comp_a : LegoComponent, comp_b : LegoComponent, intersections : Set[LegoComponent]):
        self.component_a = comp_a
        self.component_b = comp_b
        self.intersections = intersections
        self.orig_intersections = set(intersections)
        self.point_a = None
        self.point_b = None
        
    def __str__(self):
        if self.orig_intersections == self.intersections:
            return "In the trees of {} and {} I can see the into {}.".format(self.component_a, self.component_b, "+".join(str(x) for x in self.intersections))
        else:
            return "In the trees of {} and {} I can see the into {} ({}).".format(self.component_a, self.component_b, "+".join(str(x) for x in self.intersections), "+".join(str(x) for x in self.orig_intersections))


def find_events( model: LegoModel ) -> List[FusionEvent ]:
    """
    Finds the fusion events in the model.
    """
    results = [ ]   #type: List[FusionEvent]
    
    for i, a in enumerate( model.components ):
        for b in model.components[ i + 1: ]:
            a_comps = set( a.outgoing_components() )
            b_comps = set( b.outgoing_components() )
            
            a_alone = a_comps - b_comps
            b_alone = b_comps - a_comps
            ab_ints = a_comps.intersection( b_comps )
            
            __LOG("")
            __LOG("{} {}".format(a, b))
            __LOG("A       {}".format(a_comps))
            __LOG("B       {}".format(b_comps))
            __LOG("A alone {}".format(a_alone))
            __LOG("B alone {}".format(b_alone))
            __LOG("AB toge {}".format(ab_ints))
            
            if len( a_alone ) == 1 and len( b_alone ) == 1 and len(ab_ints) >= 1:
                results.append( FusionEvent( a, b, ab_ints ) )
    
    continue_ = True
    
    while continue_:
        continue_ = False
        
        for event in results:
            if len(event.intersections) > 1:
                for event_b in results:
                    f = ArrayHelper.first(event_b.intersections)
                    if len(event_b.intersections) == 1 and f in event.intersections:
                        for component in (event_b.component_a, event_b.component_b):
                            if component in event.intersections:
                                event.intersections.remove(f)
                                continue_ = True
                                
    return results





def find_points(model:LegoModel):
    """
    Finds the fusion points in the model.
    """
    for event in find_events(model):
        event.point_a = __find_point(event.component_a, event.orig_intersections, ArrayHelper.first(event.intersections))
        event.point_b = __find_point(event.component_b, event.orig_intersections, ArrayHelper.first(event.intersections))
    
    for component in model.components:
        __find_points_2(component)


def __find_sequence( model, name ):
    if name and not name.startswith("FUSION"):
        return model.find_sequence(name)
    else:
        return None


def __find_point( component : LegoComponent,
                  lower : Set[LegoComponent],
                  fusion : object):
    """
    In the tree of `component` we look for the node separating `lower` from everything else.
    If there are multiple nodes, we consider the best match
    """
    model = component.model
    tree_ = tree.tree_from_newick(component.tree)
    viables = set()
    
    for node in tree_.traverse():
        components = set()
    
        for child in node.iter_descendants():
            sequence = __find_sequence(model, child.name)
            
            if sequence:
                components.add(sequence.component)
        
        if component in components and all(x in components for x in lower):
            # Viable
            viables.add(node)

    __simplify( viables, TreeNode.iter_descendants )
                
    print("")
    print("{} FUSIONS FOR {}".format(len(viables), component))
    
    name = "FUSION{}".format(fusion)
        
    for viable in viables:
        viable.name += name
        
    component.tree = tree_.write(format=1)
    
    return name


def __simplify( viables : List[TreeNode], accession):
    repeat = True
    while repeat:
        repeat = False
        
        for viable in viables:
            desc = set( accession(viable) )
            
            for viable_b in viables:
                if viable_b in desc:
                    viables.remove( viable )
                    repeat = True
                    break
            
            if repeat:
                break


def __find_points_2( component : LegoComponent ):
    model = component.model
    tree_ = tree.tree_from_newick(component.tree)
    viables = defaultdict(list)
    
    for node in tree_.traverse():
        group = None
        success = False
        
        for child in node.iter_descendants():
            sequence = __find_sequence(model, child.name)
            
            if sequence:
                if group is None:
                    group = sequence.component
                    success = True
                elif sequence.component is not group:
                    success = False
                    break
        
        if not success:
            continue
        
        viables[group].append(node)
        
    print("")
    print("{} GROUPS FOR {}".format(len(viables), component))
    
    for group, viables in viables.items():
        __simplify(viables, TreeNode.iter_ancestors)
        
        name = "GROUP{}".format(group)
        
        for viable in viables:
            viable.name += name
        
    component.tree = tree_.write(format=1)
        
    