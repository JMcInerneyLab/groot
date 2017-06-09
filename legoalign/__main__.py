import sys

from PyQt5.QtWidgets import QApplication

from legoalign.FrmMain import FrmMain


def main( ) -> None:
    """
    Entry point
    """

    # Show the main window
    app = QApplication( sys.argv )
    #app.setStyle("Fusion")
    main_window = FrmMain( )
    main_window.show( )
    sys.exit( app.exec_( ) )


# As executable only
if __name__ == "__main__":
    main( )
