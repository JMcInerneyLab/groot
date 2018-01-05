from groot.data.lego_model import LegoSequence
from groot.frontends.cli.cli_view_utils import COMPONENT_COLOURS_ANSI_FORE, COMPONENT_COLOURS_ANSI_COUNT
from intermake.engine.environment import MCMD
from mhelper import ansi, string_helper


def sequence( seq ):
    i = ord( seq.accession[0] ) % COMPONENT_COLOURS_ANSI_COUNT
    c = COMPONENT_COLOURS_ANSI_FORE[i]
    return c + seq.accession + ansi.RESET


def graph( n, g ):
    # MCMD.progress( aΛ.to_ascii( graph_viewing.create_user_formatter(), name = "aΛ" ) )
    seqs = sorted( (x.data for x in g.nodes if x.data is not None), key = lambda x: x.accession if isinstance( x, LegoSequence ) else "zzzz" )
    MCMD.progress( "    " + n.ljust( 4 ) + ": " + str( len( seqs ) ).ljust( 4 ) + ": " + string_helper.format_array( (sequence( x ) if isinstance( x, LegoSequence ) else str( x )) for x in seqs ) )
