from groot.algorithms.alignment import register_algorithm
from groot.data.lego_model import LegoModel
from mhelper import file_helper, ignore
from intermake import subprocess_helper


@register_algorithm
def align_muscle( model: LegoModel, fasta: str ) -> str:
    """
    Uses MUSCLE to align.
    """
    ignore( model )
    
    file_helper.write_all_text( "in_file.fasta", fasta )
    
    subprocess_helper.run_subprocess( "muscle -in in_file.fasta -out out_file.fasta".split( " " ) )
    
    return file_helper.read_all_text( "out_file.fasta" )


@register_algorithm
def align_as_is( model: LegoModel, fasta: str ) -> str:
    """
    Uses the FASTA as it already is.
    """
    ignore( model )
    return fasta
