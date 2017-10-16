from typing import Optional

from PyQt5.QtWidgets import QMessageBox

from legoalign.data.lego_model import LegoSequence, LegoEdge, LegoSubsequence


def view_sequence_details( frm_main, s: Optional[ LegoSequence ] ):
    if not s:
        return
    
    S = "<h2>"
    E = "</h2>"
    L = "<br/>"
    
    details = [ ]
    details.append( S + "ACCESSION" + E )
    details.append( s.accession )
    details.append( L )
    details.append( S + "SUBSEQUENCES" + E )
    details.append( s.subsequences )
    details.append( L )
    details.append( S + "LENGTH" + E )
    details.append( s.length )
    details.append( L )
    details.append( S + "ARRAY" + E )
    details.append( s.site_array )
    details.append( L )
    details.append( S + "META" + E )
    details.append( "<br/>".join( str( x ) for x in s.comments ) )
    
    b = QMessageBox(frm_main)
    b.setText( "SEQUENCE '{}'".format( s ) )
    b.setInformativeText( "".join( str( x ) for x in details ) )
    b.exec_()


def view_edge_details( frm_main, s: Optional[ LegoEdge ] ):
    if not s:
        return
    
    S = "<h2>"
    E = "</h2>"
    L = "<br/>"
    
    details = [ ]
    details.append( S + "SOURCE" + E )
    details.append( "{}[{}:{}" + E.format( s.left.sequence, s.left.start, s.left.end ) )
    details.append( L )
    details.append( S + "DESTINATION" + E )
    details.append( "{}[{}:{}" + E.format( s.right.sequence, s.right.start, s.right.end ) )
    details.append( L )
    details.append( S + "SOURCES" + E )
    details.append( s.left )
    details.append( L )
    details.append( S + "DESTINATIONS" + E )
    details.append( s.right )
    details.append( L )
    details.append( S + "META" + E )
    details.append( "\n".join( str( x ) for x in s.comments ) )
    details.append( L )
    
    b = QMessageBox(frm_main)
    b.setText( "EDGE '{}'".format( s ) )
    b.setInformativeText( "\n".join( str( x ) for x in details ) )
    b.exec_()


def view_subsequence_details( frm_main, s: Optional[ LegoSubsequence ] ):
    if not s:
        return
    
    S = "<h2>"
    E = "</h2>"
    L = "<br/>"
    
    details = [ ]
    details.append( S + "SEQUENCE" + E )
    details.append( s.sequence.accession )
    details.append( L )
    details.append( S + "START" + E )
    details.append( s.start )
    details.append( L )
    details.append( S + "END" + E )
    details.append( s.end )
    details.append( L )
    details.append( S + "EDGES" + E )
    details.append( s.edges )
    details.append( L )
    details.append( S + "UI POSITION" + E )
    details.append( s.ui_position )
    details.append( L )
    details.append( S + "UI COLOUR" + E )
    details.append( s.ui_colour )
    details.append( L )
    details.append( S + "ARRAY" + E )
    details.append( s.site_array )
    details.append( L )
    details.append( S + "META" + E )
    details.append( s.comments )
    details.append( L )
    
    b = QMessageBox(frm_main)
    b.setText( "SUBSEQUENCE '{}'".format( s ) )
    b.setInformativeText( "\n".join( str( x ) for x in details ) )
    b.exec_()
    