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
"    QLabel        | heading               border, big, bold               section titles \n"
"    QLabel        | subheading               border, big, bold               section titles \n"
"    QTextEdit     | console             monospaced, black background    code, console output\n"
"    QPushButton   | completed           \n"
"    QPushButton   | cancel              red                             abort button\n"
"    QFrame        | header               border                          section titles\n"
"    QToolButton   | listbutton          condensed                       buttons in lists\n"
"    QLabel        | helpbox             tooltip background              help labels\n"
"*/\n"
"\n"
"QDialog\n"
"{\n"
"    background : #EEEEEE;\n"
"}\n"
"\n"
"QFrame[style=\"heading\"]\n"
"{\n"
"    background    : #C0C0C0;\n"
"    border-radius : 8px;\n"
"    padding       : 4px;\n"
"}\n"
"\n"
"QLabel[style=\"heading\"]\n"
"{\n"
"    background    : #C0C0C0;\n"
"    border-radius : 4px;\n"
"    margin        : 2px;\n"
"    padding       : 2px;\n"
"    color         : black;\n"
"    font-weight   : bold;\n"
"}\n"
"\n"
"QLabel[style=\"subheading\"]\n"
"{\n"
"    background    : #FFFFFF;\n"
"    border-radius : 4px;\n"
"    margin        : 2px;\n"
"    padding       : 2px;\n"
"    color         : black;\n"
"    font-weight   : bold;\n"
"}\n"
"\n"
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
"\n"
"QRadioButton::indicator,QCheckBox::indicator\n"
"{\n"
"background: #0080C0;\n"
"width: 16px;\n"
"height: 16px;\n"
"}\n"
"\n"
"QCheckBox::indicator\n"
"{\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QRadioButton::indicator\n"
"{\n"
"border-radius: 8px;\n"
"}\n"
"\n"
"QRadioButton::indicator:checked,QCheckBox::indicator:checked\n"
"{\n"
"background: #00C080;\n"
"image: url(:/check_yes_white.svg);\n"
"}\n"
"\n"
"QRadioButton::indicator:unchecked,QCheckBox::indicator:unchecked\n"
"{\n"
"image: none;\n"
"}\n"
"\n"
"QRadioButton::indicator:indeterminate,QCheckBox::indicator:indeterminate\n"
"{\n"
"image: url(:/check_indeterminate_white.svg);\n"
"}")
        MainWindow.setDockNestingEnabled(True)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowNestedDocks|QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.VerticalTabs)
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setChildrenCollapsible(True)
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
        icon.addPixmap(QtGui.QPixmap(":/list.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        icon1.addPixmap(QtGui.QPixmap(":/sequence.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        icon2.addPixmap(QtGui.QPixmap(":/tree.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        icon3.addPixmap(QtGui.QPixmap(":/edge.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        self.SCR_AREA.setGeometry(QtCore.QRect(0, 0, 380, 830))
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
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.BTN_VIEW_SETTINGS = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN_VIEW_SETTINGS.sizePolicy().hasHeightForWidth())
        self.BTN_VIEW_SETTINGS.setSizePolicy(sizePolicy)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_VIEW_SETTINGS.setIcon(icon4)
        self.BTN_VIEW_SETTINGS.setObjectName("BTN_VIEW_SETTINGS")
        self.horizontalLayout_2.addWidget(self.BTN_VIEW_SETTINGS)
        self.verticalLayout_6.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        spacerItem1 = QtWidgets.QSpacerItem(36, 16, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem1)
        self.BTN_SEL_COMPONENT = QtWidgets.QToolButton(self.layoutWidget)
        self.BTN_SEL_COMPONENT.setMinimumSize(QtCore.QSize(128, 0))
        self.BTN_SEL_COMPONENT.setMaximumSize(QtCore.QSize(128, 16777215))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/compartmentalise.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_SEL_COMPONENT.setIcon(icon5)
        self.BTN_SEL_COMPONENT.setCheckable(True)
        self.BTN_SEL_COMPONENT.setAutoExclusive(True)
        self.BTN_SEL_COMPONENT.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_SEL_COMPONENT.setObjectName("BTN_SEL_COMPONENT")
        self.horizontalLayout_7.addWidget(self.BTN_SEL_COMPONENT)
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
        icon6.addPixmap(QtGui.QPixmap(":/subsequence.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_SEL_SUBSEQUENCE.setIcon(icon6)
        self.BTN_SEL_SUBSEQUENCE.setCheckable(True)
        self.BTN_SEL_SUBSEQUENCE.setAutoExclusive(True)
        self.BTN_SEL_SUBSEQUENCE.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_SEL_SUBSEQUENCE.setObjectName("BTN_SEL_SUBSEQUENCE")
        self.horizontalLayout_7.addWidget(self.BTN_SEL_SUBSEQUENCE)
        self.BTN_SEL_EDGE = QtWidgets.QToolButton(self.layoutWidget)
        self.BTN_SEL_EDGE.setMinimumSize(QtCore.QSize(128, 0))
        self.BTN_SEL_EDGE.setMaximumSize(QtCore.QSize(128, 16777215))
        self.BTN_SEL_EDGE.setIcon(icon3)
        self.BTN_SEL_EDGE.setCheckable(True)
        self.BTN_SEL_EDGE.setAutoExclusive(True)
        self.BTN_SEL_EDGE.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_SEL_EDGE.setObjectName("BTN_SEL_EDGE")
        self.horizontalLayout_7.addWidget(self.BTN_SEL_EDGE)
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
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.BTN_STATUS_FILE = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN_STATUS_FILE.sizePolicy().hasHeightForWidth())
        self.BTN_STATUS_FILE.setSizePolicy(sizePolicy)
        self.BTN_STATUS_FILE.setMaximumSize(QtCore.QSize(128, 16777215))
        self.BTN_STATUS_FILE.setCheckable(True)
        self.BTN_STATUS_FILE.setObjectName("BTN_STATUS_FILE")
        self.horizontalLayout_4.addWidget(self.BTN_STATUS_FILE)
        self.BTN_STATUS_BLAST = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN_STATUS_BLAST.sizePolicy().hasHeightForWidth())
        self.BTN_STATUS_BLAST.setSizePolicy(sizePolicy)
        self.BTN_STATUS_BLAST.setMaximumSize(QtCore.QSize(128, 16777215))
        self.BTN_STATUS_BLAST.setCheckable(True)
        self.BTN_STATUS_BLAST.setObjectName("BTN_STATUS_BLAST")
        self.horizontalLayout_4.addWidget(self.BTN_STATUS_BLAST)
        self.BTN_STATUS_FASTA = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN_STATUS_FASTA.sizePolicy().hasHeightForWidth())
        self.BTN_STATUS_FASTA.setSizePolicy(sizePolicy)
        self.BTN_STATUS_FASTA.setMaximumSize(QtCore.QSize(128, 16777215))
        self.BTN_STATUS_FASTA.setCheckable(True)
        self.BTN_STATUS_FASTA.setObjectName("BTN_STATUS_FASTA")
        self.horizontalLayout_4.addWidget(self.BTN_STATUS_FASTA)
        self.BTN_STATUS_COMPONENTS = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN_STATUS_COMPONENTS.sizePolicy().hasHeightForWidth())
        self.BTN_STATUS_COMPONENTS.setSizePolicy(sizePolicy)
        self.BTN_STATUS_COMPONENTS.setMaximumSize(QtCore.QSize(128, 16777215))
        self.BTN_STATUS_COMPONENTS.setCheckable(True)
        self.BTN_STATUS_COMPONENTS.setObjectName("BTN_STATUS_COMPONENTS")
        self.horizontalLayout_4.addWidget(self.BTN_STATUS_COMPONENTS)
        self.BTN_STATUS_ALIGNMENTS = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN_STATUS_ALIGNMENTS.sizePolicy().hasHeightForWidth())
        self.BTN_STATUS_ALIGNMENTS.setSizePolicy(sizePolicy)
        self.BTN_STATUS_ALIGNMENTS.setMaximumSize(QtCore.QSize(128, 16777215))
        self.BTN_STATUS_ALIGNMENTS.setCheckable(True)
        self.BTN_STATUS_ALIGNMENTS.setObjectName("BTN_STATUS_ALIGNMENTS")
        self.horizontalLayout_4.addWidget(self.BTN_STATUS_ALIGNMENTS)
        self.BTN_STATUS_TREES = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN_STATUS_TREES.sizePolicy().hasHeightForWidth())
        self.BTN_STATUS_TREES.setSizePolicy(sizePolicy)
        self.BTN_STATUS_TREES.setMaximumSize(QtCore.QSize(128, 16777215))
        self.BTN_STATUS_TREES.setCheckable(True)
        self.BTN_STATUS_TREES.setObjectName("BTN_STATUS_TREES")
        self.horizontalLayout_4.addWidget(self.BTN_STATUS_TREES)
        self.BTN_STATUS_FUSIONS = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN_STATUS_FUSIONS.sizePolicy().hasHeightForWidth())
        self.BTN_STATUS_FUSIONS.setSizePolicy(sizePolicy)
        self.BTN_STATUS_FUSIONS.setMaximumSize(QtCore.QSize(128, 16777215))
        self.BTN_STATUS_FUSIONS.setCheckable(True)
        self.BTN_STATUS_FUSIONS.setObjectName("BTN_STATUS_FUSIONS")
        self.horizontalLayout_4.addWidget(self.BTN_STATUS_FUSIONS)
        self.BTN_STATUS_NRFG = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN_STATUS_NRFG.sizePolicy().hasHeightForWidth())
        self.BTN_STATUS_NRFG.setSizePolicy(sizePolicy)
        self.BTN_STATUS_NRFG.setMaximumSize(QtCore.QSize(128, 16777215))
        self.BTN_STATUS_NRFG.setCheckable(True)
        self.BTN_STATUS_NRFG.setObjectName("BTN_STATUS_NRFG")
        self.horizontalLayout_4.addWidget(self.BTN_STATUS_NRFG)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem4)
        self.verticalLayout_6.addLayout(self.horizontalLayout_4)
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
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
        self.menu_Modifications = QtWidgets.QMenu(self.menuBar)
        self.menu_Modifications.setObjectName("menu_Modifications")
        self.menu_View_3 = QtWidgets.QMenu(self.menuBar)
        self.menu_View_3.setObjectName("menu_View_3")
        MainWindow.setMenuBar(self.menuBar)
        self.ACT_FILE_NEW = QtWidgets.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/Images/Resources/new-file.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ACT_FILE_NEW.setIcon(icon7)
        self.ACT_FILE_NEW.setObjectName("ACT_FILE_NEW")
        self.ACT_FILE_IMPORT = QtWidgets.QAction(MainWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/Images/Resources/import-file.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ACT_FILE_IMPORT.setIcon(icon8)
        self.ACT_FILE_IMPORT.setObjectName("ACT_FILE_IMPORT")
        self.ACT_APP_EXIT = QtWidgets.QAction(MainWindow)
        self.ACT_APP_EXIT.setObjectName("ACT_APP_EXIT")
        self.ACT_FILE_SAVE = QtWidgets.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/Images/Resources/save-file.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ACT_FILE_SAVE.setIcon(icon9)
        self.ACT_FILE_SAVE.setObjectName("ACT_FILE_SAVE")
        self.ACT_FILE_OPEN = QtWidgets.QAction(MainWindow)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/Images/Resources/open-file.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ACT_FILE_OPEN.setIcon(icon10)
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
        self.ACT_FILE_SAVE_AS = QtWidgets.QAction(MainWindow)
        self.ACT_FILE_SAVE_AS.setObjectName("ACT_FILE_SAVE_AS")
        self.ACT_FILE_EXPORT = QtWidgets.QAction(MainWindow)
        self.ACT_FILE_EXPORT.setObjectName("ACT_FILE_EXPORT")
        self.ACT_SELECT_BY_NAME = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_BY_NAME.setObjectName("ACT_SELECT_BY_NAME")
        self.ACT_VIEW_ALIGN = QtWidgets.QAction(MainWindow)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/align_adjacent.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ACT_VIEW_ALIGN.setIcon(icon11)
        self.ACT_VIEW_ALIGN.setObjectName("ACT_VIEW_ALIGN")
        self.ACT_SELECT_LEFT = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_LEFT.setObjectName("ACT_SELECT_LEFT")
        self.ACT_SELECT_RIGHT = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_RIGHT.setObjectName("ACT_SELECT_RIGHT")
        self.ACT_SELECT_DIRECT_CONNECTIONS = QtWidgets.QAction(MainWindow)
        self.ACT_SELECT_DIRECT_CONNECTIONS.setObjectName("ACT_SELECT_DIRECT_CONNECTIONS")
        self.ACT_VIEW_ALIGN_SUBSEQUENCES = QtWidgets.QAction(MainWindow)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(":/align_component.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ACT_VIEW_ALIGN_SUBSEQUENCES.setIcon(icon12)
        self.ACT_VIEW_ALIGN_SUBSEQUENCES.setObjectName("ACT_VIEW_ALIGN_SUBSEQUENCES")
        self.ACT_VIEW_ALIGN_FIRST_SUBSEQUENCES = QtWidgets.QAction(MainWindow)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(":/align_left.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ACT_VIEW_ALIGN_FIRST_SUBSEQUENCES.setIcon(icon13)
        self.ACT_VIEW_ALIGN_FIRST_SUBSEQUENCES.setObjectName("ACT_VIEW_ALIGN_FIRST_SUBSEQUENCES")
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
        self.ACT_REFRESH_VIEW = QtWidgets.QAction(MainWindow)
        self.ACT_REFRESH_VIEW.setObjectName("ACT_REFRESH_VIEW")
        self.ACT_UPDATE_VIEW = QtWidgets.QAction(MainWindow)
        self.ACT_UPDATE_VIEW.setObjectName("ACT_UPDATE_VIEW")
        self.ACT_DEBUG = QtWidgets.QAction(MainWindow)
        self.ACT_DEBUG.setObjectName("ACT_DEBUG")
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
        self.menu_Modifications.addAction(self.ACT_MODIFY_CLEAN)
        self.menu_Modifications.addAction(self.ACT_MODIFY_SET_TREE)
        self.menu_Modifications.addAction(self.ACT_MODIFY_SET_ALIGNMENT)
        self.menu_Modifications.addSeparator()
        self.menu_Modifications.addAction(self.ACT_MODIFY_QUANTISE)
        self.menu_Modifications.addSeparator()
        self.menu_Modifications.addAction(self.ACT_MODIFY_NEW_ENTITY)
        self.menu_Modifications.addAction(self.ACT_MODIFY_REMOVE_ENTITY)
        self.menu_View_3.addAction(self.ACT_VIEW_ALIGN_SUBSEQUENCES)
        self.menu_View_3.addAction(self.ACT_VIEW_ALIGN)
        self.menu_View_3.addAction(self.ACT_VIEW_ALIGN_FIRST_SUBSEQUENCES)
        self.menuBar.addAction(self.menu_File.menuAction())
        self.menuBar.addAction(self.menuSelect.menuAction())
        self.menuBar.addAction(self.menu_View_3.menuAction())
        self.menuBar.addAction(self.menu_Modifications.menuAction())
        self.menuBar.addAction(self.menu_Help.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", "Data"))
        self.label.setProperty("style", _translate("MainWindow", "heading"))
        self.CHKBTN_DATA_DATA.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to BLAST viewing</p></body></html>"))
        self.CHKBTN_DATA_DATA.setText(_translate("MainWindow", "Data"))
        self.CHKBTN_DATA_FASTA.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to FASTA viewing</p></body></html>"))
        self.CHKBTN_DATA_FASTA.setText(_translate("MainWindow", "Fasta"))
        self.CHKBTN_DATA_NEWICK.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to Newick viewing</p></body></html>"))
        self.CHKBTN_DATA_NEWICK.setText(_translate("MainWindow", "Newick"))
        self.CHKBTN_DATA_BLAST.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to BLAST viewing</p></body></html>"))
        self.CHKBTN_DATA_BLAST.setText(_translate("MainWindow", "Blast"))
        self.label_3.setText(_translate("MainWindow", "Diagram"))
        self.label_3.setProperty("style", _translate("MainWindow", "heading"))
        self.BTN_SEL_COMPONENT.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to component edit mode.</p></body></html>"))
        self.BTN_SEL_COMPONENT.setText(_translate("MainWindow", "Component"))
        self.BTN_SEL_SEQUENCE.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to sequence edit mode.</p></body></html>"))
        self.BTN_SEL_SEQUENCE.setStatusTip(_translate("MainWindow", "Remove sequence"))
        self.BTN_SEL_SEQUENCE.setText(_translate("MainWindow", "Genes"))
        self.BTN_SEL_SUBSEQUENCE.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to subsequence edit mode.</p></body></html>"))
        self.BTN_SEL_SUBSEQUENCE.setStatusTip(_translate("MainWindow", "Remove (merge) splits"))
        self.BTN_SEL_SUBSEQUENCE.setText(_translate("MainWindow", "Domains"))
        self.BTN_SEL_EDGE.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to edge edit mode.</p></body></html>"))
        self.BTN_SEL_EDGE.setStatusTip(_translate("MainWindow", "Remove edge"))
        self.BTN_SEL_EDGE.setText(_translate("MainWindow", "Edge"))
        self.BTN_STATUS_FILE.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to component edit mode.</p></body></html>"))
        self.BTN_STATUS_FILE.setText(_translate("MainWindow", "MODEL"))
        self.BTN_STATUS_BLAST.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to component edit mode.</p></body></html>"))
        self.BTN_STATUS_BLAST.setText(_translate("MainWindow", "BLAST"))
        self.BTN_STATUS_FASTA.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to component edit mode.</p></body></html>"))
        self.BTN_STATUS_FASTA.setText(_translate("MainWindow", "FASTA"))
        self.BTN_STATUS_COMPONENTS.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to component edit mode.</p></body></html>"))
        self.BTN_STATUS_COMPONENTS.setText(_translate("MainWindow", "COMPONENTS"))
        self.BTN_STATUS_ALIGNMENTS.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to component edit mode.</p></body></html>"))
        self.BTN_STATUS_ALIGNMENTS.setText(_translate("MainWindow", "ALIGNMENT"))
        self.BTN_STATUS_TREES.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to component edit mode.</p></body></html>"))
        self.BTN_STATUS_TREES.setText(_translate("MainWindow", "TREES"))
        self.BTN_STATUS_FUSIONS.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to component edit mode.</p></body></html>"))
        self.BTN_STATUS_FUSIONS.setText(_translate("MainWindow", "FUSIONS"))
        self.BTN_STATUS_NRFG.setToolTip(_translate("MainWindow", "<html><head/><body><p>Switch to component edit mode.</p></body></html>"))
        self.BTN_STATUS_NRFG.setText(_translate("MainWindow", "NRFG"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.MNU_RECENT.setTitle(_translate("MainWindow", "&Recent diagrams"))
        self.MNU_EXAMPLES.setTitle(_translate("MainWindow", "&Import sample data"))
        self.menuSelect.setTitle(_translate("MainWindow", "&Edit"))
        self.menu_Help.setTitle(_translate("MainWindow", "&Help"))
        self.menu_Debug.setTitle(_translate("MainWindow", "&Debug"))
        self.menu_Modifications.setTitle(_translate("MainWindow", "&Tools"))
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
        self.ACT_SELECT_EMPTY.setText(_translate("MainWindow", "&Select items with missing site data"))
        self.ACT_SELECTION_INVERT.setText(_translate("MainWindow", "&Invert selection"))
        self.ACT_FILE_SAVE_AS.setText(_translate("MainWindow", "Save diagram &as..."))
        self.ACT_FILE_EXPORT.setText(_translate("MainWindow", "Export selected data..."))
        self.ACT_SELECT_BY_NAME.setText(_translate("MainWindow", "Select items by &name..."))
        self.ACT_VIEW_ALIGN.setText(_translate("MainWindow", "Gene-align"))
        self.ACT_SELECT_LEFT.setText(_translate("MainWindow", "Select all subsequences to the left"))
        self.ACT_SELECT_LEFT.setShortcut(_translate("MainWindow", "Ctrl+Shift+Left"))
        self.ACT_SELECT_RIGHT.setText(_translate("MainWindow", "Select all domains to the right"))
        self.ACT_SELECT_RIGHT.setShortcut(_translate("MainWindow", "Ctrl+Shift+Right"))
        self.ACT_SELECT_DIRECT_CONNECTIONS.setText(_translate("MainWindow", "Select all domains with direct connections"))
        self.ACT_SELECT_DIRECT_CONNECTIONS.setShortcut(_translate("MainWindow", "Ctrl+Shift+Up"))
        self.ACT_VIEW_ALIGN_SUBSEQUENCES.setText(_translate("MainWindow", "Component-align"))
        self.ACT_VIEW_ALIGN_FIRST_SUBSEQUENCES.setText(_translate("MainWindow", "Domain-align"))
        self.ACT_MODIFY_CLEAN.setText(_translate("MainWindow", "&Clean"))
        self.ACT_MODIFY_SET_TREE.setText(_translate("MainWindow", "Set &tree"))
        self.ACT_MODIFY_SET_ALIGNMENT.setText(_translate("MainWindow", "Set &alignment"))
        self.ACT_MODIFY_QUANTISE.setText(_translate("MainWindow", "&Quantise"))
        self.ACT_MODIFY_NEW_ENTITY.setText(_translate("MainWindow", "&New entity"))
        self.ACT_MODIFY_REMOVE_ENTITY.setText(_translate("MainWindow", "&Remove entity"))
        self.ACT_REFRESH_VIEW.setText(_translate("MainWindow", "&Refresh view"))
        self.ACT_UPDATE_VIEW.setText(_translate("MainWindow", "&Update view"))
        self.ACT_DEBUG.setText(_translate("MainWindow", "&Debug/other"))


