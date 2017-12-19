# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_main_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1344, 964)
        MainWindow.setStyleSheet("/**\n"
"    This is the default style-sheet used by all Intermake dialogues.\n"
"    It can be retrieved via `intermake_gui.default_style_sheet()` function.\n"
"    \n"
"    Attach a string property named \"theme\" to widgets to use the unique styles listed below:\n"
"    \n"
"    WIDGET        | THEME               APPEARANCE (GUIDE)              USAGE (GUIDE)\n"
"    --------------+-------------\n"
"    QLabel        | title               border, big, bold               section titles \n"
"    QTextEdit     | console             monospaced, black background    code, console output\n"
"    QPushButton   | completed           \n"
"    QPushButton   | cancel              red                             abort button\n"
"    QFrame        | title               border                          section titles\n"
"    QToolButton   | listbutton          condensed                       buttons in lists\n"
"    QLabel        | helpbox             tooltip background              help labels\n"
"*/\n"
"\n"
"QDialog\n"
"{\n"
"    background : #808080;\n"
"}\n"
"\n"
"QLabel[style=\"title\"]\n"
"{\n"
"    background    : #FFFFFF;\n"
"    border-radius : 4px;\n"
"    margin        : 2px;\n"
"    padding       : 2px;\n"
"    color         : black;\n"
"    font-weight   : bold;\n"
"}\n"
"\n"
"QLabel[style=\"helpbox\"]\n"
"{\n"
"    background    : #FFFFD0;\n"
"}\n"
"\n"
"QToolButton\n"
"{\n"
"    background    : #0080C0;\n"
"    border-radius : 4px;\n"
"    margin        : 2px;\n"
"    padding       : 2px;\n"
"    color         : white;\n"
"    font-weight   : bold;\n"
"}\n"
"\n"
"QPushButton\n"
"{\n"
"    background    : #0080C0;\n"
"    color         : white;\n"
"    font-weight   : bold;\n"
"    padding       : 4px;\n"
"    border-color  : white;\n"
"    border-width  : 1px;\n"
"    border-radius : 8px;\n"
"}\n"
"\n"
"QTreeWidget\n"
"{\n"
"    background    : white;\n"
"    color         : black;\n"
"    border-style  : solid;\n"
"    border-width  : 1px;\n"
"    border-color  : white;\n"
"    border-radius : 8px;\n"
"}\n"
"\n"
"QTextEdit\n"
"{\n"
"    background    : white;\n"
"    color         : black;\n"
"    border-width  : 1px;\n"
"    border-color  : #00FF00;\n"
"    border-radius : 8px;\n"
"}\n"
"\n"
"QTextEdit[style=\"console\"]\n"
"{\n"
"    background : black;\n"
"    color      : white;\n"
"}\n"
"\n"
"QPushButton[style=\"completed\"]\n"
"{\n"
"    background    : #00C080;\n"
"    color         : white;\n"
"    padding       : 8px;\n"
"    border-color  : white;\n"
"    border-width  : 1px;\n"
"    border-radius : 8px;\n"
"}\n"
"\n"
"QPushButton[style=\"cancel\"]\n"
"{\n"
"    background    : #C00000;\n"
"    color         : white;\n"
"    padding       : 8px;\n"
"    border-color  : white;\n"
"    border-width  : 1px;\n"
"    border-radius : 8px;\n"
"}\n"
"\n"
"QFrame[style=\"title\"]\n"
"{\n"
"    background    : #C0C0C0;\n"
"    border-radius : 8px;\n"
"    padding       : 4px;\n"
"}\n"
"\n"
"QMenuBar\n"
"{\n"
"    background-color : #0070B0;\n"
"    color            : white;\n"
"    border-width     : 1px;\n"
"    border-style     : transparent;\n"
"    border-color     : black;\n"
"}\n"
"\n"
"QMenuBar::item\n"
"{\n"
"    background-color : #0080C0;\n"
"    color            : white;\n"
"    border-width     : 1px;\n"
"    border-style     : solid;\n"
"    border-color     : transparent;\n"
"    border-radius    : 8px;\n"
"    padding          : 2px;\n"
"    margin           : 2px;\n"
"}\n"
"\n"
"QMenu\n"
"{\n"
"    background-color : #0070B0;\n"
"    color            : white;\n"
"    border-width     : 1px;\n"
"    border-style     : transparent;\n"
"    border-color     : black;\n"
"    border-radius    : 8px;\n"
"}\n"
"\n"
"QMenu::item\n"
"{\n"
"    background-color : #0080C0;\n"
"    color            : white;\n"
"    border-width     : 1px;\n"
"    border-style     : transparent;\n"
"    border-color     : black;\n"
"    border-radius    : 8px;\n"
"    padding          : 8px;\n"
"    padding-left     : 32px;\n"
"    margin           : 1px;\n"
"}\n"
"\n"
"QMenu::item:selected\n"
"{\n"
"    background-color : #00C080;\n"
"}\n"
"\n"
"QToolButton[style=\"listbutton\"]\n"
"{\n"
"background: transparent;\n"
"border-style: outset;\n"
"border-width: 2px;\n"
"border-color: transparent;\n"
"}\n"
"\n"
"QToolButton[style=\"listbutton\"]::hover\n"
"{\n"
"background: #F0F0F0;\n"
"border-color: blue;\n"
"}\n"
"\n"
"QToolButton[style=\"listbutton\"]::pressed\n"
"{\n"
"background: #D0D0D0;\n"
"border-style: inset;\n"
"}\n"
"\n"
"QPushButton[checkable=\"true\"]:hover,QToolButton[checkable=\"true\"]:hover\n"
"{\n"
"border-width: 1px;\n"
"border-style: solid;\n"
"background: #0040C0\n"
"}\n"
"\n"
"QPushButton:checked,QToolButton:checked\n"
"{\n"
"    background : #00C000;\n"
"}\n"
"\n"
"QScrollBar\n"
"{\n"
"background: #E0E0E0;\n"
"}\n"
"\n"
"QScrollBar:vertical\n"
"{\n"
"    width: 8px;\n"
"}\n"
"\n"
"QScrollBar:horizontal\n"
"{\n"
"    height: 8px;\n"
"}\n"
"\n"
"QScrollBar::handle\n"
"{\n"
"background: #90C0D0;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical\n"
"{\n"
"min-width: 8px;\n"
"margin: 8px 0px 8px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal\n"
"{\n"
"min-height: 8px;\n"
"margin: 0px 8px 0px 8px;\n"
"}\n"
"\n"
"QScrollBar:up-arrow, QScrollBar::down-arrow, QScrollBar::left-arrow, QScrollBar::right-arrow\n"
"{\n"
"border-size: 1px;\n"
"border-radius: 4px;\n"
"width: 8px;\n"
"height: 8px;\n"
"background: #0080C0;\n"
"}\n"
"\n"
"QScrollBar::sub-line, QScrollBar::add-line\n"
"{\n"
"background: #C0C0C0;\n"
"}\n"
"")
        MainWindow.setDockNestingEnabled(True)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowNestedDocks|QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.VerticalTabs)
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter_2 = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.widget = QtWidgets.QWidget(self.splitter_2)
        self.widget.setObjectName("widget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.splitter = QtWidgets.QSplitter(self.widget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setObjectName("splitter")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_7.addWidget(self.label)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.CHKBTN_DATA_DATA = QtWidgets.QToolButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CHKBTN_DATA_DATA.sizePolicy().hasHeightForWidth())
        self.CHKBTN_DATA_DATA.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/Images/Resources/new-file.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.CHKBTN_DATA_DATA.setIcon(icon)
        self.CHKBTN_DATA_DATA.setCheckable(True)
        self.CHKBTN_DATA_DATA.setAutoExclusive(True)
        self.CHKBTN_DATA_DATA.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.CHKBTN_DATA_DATA.setAutoRaise(True)
        self.CHKBTN_DATA_DATA.setObjectName("CHKBTN_DATA_DATA")
        self.horizontalLayout.addWidget(self.CHKBTN_DATA_DATA)
        self.CHKBTN_DATA_FASTA = QtWidgets.QToolButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CHKBTN_DATA_FASTA.sizePolicy().hasHeightForWidth())
        self.CHKBTN_DATA_FASTA.setSizePolicy(sizePolicy)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/Images/Resources/sequence.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.CHKBTN_DATA_FASTA.setIcon(icon1)
        self.CHKBTN_DATA_FASTA.setCheckable(True)
        self.CHKBTN_DATA_FASTA.setChecked(True)
        self.CHKBTN_DATA_FASTA.setAutoExclusive(True)
        self.CHKBTN_DATA_FASTA.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.CHKBTN_DATA_FASTA.setAutoRaise(True)
        self.CHKBTN_DATA_FASTA.setObjectName("CHKBTN_DATA_FASTA")
        self.horizontalLayout.addWidget(self.CHKBTN_DATA_FASTA)
        self.CHKBTN_DATA_NEWICK = QtWidgets.QToolButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CHKBTN_DATA_NEWICK.sizePolicy().hasHeightForWidth())
        self.CHKBTN_DATA_NEWICK.setSizePolicy(sizePolicy)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/Images/Resources/tree.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.CHKBTN_DATA_NEWICK.setIcon(icon2)
        self.CHKBTN_DATA_NEWICK.setCheckable(True)
        self.CHKBTN_DATA_NEWICK.setAutoExclusive(True)
        self.CHKBTN_DATA_NEWICK.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.CHKBTN_DATA_NEWICK.setAutoRaise(True)
        self.CHKBTN_DATA_NEWICK.setObjectName("CHKBTN_DATA_NEWICK")
        self.horizontalLayout.addWidget(self.CHKBTN_DATA_NEWICK)
        self.CHKBTN_DATA_BLAST = QtWidgets.QToolButton(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CHKBTN_DATA_BLAST.sizePolicy().hasHeightForWidth())
        self.CHKBTN_DATA_BLAST.setSizePolicy(sizePolicy)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/Images/Resources/align.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.CHKBTN_DATA_BLAST.setIcon(icon3)
        self.CHKBTN_DATA_BLAST.setCheckable(True)
        self.CHKBTN_DATA_BLAST.setAutoExclusive(True)
        self.CHKBTN_DATA_BLAST.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.CHKBTN_DATA_BLAST.setAutoRaise(True)
        self.CHKBTN_DATA_BLAST.setObjectName("CHKBTN_DATA_BLAST")
        self.horizontalLayout.addWidget(self.CHKBTN_DATA_BLAST)
        self.horizontalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout_7.addLayout(self.horizontalLayout_3)
        self.scrollArea = QtWidgets.QScrollArea(self.verticalLayoutWidget)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.scrollArea.setPalette(palette)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.SCR_AREA = QtWidgets.QWidget()
        self.SCR_AREA.setGeometry(QtCore.QRect(0, 0, 350, 826))
        self.SCR_AREA.setObjectName("SCR_AREA")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.SCR_AREA)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.scrollArea.setWidget(self.SCR_AREA)
        self.verticalLayout_7.addWidget(self.scrollArea)
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_6.addWidget(self.label_3)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        spacerItem1 = QtWidgets.QSpacerItem(36, 16, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem1)
        self.BTN_SEL_COMPONENT = QtWidgets.QToolButton(self.layoutWidget)
        self.BTN_SEL_COMPONENT.setMinimumSize(QtCore.QSize(128, 0))
        self.BTN_SEL_COMPONENT.setMaximumSize(QtCore.QSize(128, 16777215))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/Images/Resources/compartmentalise.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_SEL_COMPONENT.setIcon(icon4)
        self.BTN_SEL_COMPONENT.setCheckable(True)
        self.BTN_SEL_COMPONENT.setAutoExclusive(True)
        self.BTN_SEL_COMPONENT.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_SEL_COMPONENT.setObjectName("BTN_SEL_COMPONENT")
        self.horizontalLayout_7.addWidget(self.BTN_SEL_COMPONENT)
        self.BTN_SEL_EDGE = QtWidgets.QToolButton(self.layoutWidget)
        self.BTN_SEL_EDGE.setMinimumSize(QtCore.QSize(128, 0))
        self.BTN_SEL_EDGE.setMaximumSize(QtCore.QSize(128, 16777215))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/Images/Resources/edge.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_SEL_EDGE.setIcon(icon5)
        self.BTN_SEL_EDGE.setCheckable(True)
        self.BTN_SEL_EDGE.setAutoExclusive(True)
        self.BTN_SEL_EDGE.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_SEL_EDGE.setObjectName("BTN_SEL_EDGE")
        self.horizontalLayout_7.addWidget(self.BTN_SEL_EDGE)
        self.BTN_SEL_SEQUENCE = QtWidgets.QToolButton(self.layoutWidget)
        self.BTN_SEL_SEQUENCE.setMinimumSize(QtCore.QSize(128, 0))
        self.BTN_SEL_SEQUENCE.setMaximumSize(QtCore.QSize(128, 16777215))
        self.BTN_SEL_SEQUENCE.setIcon(icon1)
        self.BTN_SEL_SEQUENCE.setCheckable(True)
        self.BTN_SEL_SEQUENCE.setChecked(True)
        self.BTN_SEL_SEQUENCE.setAutoExclusive(True)
        self.BTN_SEL_SEQUENCE.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_SEL_SEQUENCE.setObjectName("BTN_SEL_SEQUENCE")
        self.horizontalLayout_7.addWidget(self.BTN_SEL_SEQUENCE)
        self.BTN_SEL_SUBSEQUENCE = QtWidgets.QToolButton(self.layoutWidget)
        self.BTN_SEL_SUBSEQUENCE.setMinimumSize(QtCore.QSize(128, 0))
        self.BTN_SEL_SUBSEQUENCE.setMaximumSize(QtCore.QSize(128, 16777215))
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/Images/Resources/subsequence.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_SEL_SUBSEQUENCE.setIcon(icon6)
        self.BTN_SEL_SUBSEQUENCE.setCheckable(True)
        self.BTN_SEL_SUBSEQUENCE.setAutoExclusive(True)
        self.BTN_SEL_SUBSEQUENCE.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_SEL_SUBSEQUENCE.setObjectName("BTN_SEL_SUBSEQUENCE")
        self.horizontalLayout_7.addWidget(self.BTN_SEL_SUBSEQUENCE)
        spacerItem2 = QtWidgets.QSpacerItem(182, 16, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem2)
        self.verticalLayout_6.addLayout(self.horizontalLayout_7)
        self.FRA_MAIN = QtWidgets.QFrame(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FRA_MAIN.sizePolicy().hasHeightForWidth())
        self.FRA_MAIN.setSizePolicy(sizePolicy)
        self.FRA_MAIN.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FRA_MAIN.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FRA_MAIN.setObjectName("FRA_MAIN")
        self.verticalLayout_6.addWidget(self.FRA_MAIN)
        self.gridLayout_3.addWidget(self.splitter, 0, 0, 1, 1)
        self.verticalLayoutWidget_4 = QtWidgets.QWidget(self.splitter_2)
        self.verticalLayoutWidget_4.setObjectName("verticalLayoutWidget_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_4)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_3.addWidget(self.label_4)
        self.CHK_VIEW_NAMES = QtWidgets.QCheckBox(self.verticalLayoutWidget_4)
        self.CHK_VIEW_NAMES.setChecked(True)
        self.CHK_VIEW_NAMES.setTristate(True)
        self.CHK_VIEW_NAMES.setObjectName("CHK_VIEW_NAMES")
        self.verticalLayout_3.addWidget(self.CHK_VIEW_NAMES)
        self.CHK_VIEW_PIANO_ROLLS = QtWidgets.QCheckBox(self.verticalLayoutWidget_4)
        self.CHK_VIEW_PIANO_ROLLS.setChecked(True)
        self.CHK_VIEW_PIANO_ROLLS.setTristate(True)
        self.CHK_VIEW_PIANO_ROLLS.setObjectName("CHK_VIEW_PIANO_ROLLS")
        self.verticalLayout_3.addWidget(self.CHK_VIEW_PIANO_ROLLS)
        self.CHK_MOVE = QtWidgets.QCheckBox(self.verticalLayoutWidget_4)
        self.CHK_MOVE.setChecked(True)
        self.CHK_MOVE.setObjectName("CHK_MOVE")
        self.verticalLayout_3.addWidget(self.CHK_MOVE)
        self.CHK_VIEW_POSITIONS = QtWidgets.QCheckBox(self.verticalLayoutWidget_4)
        self.CHK_VIEW_POSITIONS.setChecked(True)
        self.CHK_VIEW_POSITIONS.setTristate(True)
        self.CHK_VIEW_POSITIONS.setObjectName("CHK_VIEW_POSITIONS")
        self.verticalLayout_3.addWidget(self.CHK_VIEW_POSITIONS)
        self.CHK_MOVE_YSNAP = QtWidgets.QCheckBox(self.verticalLayoutWidget_4)
        self.CHK_MOVE_YSNAP.setChecked(True)
        self.CHK_MOVE_YSNAP.setObjectName("CHK_MOVE_YSNAP")
        self.verticalLayout_3.addWidget(self.CHK_MOVE_YSNAP)
        self.CHK_MOVE_XSNAP = QtWidgets.QCheckBox(self.verticalLayoutWidget_4)
        self.CHK_MOVE_XSNAP.setChecked(True)
        self.CHK_MOVE_XSNAP.setObjectName("CHK_MOVE_XSNAP")
        self.verticalLayout_3.addWidget(self.CHK_MOVE_XSNAP)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem3)
        self.gridLayout.addWidget(self.splitter_2, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1344, 30))
        self.menuBar.setObjectName("menuBar")
        self.menu_File = QtWidgets.QMenu(self.menuBar)
        self.menu_File.setObjectName("menu_File")
        self.MNU_RECENT = QtWidgets.QMenu(self.menu_File)
        self.MNU_RECENT.setObjectName("MNU_RECENT")
        self.MNU_EXAMPLES = QtWidgets.QMenu(self.menu_File)
        self.MNU_EXAMPLES.setObjectName("MNU_EXAMPLES")
        self.menuSelect = QtWidgets.QMenu(self.menuBar)
        self.menuSelect.setObjectName("menuSelect")
        self.menu_Help = QtWidgets.QMenu(self.menuBar)
        self.menu_Help.setObjectName("menu_Help")
        self.menu_Debug = QtWidgets.QMenu(self.menu_Help)
        self.menu_Debug.setObjectName("menu_Debug")
        self.menu_View = QtWidgets.QMenu(self.menuBar)
        self.menu_View.setObjectName("menu_View")
        self.menu_Generating = QtWidgets.QMenu(self.menuBar)
        self.menu_Generating.setObjectName("menu_Generating")
        self.menu_Remove = QtWidgets.QMenu(self.menu_Generating)
        self.menu_Remove.setObjectName("menu_Remove")
        self.menu_Modifications = QtWidgets.QMenu(self.menuBar)
        self.menu_Modifications.setObjectName("menu_Modifications")
        self.menu_View_2 = QtWidgets.QMenu(self.menuBar)
        self.menu_View_2.setObjectName("menu_View_2")
        self.menu_2 = QtWidgets.QMenu(self.menuBar)
        self.menu_2.setTearOffEnabled(True)
        self.menu_2.setObjectName("menu_2")
        self.menu_View_3 = QtWidgets.QMenu(self.menuBar)
        self.menu_View_3.setObjectName("menu_View_3")
        MainWindow.setMenuBar(self.menuBar)
        self.ACT_FILE_NEW = QtWidgets.QAction(MainWindow)
        self.ACT_FILE_NEW.setIcon(icon)
        self.ACT_FILE_NEW.setObjectName("ACT_FILE_NEW")
        self.ACT_FILE_IMPORT = QtWidgets.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/Images/Resources/import-file.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ACT_FILE_IMPORT.setIcon(icon7)
        self.ACT_FILE_IMPORT.setObjectName("ACT_FILE_IMPORT")
        self.ACT_APP_EXIT = QtWidgets.QAction(MainWindow)
        self.ACT_APP_EXIT.setObjectName("ACT_APP_EXIT")
        self.ACT_FILE_SAVE = QtWidgets.QAction(MainWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/Images/Resources/save-file.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ACT_FILE_SAVE.setIcon(icon8)
        self.ACT_FILE_SAVE.setObjectName("ACT_FILE_SAVE")
        self.ACT_FILE_OPEN = QtWidgets.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/Images/Resources/open-file.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ACT_FILE_OPEN.setIcon(icon9)
        self.ACT_FILE_OPEN.setObjectName("ACT_FILE_OPEN")
        self.ACT_HELP_KEYS = QtWidgets.QAction(MainWindow)
        self.ACT_HELP_KEYS.setObjectName("ACT_HELP_KEYS")
        self.ACT_SELECT_ALL = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_ALL.setObjectName("ACT_SELECT_ALL")
        self.ACT_SELECT_NONE = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_NONE.setObjectName("ACT_SELECT_NONE")
        self.ACT_SELECT_EMPTY = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_EMPTY.setObjectName("ACT_SELECT_EMPTY")
        self.ACT_SELECTION_INVERT = QtWidgets.QAction(MainWindow)
        self.ACT_SELECTION_INVERT.setObjectName("ACT_SELECTION_INVERT")
        self.ACT_SELECT_SEQUENCE = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_SEQUENCE.setCheckable(True)
        self.ACT_SELECT_SEQUENCE.setChecked(True)
        self.ACT_SELECT_SEQUENCE.setObjectName("ACT_SELECT_SEQUENCE")
        self.ACT_SELECT_SUBSEQUENCE = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_SUBSEQUENCE.setCheckable(True)
        self.ACT_SELECT_SUBSEQUENCE.setObjectName("ACT_SELECT_SUBSEQUENCE")
        self.ACT_SELECT_EDGE = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_EDGE.setCheckable(True)
        self.ACT_SELECT_EDGE.setObjectName("ACT_SELECT_EDGE")
        self.ACT_SELECT_COMPONENT = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_COMPONENT.setCheckable(True)
        self.ACT_SELECT_COMPONENT.setObjectName("ACT_SELECT_COMPONENT")
        self.ACT_FILE_SAVE_AS = QtWidgets.QAction(MainWindow)
        self.ACT_FILE_SAVE_AS.setObjectName("ACT_FILE_SAVE_AS")
        self.ACT_FILE_EXPORT = QtWidgets.QAction(MainWindow)
        self.ACT_FILE_EXPORT.setObjectName("ACT_FILE_EXPORT")
        self.ACT_SELECT_BY_NAME = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_BY_NAME.setObjectName("ACT_SELECT_BY_NAME")
        self.ACT_WINDOW_VIEW = QtWidgets.QAction(MainWindow)
        self.ACT_WINDOW_VIEW.setCheckable(True)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/Images/Resources/window.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ACT_WINDOW_VIEW.setIcon(icon10)
        self.ACT_WINDOW_VIEW.setObjectName("ACT_WINDOW_VIEW")
        self.ACT_WINDOW_EDIT = QtWidgets.QAction(MainWindow)
        self.ACT_WINDOW_EDIT.setCheckable(True)
        self.ACT_WINDOW_EDIT.setIcon(icon10)
        self.ACT_WINDOW_EDIT.setObjectName("ACT_WINDOW_EDIT")
        self.ACT_WINDOW_SELECTION = QtWidgets.QAction(MainWindow)
        self.ACT_WINDOW_SELECTION.setCheckable(True)
        self.ACT_WINDOW_SELECTION.setIcon(icon10)
        self.ACT_WINDOW_SELECTION.setObjectName("ACT_WINDOW_SELECTION")
        self.ACT_VIEW_ALIGN = QtWidgets.QAction(MainWindow)
        self.ACT_VIEW_ALIGN.setObjectName("ACT_VIEW_ALIGN")
        self.ACT_SELECT_LEFT = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_LEFT.setObjectName("ACT_SELECT_LEFT")
        self.ACT_SELECT_RIGHT = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_RIGHT.setObjectName("ACT_SELECT_RIGHT")
        self.ACT_SELECT_DIRECT_CONNECTIONS = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_DIRECT_CONNECTIONS.setObjectName("ACT_SELECT_DIRECT_CONNECTIONS")
        self.ACT_VIEW_ALIGN_SUBSEQUENCES = QtWidgets.QAction(MainWindow)
        self.ACT_VIEW_ALIGN_SUBSEQUENCES.setObjectName("ACT_VIEW_ALIGN_SUBSEQUENCES")
        self.ACT_VIEW_ALIGN_FIRST_SUBSEQUENCES = QtWidgets.QAction(MainWindow)
        self.ACT_VIEW_ALIGN_FIRST_SUBSEQUENCES.setObjectName("ACT_VIEW_ALIGN_FIRST_SUBSEQUENCES")
        self.ACT_MAKE_COMPONENTS = QtWidgets.QAction(MainWindow)
        self.ACT_MAKE_COMPONENTS.setObjectName("ACT_MAKE_COMPONENTS")
        self.ACT_MAKE_ALIGNMENTS = QtWidgets.QAction(MainWindow)
        self.ACT_MAKE_ALIGNMENTS.setObjectName("ACT_MAKE_ALIGNMENTS")
        self.ACT_MAKE_TREE = QtWidgets.QAction(MainWindow)
        self.ACT_MAKE_TREE.setObjectName("ACT_MAKE_TREE")
        self.ACT_MAKE_CONSENSUS = QtWidgets.QAction(MainWindow)
        self.ACT_MAKE_CONSENSUS.setObjectName("ACT_MAKE_CONSENSUS")
        self.ACT_MAKE_NRFG = QtWidgets.QAction(MainWindow)
        self.ACT_MAKE_NRFG.setObjectName("ACT_MAKE_NRFG")
        self.ACT_MAKE_FUSIONS = QtWidgets.QAction(MainWindow)
        self.ACT_MAKE_FUSIONS.setObjectName("ACT_MAKE_FUSIONS")
        self.ACT_MODIFY_CLEAN = QtWidgets.QAction(MainWindow)
        self.ACT_MODIFY_CLEAN.setObjectName("ACT_MODIFY_CLEAN")
        self.ACT_MODIFY_SET_TREE = QtWidgets.QAction(MainWindow)
        self.ACT_MODIFY_SET_TREE.setObjectName("ACT_MODIFY_SET_TREE")
        self.ACT_MODIFY_SET_ALIGNMENT = QtWidgets.QAction(MainWindow)
        self.ACT_MODIFY_SET_ALIGNMENT.setObjectName("ACT_MODIFY_SET_ALIGNMENT")
        self.ACT_MODIFY_QUANTISE = QtWidgets.QAction(MainWindow)
        self.ACT_MODIFY_QUANTISE.setObjectName("ACT_MODIFY_QUANTISE")
        self.ACT_MODIFY_NEW_ENTITY = QtWidgets.QAction(MainWindow)
        self.ACT_MODIFY_NEW_ENTITY.setObjectName("ACT_MODIFY_NEW_ENTITY")
        self.ACT_MODIFY_REMOVE_ENTITY = QtWidgets.QAction(MainWindow)
        self.ACT_MODIFY_REMOVE_ENTITY.setObjectName("ACT_MODIFY_REMOVE_ENTITY")
        self.ACT_PRINT_FASTA = QtWidgets.QAction(MainWindow)
        self.ACT_PRINT_FASTA.setObjectName("ACT_PRINT_FASTA")
        self.ACT_PRINT_STATUS = QtWidgets.QAction(MainWindow)
        self.ACT_PRINT_STATUS.setObjectName("ACT_PRINT_STATUS")
        self.ACT_PRINT_ALIGNMENT = QtWidgets.QAction(MainWindow)
        self.ACT_PRINT_ALIGNMENT.setObjectName("ACT_PRINT_ALIGNMENT")
        self.ACT_PRINT_CONSENSUS = QtWidgets.QAction(MainWindow)
        self.ACT_PRINT_CONSENSUS.setObjectName("ACT_PRINT_CONSENSUS")
        self.ACT_PRINT_TREE = QtWidgets.QAction(MainWindow)
        self.ACT_PRINT_TREE.setObjectName("ACT_PRINT_TREE")
        self.ACT_PRINT_COMPONENT_EDGES = QtWidgets.QAction(MainWindow)
        self.ACT_PRINT_COMPONENT_EDGES.setObjectName("ACT_PRINT_COMPONENT_EDGES")
        self.ACT_PRINT_COMPONENTS = QtWidgets.QAction(MainWindow)
        self.ACT_PRINT_COMPONENTS.setObjectName("ACT_PRINT_COMPONENTS")
        self.ACT_PRINT_FUSIONS = QtWidgets.QAction(MainWindow)
        self.ACT_PRINT_FUSIONS.setObjectName("ACT_PRINT_FUSIONS")
        self.ACT_PRINT_NRFG = QtWidgets.QAction(MainWindow)
        self.ACT_PRINT_NRFG.setObjectName("ACT_PRINT_NRFG")
        self.ACTION_VIEW_MCOMMAND = QtWidgets.QAction(MainWindow)
        self.ACTION_VIEW_MCOMMAND.setObjectName("ACTION_VIEW_MCOMMAND")
        self.ACT_DROP_COMPONENTS = QtWidgets.QAction(MainWindow)
        self.ACT_DROP_COMPONENTS.setObjectName("ACT_DROP_COMPONENTS")
        self.ACT_DROP_ALIGNMENTS = QtWidgets.QAction(MainWindow)
        self.ACT_DROP_ALIGNMENTS.setObjectName("ACT_DROP_ALIGNMENTS")
        self.ACT_DROP_TREE = QtWidgets.QAction(MainWindow)
        self.ACT_DROP_TREE.setObjectName("ACT_DROP_TREE")
        self.ACT_DROP_CONSENSUS = QtWidgets.QAction(MainWindow)
        self.ACT_DROP_CONSENSUS.setObjectName("ACT_DROP_CONSENSUS")
        self.ACT_DROP_FUSIONS = QtWidgets.QAction(MainWindow)
        self.ACT_DROP_FUSIONS.setObjectName("ACT_DROP_FUSIONS")
        self.ACT_DROP_NRFG = QtWidgets.QAction(MainWindow)
        self.ACT_DROP_NRFG.setObjectName("ACT_DROP_NRFG")
        self.ACT_REFRESH_VIEW = QtWidgets.QAction(MainWindow)
        self.ACT_REFRESH_VIEW.setObjectName("ACT_REFRESH_VIEW")
        self.ACT_UPDATE_VIEW = QtWidgets.QAction(MainWindow)
        self.ACT_UPDATE_VIEW.setObjectName("ACT_UPDATE_VIEW")
        self.ACT_DEBUG = QtWidgets.QAction(MainWindow)
        self.ACT_DEBUG.setObjectName("ACT_DEBUG")
        self.ACT_CLI = QtWidgets.QAction(MainWindow)
        self.ACT_CLI.setObjectName("ACT_CLI")
        self.menu_File.addAction(self.ACT_FILE_NEW)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.ACT_FILE_OPEN)
        self.menu_File.addAction(self.MNU_RECENT.menuAction())
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.ACT_FILE_SAVE)
        self.menu_File.addAction(self.ACT_FILE_SAVE_AS)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.ACT_FILE_IMPORT)
        self.menu_File.addAction(self.MNU_EXAMPLES.menuAction())
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.ACT_FILE_EXPORT)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.ACT_APP_EXIT)
        self.menuSelect.addAction(self.ACT_SELECT_ALL)
        self.menuSelect.addAction(self.ACT_SELECT_NONE)
        self.menuSelect.addAction(self.ACT_SELECTION_INVERT)
        self.menuSelect.addSeparator()
        self.menuSelect.addAction(self.ACT_SELECT_EMPTY)
        self.menuSelect.addAction(self.ACT_SELECT_BY_NAME)
        self.menuSelect.addSeparator()
        self.menuSelect.addAction(self.ACT_SELECT_LEFT)
        self.menuSelect.addAction(self.ACT_SELECT_RIGHT)
        self.menuSelect.addAction(self.ACT_SELECT_DIRECT_CONNECTIONS)
        self.menu_Debug.addAction(self.ACT_REFRESH_VIEW)
        self.menu_Debug.addAction(self.ACT_UPDATE_VIEW)
        self.menu_Debug.addAction(self.ACT_DEBUG)
        self.menu_Help.addAction(self.ACT_HELP_KEYS)
        self.menu_Help.addAction(self.menu_Debug.menuAction())
        self.menu_View.addAction(self.ACT_WINDOW_VIEW)
        self.menu_View.addAction(self.ACT_WINDOW_EDIT)
        self.menu_View.addAction(self.ACT_WINDOW_SELECTION)
        self.menu_View.addSeparator()
        self.menu_View.addAction(self.ACTION_VIEW_MCOMMAND)
        self.menu_View.addAction(self.ACT_CLI)
        self.menu_Remove.addAction(self.ACT_DROP_COMPONENTS)
        self.menu_Remove.addAction(self.ACT_DROP_ALIGNMENTS)
        self.menu_Remove.addAction(self.ACT_DROP_TREE)
        self.menu_Remove.addAction(self.ACT_DROP_CONSENSUS)
        self.menu_Remove.addAction(self.ACT_DROP_FUSIONS)
        self.menu_Remove.addAction(self.ACT_DROP_NRFG)
        self.menu_Generating.addAction(self.ACT_MAKE_COMPONENTS)
        self.menu_Generating.addAction(self.ACT_MAKE_ALIGNMENTS)
        self.menu_Generating.addAction(self.ACT_MAKE_TREE)
        self.menu_Generating.addAction(self.ACT_MAKE_CONSENSUS)
        self.menu_Generating.addAction(self.ACT_MAKE_FUSIONS)
        self.menu_Generating.addAction(self.ACT_MAKE_NRFG)
        self.menu_Generating.addSeparator()
        self.menu_Generating.addAction(self.menu_Remove.menuAction())
        self.menu_Modifications.addAction(self.ACT_MODIFY_CLEAN)
        self.menu_Modifications.addAction(self.ACT_MODIFY_SET_TREE)
        self.menu_Modifications.addAction(self.ACT_MODIFY_SET_ALIGNMENT)
        self.menu_Modifications.addSeparator()
        self.menu_Modifications.addAction(self.ACT_MODIFY_QUANTISE)
        self.menu_Modifications.addSeparator()
        self.menu_Modifications.addAction(self.ACT_MODIFY_NEW_ENTITY)
        self.menu_Modifications.addAction(self.ACT_MODIFY_REMOVE_ENTITY)
        self.menu_View_2.addAction(self.ACT_PRINT_FASTA)
        self.menu_View_2.addAction(self.ACT_PRINT_STATUS)
        self.menu_View_2.addAction(self.ACT_PRINT_ALIGNMENT)
        self.menu_View_2.addAction(self.ACT_PRINT_CONSENSUS)
        self.menu_View_2.addAction(self.ACT_PRINT_TREE)
        self.menu_View_2.addAction(self.ACT_PRINT_COMPONENT_EDGES)
        self.menu_View_2.addAction(self.ACT_PRINT_COMPONENTS)
        self.menu_View_2.addAction(self.ACT_PRINT_FUSIONS)
        self.menu_View_2.addAction(self.ACT_PRINT_NRFG)
        self.menu_View_3.addAction(self.ACT_SELECT_COMPONENT)
        self.menu_View_3.addAction(self.ACT_SELECT_SEQUENCE)
        self.menu_View_3.addAction(self.ACT_SELECT_SUBSEQUENCE)
        self.menu_View_3.addAction(self.ACT_SELECT_EDGE)
        self.menu_View_3.addSeparator()
        self.menu_View_3.addAction(self.ACT_VIEW_ALIGN_SUBSEQUENCES)
        self.menu_View_3.addAction(self.ACT_VIEW_ALIGN)
        self.menu_View_3.addAction(self.ACT_VIEW_ALIGN_FIRST_SUBSEQUENCES)
        self.menuBar.addAction(self.menu_File.menuAction())
        self.menuBar.addAction(self.menuSelect.menuAction())
        self.menuBar.addAction(self.menu_View_3.menuAction())
        self.menuBar.addAction(self.menu_View.menuAction())
        self.menuBar.addAction(self.menu_Help.menuAction())
        self.menuBar.addAction(self.menu_2.menuAction())
        self.menuBar.addAction(self.menu_Generating.menuAction())
        self.menuBar.addAction(self.menu_Modifications.menuAction())
        self.menuBar.addAction(self.menu_View_2.menuAction())

        self.retranslateUi(MainWindow)
        self.BTN_SEL_COMPONENT.clicked.connect(self.ACT_SELECT_COMPONENT.trigger)
        self.BTN_SEL_EDGE.clicked.connect(self.ACT_SELECT_EDGE.trigger)
        self.BTN_SEL_SEQUENCE.clicked.connect(self.ACT_SELECT_SEQUENCE.trigger)
        self.BTN_SEL_SUBSEQUENCE.clicked.connect(self.ACT_SELECT_SUBSEQUENCE.trigger)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", "Data"))
        self.label.setProperty("style", _translate("MainWindow", "title"))
        self.CHKBTN_DATA_DATA.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to BLAST viewing</p></body></html>"))
        self.CHKBTN_DATA_DATA.setText(_translate("MainWindow", "Data"))
        self.CHKBTN_DATA_FASTA.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to FASTA viewing</p></body></html>"))
        self.CHKBTN_DATA_FASTA.setText(_translate("MainWindow", "Fasta"))
        self.CHKBTN_DATA_NEWICK.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to Newick viewing</p></body></html>"))
        self.CHKBTN_DATA_NEWICK.setText(_translate("MainWindow", "Newick"))
        self.CHKBTN_DATA_BLAST.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to BLAST viewing</p></body></html>"))
        self.CHKBTN_DATA_BLAST.setText(_translate("MainWindow", "Blast"))
        self.label_3.setText(_translate("MainWindow", "Diagram"))
        self.label_3.setProperty("style", _translate("MainWindow", "title"))
        self.BTN_SEL_COMPONENT.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to component edit mode.</p></body></html>"))
        self.BTN_SEL_COMPONENT.setText(_translate("MainWindow", "Component"))
        self.BTN_SEL_EDGE.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to edge edit mode.</p></body></html>"))
        self.BTN_SEL_EDGE.setStatusTip(_translate("MainWindow", "Remove edge"))
        self.BTN_SEL_EDGE.setText(_translate("MainWindow", "Edge"))
        self.BTN_SEL_SEQUENCE.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to sequence edit mode.</p></body></html>"))
        self.BTN_SEL_SEQUENCE.setStatusTip(_translate("MainWindow", "Remove sequence"))
        self.BTN_SEL_SEQUENCE.setText(_translate("MainWindow", "Sequence"))
        self.BTN_SEL_SUBSEQUENCE.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to subsequence edit mode.</p></body></html>"))
        self.BTN_SEL_SUBSEQUENCE.setStatusTip(_translate("MainWindow", "Remove (merge) splits"))
        self.BTN_SEL_SUBSEQUENCE.setText(_translate("MainWindow", "Subsequence"))
        self.label_4.setText(_translate("MainWindow", "View"))
        self.label_4.setProperty("style", _translate("MainWindow", "title"))
        self.CHK_VIEW_NAMES.setToolTip(_translate("MainWindow", "<html><head/><body><p>View sequence names (<span style=\" font-style:italic;\">yes</span> | <span style=\" font-style:italic;\">no</span> | <span style=\" font-style:italic;\">when-selected</span>)</p></body></html>"))
        self.CHK_VIEW_NAMES.setText(_translate("MainWindow", "Names"))
        self.CHK_VIEW_PIANO_ROLLS.setToolTip(_translate("MainWindow", "<html><head/><body><p>View sequence data as piano rolls (<span style=\" font-style:italic;\">yes</span> | <span style=\" font-style:italic;\">no</span> | <span style=\" font-style:italic;\">when-selected</span>)</p></body></html>"))
        self.CHK_VIEW_PIANO_ROLLS.setText(_translate("MainWindow", "Piano rolls"))
        self.CHK_MOVE.setToolTip(_translate("MainWindow", "<html><head/><body><p>Enable movement of elements using the mouse (<span style=\" font-style:italic;\">yes</span> | <span style=\" font-style:italic;\">no</span>).</p><p><span style=\" font-weight:600;\">Note: Double-click the diagram to toggle this option.</span></p></body></html>"))
        self.CHK_MOVE.setText(_translate("MainWindow", "Enable movement"))
        self.CHK_VIEW_POSITIONS.setToolTip(_translate("MainWindow", "<html><head/><body><p>View split positions (<span style=\" font-style:italic;\">yes</span> | <span style=\" font-style:italic;\">no</span> | <span style=\" font-style:italic;\">when-selected</span>)</p></body></html>"))
        self.CHK_VIEW_POSITIONS.setText(_translate("MainWindow", "Positions"))
        self.CHK_MOVE_YSNAP.setToolTip(_translate("MainWindow", "<html><head/><body><p>When moving elements using the mouse, snap to the vertical grid (<span style=\" font-style:italic;\">yes</span> | <span style=\" font-style:italic;\">no</span>).</p></body></html>"))
        self.CHK_MOVE_YSNAP.setText(_translate("MainWindow", "Y-snap"))
        self.CHK_MOVE_XSNAP.setToolTip(_translate("MainWindow", "<html><head/><body><p>When moving elements using the mouse, snap horizontally to nearby boundaries (<span style=\" font-style:italic;\">yes</span> | <span style=\" font-style:italic;\">no</span>).</p></body></html>"))
        self.CHK_MOVE_XSNAP.setText(_translate("MainWindow", "X-snap"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.MNU_RECENT.setTitle(_translate("MainWindow", "&Recent diagrams"))
        self.MNU_EXAMPLES.setTitle(_translate("MainWindow", "&Import sample data"))
        self.menuSelect.setTitle(_translate("MainWindow", "&Edit"))
        self.menu_Help.setTitle(_translate("MainWindow", "&Help"))
        self.menu_Debug.setTitle(_translate("MainWindow", "&Debug"))
        self.menu_View.setTitle(_translate("MainWindow", "&Window"))
        self.menu_Generating.setTitle(_translate("MainWindow", "&Generating"))
        self.menu_Remove.setTitle(_translate("MainWindow", "&Remove"))
        self.menu_Modifications.setTitle(_translate("MainWindow", "&Modifications"))
        self.menu_View_2.setTitle(_translate("MainWindow", "&Display"))
        self.menu_2.setTitle(_translate("MainWindow", "|"))
        self.menu_View_3.setTitle(_translate("MainWindow", "&View"))
        self.ACT_FILE_NEW.setText(_translate("MainWindow", "&New diagram"))
        self.ACT_FILE_NEW.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.ACT_FILE_IMPORT.setText(_translate("MainWindow", "&Import custom data..."))
        self.ACT_FILE_IMPORT.setShortcut(_translate("MainWindow", "Ctrl+I"))
        self.ACT_APP_EXIT.setText(_translate("MainWindow", "E&xit program"))
        self.ACT_APP_EXIT.setShortcut(_translate("MainWindow", "Ctrl+Q"))
        self.ACT_FILE_SAVE.setText(_translate("MainWindow", "&Save diagram..."))
        self.ACT_FILE_SAVE.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.ACT_FILE_OPEN.setText(_translate("MainWindow", "&Open diagram..."))
        self.ACT_FILE_OPEN.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.ACT_HELP_KEYS.setText(_translate("MainWindow", "&Keys"))
        self.ACT_HELP_KEYS.setShortcut(_translate("MainWindow", "F1"))
        self.ACT_SELECT_ALL.setText(_translate("MainWindow", "Select &all"))
        self.ACT_SELECT_NONE.setText(_translate("MainWindow", "Select &none"))
        self.ACT_SELECT_EMPTY.setText(_translate("MainWindow", "&Select items missing sequence data"))
        self.ACT_SELECTION_INVERT.setText(_translate("MainWindow", "&Invert selection"))
        self.ACT_SELECT_SEQUENCE.setText(_translate("MainWindow", "Sequence mode"))
        self.ACT_SELECT_SUBSEQUENCE.setText(_translate("MainWindow", "Subsequence mode"))
        self.ACT_SELECT_EDGE.setText(_translate("MainWindow", "Edge mode"))
        self.ACT_SELECT_COMPONENT.setText(_translate("MainWindow", "Component mode"))
        self.ACT_FILE_SAVE_AS.setText(_translate("MainWindow", "Save diagram &as..."))
        self.ACT_FILE_EXPORT.setText(_translate("MainWindow", "Export selected data..."))
        self.ACT_SELECT_BY_NAME.setText(_translate("MainWindow", "Select items by &name"))
        self.ACT_WINDOW_VIEW.setText(_translate("MainWindow", "Settings panel"))
        self.ACT_WINDOW_EDIT.setText(_translate("MainWindow", "Mode panel"))
        self.ACT_WINDOW_SELECTION.setText(_translate("MainWindow", "Data panel"))
        self.ACT_VIEW_ALIGN.setText(_translate("MainWindow", "Align component starts to selected sequence"))
        self.ACT_SELECT_LEFT.setText(_translate("MainWindow", "Select all subsequences to the left"))
        self.ACT_SELECT_LEFT.setShortcut(_translate("MainWindow", "Ctrl+Shift+Left"))
        self.ACT_SELECT_RIGHT.setText(_translate("MainWindow", "Select all subsequences to the right"))
        self.ACT_SELECT_RIGHT.setShortcut(_translate("MainWindow", "Ctrl+Shift+Right"))
        self.ACT_SELECT_DIRECT_CONNECTIONS.setText(_translate("MainWindow", "Select all subsequences with direct connections"))
        self.ACT_SELECT_DIRECT_CONNECTIONS.setShortcut(_translate("MainWindow", "Ctrl+Shift+Up"))
        self.ACT_VIEW_ALIGN_SUBSEQUENCES.setText(_translate("MainWindow", "Align subsequences to previous sibilings"))
        self.ACT_VIEW_ALIGN_FIRST_SUBSEQUENCES.setText(_translate("MainWindow", "Align first subsequences"))
        self.ACT_MAKE_COMPONENTS.setText(_translate("MainWindow", "Make &components"))
        self.ACT_MAKE_ALIGNMENTS.setText(_translate("MainWindow", "Make &alignments"))
        self.ACT_MAKE_TREE.setText(_translate("MainWindow", "Make &tree"))
        self.ACT_MAKE_CONSENSUS.setText(_translate("MainWindow", "Make con&sensus"))
        self.ACT_MAKE_NRFG.setText(_translate("MainWindow", "Make &NRFG"))
        self.ACT_MAKE_FUSIONS.setText(_translate("MainWindow", "Make &fusions"))
        self.ACT_MODIFY_CLEAN.setText(_translate("MainWindow", "&Clean"))
        self.ACT_MODIFY_SET_TREE.setText(_translate("MainWindow", "Set &tree"))
        self.ACT_MODIFY_SET_ALIGNMENT.setText(_translate("MainWindow", "Set &alignment"))
        self.ACT_MODIFY_QUANTISE.setText(_translate("MainWindow", "&Quantise"))
        self.ACT_MODIFY_NEW_ENTITY.setText(_translate("MainWindow", "&New entity"))
        self.ACT_MODIFY_REMOVE_ENTITY.setText(_translate("MainWindow", "&Remove entity"))
        self.ACT_PRINT_FASTA.setText(_translate("MainWindow", "View &FASTA"))
        self.ACT_PRINT_STATUS.setText(_translate("MainWindow", "View &status"))
        self.ACT_PRINT_ALIGNMENT.setText(_translate("MainWindow", "&View alignment"))
        self.ACT_PRINT_CONSENSUS.setText(_translate("MainWindow", "&View consensus"))
        self.ACT_PRINT_TREE.setText(_translate("MainWindow", "View &tree"))
        self.ACT_PRINT_COMPONENT_EDGES.setText(_translate("MainWindow", "View component &edges"))
        self.ACT_PRINT_COMPONENTS.setText(_translate("MainWindow", "View &components"))
        self.ACT_PRINT_FUSIONS.setText(_translate("MainWindow", "View fusions"))
        self.ACT_PRINT_NRFG.setText(_translate("MainWindow", "View NRF&G"))
        self.ACTION_VIEW_MCOMMAND.setText(_translate("MainWindow", "&Intermake..."))
        self.ACT_DROP_COMPONENTS.setText(_translate("MainWindow", "Drop components"))
        self.ACT_DROP_ALIGNMENTS.setText(_translate("MainWindow", "Drop alignments"))
        self.ACT_DROP_TREE.setText(_translate("MainWindow", "Drop tree"))
        self.ACT_DROP_CONSENSUS.setText(_translate("MainWindow", "Drop consensus"))
        self.ACT_DROP_FUSIONS.setText(_translate("MainWindow", "Drop fusions"))
        self.ACT_DROP_NRFG.setText(_translate("MainWindow", "Drop NRFG"))
        self.ACT_REFRESH_VIEW.setText(_translate("MainWindow", "&Refresh view"))
        self.ACT_UPDATE_VIEW.setText(_translate("MainWindow", "&Update view"))
        self.ACT_DEBUG.setText(_translate("MainWindow", "&Debug/other"))
        self.ACT_CLI.setText(_translate("MainWindow", "&CLI"))


