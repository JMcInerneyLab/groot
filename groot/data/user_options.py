from intermake.engine.environment import MENV


class GlobalOptions:
    """
    :data recent_files: Files recently accessed.
    """
    
    def __init__(self):
        self.recent_files = []
        
        
__global_options = None
        
def options() -> GlobalOptions:
    global __global_options
    
    if __global_options is None:
        __global_options = MENV.local_data.store.get_and_init( "lego-options", GlobalOptions() )
        
    return __global_options
        
        
def remember_file( file_name: str ) -> None:
    """
    PRIVATE
    Adds a file to the recent list
    """
    opt = options()
    
    if file_name in opt.recent_files:
        opt.recent_files.remove( file_name )
    
    opt.recent_files.append( file_name )
    
    while len( opt.recent_files ) > 10:
        del opt.recent_files[ 0 ]
    
    MENV.local_data.store["lego-options"] = opt
    
