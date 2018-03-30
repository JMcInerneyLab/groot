from mhelper import file_helper


def get_path():
    return file_helper.join( file_helper.get_directory( __file__ ), "sample_data" )
