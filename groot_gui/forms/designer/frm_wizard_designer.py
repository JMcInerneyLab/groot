# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot_gui/forms/designer/frm_wizard_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1018, 604)
        Dialog.setStyleSheet("/**\n"
"    PURPOSE:\n"
"        This is the default style-sheet used by all Intermake dialogues.\n"
"        It needs to be processed by intermake_gui.py before it can be used. \n"
"        It can be retrieved in processed form by the `intermake_gui.default_style_sheet()` function.\n"
"\n"
"    USAGE:    \n"
"        You can replace this stylesheet with your own.\n"
"        If you blank the contents of this stylesheet, the OSs default controls will be used.\n"
"        If you delete this stylesheet, the program will crash.\n"
"        \n"
"    EXTENSIONS:\n"
"        Normally not permitted in Qt, the following values are read through Intermake.\n"
"            * #DEFINE X Y                    - replaces all text `X` with `Y`\n"
"            * #WHEN X Y Z                    - only executes the following lines if the current\n"
"                                               section is any of `X` `Y` or `Z`.\n"
"                                               The section is specified when the user selects a\n"
"                                               stylesheet.\n"
"            * `QApplication.style`           - one of the Qt styles\n"
"            * `QApplication.small_icon_size` - the menu icon size, permitted only if `style` is set\n"
"            * `QMdiArea.background`          - colour of the Mdi area\n"
"\n"
"    DETAILS:\n"
"        Follow standard Qt stylesheet guidelines.\n"
"        \n"
"        The `:root` section defines constants that may be used elsewhere. These constants are\n"
"        substituted during the the processing stage and the `:root` section is removed.\n"
"        \n"
"        Intermake controls may have a string property named \"theme\" assigned to to certain widgets.\n"
"        This specifies that a unique appearance for the widget is intended:\n"
"        \n"
"        WIDGET        | THEME             | APPEARANCE (GUIDE)            | USAGE (GUIDE)\n"
"        --------------+-------------------+-------------------------------+-------------------------------\n"
"        QLabel        | heading           | border, big, bold             | section titles \n"
"        QLabel        | subheading        | border, big, bold             | section titles \n"
"        QTextEdit     | console           | monospaced, black background  | code, console output\n"
"        QPushButton   | completed         |                               |\n"
"        QPushButton   | cancel            | red                           | abort button\n"
"        QFrame        | header            | border                        | section titles\n"
"        QToolButton   | listbutton        | condensed                     | buttons in lists\n"
"        QLabel        | helpbox           | tooltip background            | help labels\n"
"        QLabel        | icon              | background suitable for image | label showing an icon\n"
"        QLabel        | warning           | yellow background, red text   | warning messages     \n"
"        QMdiArea      | empty             | darker                        | when MDI area has no windows\n"
"*/\n"
"\n"
"\n"
"\n"
"QToolButton[style=\"listbutton\"]\n"
"{\n"
"    background   : #40C0FF;\n"
"    border-style : outset;\n"
"    border-width : 2px;\n"
"    border-color : transparent;\n"
"}\n"
"\n"
"QToolButton[style=\"listbutton\"]::hover\n"
"{\n"
"    background   : #B0D5E8;\n"
"    border-color : blue;\n"
"}\n"
"\n"
"QToolButton[style=\"listbutton\"]::pressed\n"
"{\n"
"    background   : #0040C0;\n"
"    border-style : inset;\n"
"}\n"
"\n"
"QLabel[style=\"icon\"]\n"
"{\n"
"    background    : #EEEEEE;\n"
"    border-radius : 8px;\n"
"}\n"
"\n"
"QFrame[style=\"title\"]\n"
"{\n"
"    margin-top     : 16px;\n"
"    margin-bottom  : 4px;\n"
"    margin-left    : 0px;\n"
"    margin-right   : 0px;\n"
"    border-radius  : 0px;\n"
"    border-bottom  : 2px solid silver;\n"
"    border-left    : none;\n"
"    border-right   : none;\n"
"    border-top     : none;\n"
"    padding-top    : 2px;\n"
"    padding-bottom : 2px;\n"
"    padding-left   : -4px;\n"
"    padding-right  : 0px;\n"
"    color          : black;\n"
"    font-size      : 18px;\n"
"}\n"
"\n"
"QLabel[style=\"title\"], QFrame[style=\"title\"]\n"
"{\n"
"    background    : #EEEEEE;\n"
"    border-radius : 4px;\n"
"    margin        : 2px;\n"
"    padding       : 2px;\n"
"    color         : black;\n"
"    font-size     : 18px;\n"
"}\n"
"\n"
"QLabel[style=\"title-embeded\"]\n"
"{\n"
"    background : #EEEEEE;\n"
"    color      : black;\n"
"    font-size  : 18px;\n"
"}\n"
"\n"
"\n"
"\n"
"\n"
"QLabel[style=\"helpbox\"]\n"
"{\n"
"    background    : transparent;\n"
"    color         : steelblue;\n"
"    padding       : 2px;\n"
"    border-radius : 4px;\n"
"}\n"
"\n"
"QLabel[style=\"subheading\"]\n"
"{\n"
"    font-weight: bold;\n"
"    font-style: italic;\n"
"}\n"
"\n"
"QLabel[style=\"heading\"], QPushButton[style=\"heading\"]\n"
"{\n"
"    font-weight: bold;\n"
"    border-bottom  : 1px solid #404040;\n"
"    border-left    : none;\n"
"    border-right   : none;\n"
"    border-top     : none;\n"
"    color: #404040;\n"
"}\n"
"\n"
"\n"
"QTextEdit[style=\"console\"]\n"
"{\n"
"    font-family: \"Consolas\", monospace;\n"
"    background : black;\n"
"    color      : white;\n"
"}\n"
"\n"
"QTextEdit[style=\"monospaced\"]\n"
"{\n"
"    font-family: \"Consolas\", monospace;\n"
"}\n"
"\n"
"QPushButton[style=\"completed\"]\n"
"{\n"
"    background    : #00C080;\n"
"    border-color  : #00C080; \n"
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
"QMdiArea[style=\"empty\"]\n"
"{\n"
"    background : #7DA3ED;\n"
"}\n"
"\n"
"QLabel[style=\"warning\"]\n"
"{\n"
"    background       : #FFFFD0;\n"
"    padding          : 8px;\n"
"    border-radius    : 8px;\n"
"    image            : url(\":/warning.svg\");\n"
"    image-position   : left;\n"
"    qproperty-indent : 24;\n"
"}\n"
"\n"
"QToolButton[style=\"dropdown\"]\n"
"{\n"
"    qproperty-toolButtonStyle : ToolButtonTextBesideIcon;\n"
"    qproperty-icon            : url(:/dropdown.svg);\n"
"}\n"
"\n"
"QToolButton[style=\"refresh\"]\n"
"{\n"
"    qproperty-toolButtonStyle : ToolButtonTextBesideIcon;\n"
"    qproperty-icon            : url(:/refresh.svg);\n"
"}\n"
"")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_9 = QtWidgets.QLabel(Dialog)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_3.addWidget(self.label_9)
        self.LBL_WRN_ACTIVE = QtWidgets.QLabel(Dialog)
        self.LBL_WRN_ACTIVE.setObjectName("LBL_WRN_ACTIVE")
        self.verticalLayout_3.addWidget(self.LBL_WRN_ACTIVE)
        self.LBL_WRN_MODEL = QtWidgets.QLabel(Dialog)
        self.LBL_WRN_MODEL.setObjectName("LBL_WRN_MODEL")
        self.verticalLayout_3.addWidget(self.LBL_WRN_MODEL)
        self.stackedWidget = QtWidgets.QStackedWidget(Dialog)
        self.stackedWidget.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.stackedWidget.setObjectName("stackedWidget")
        self.PAGE_INTRO = QtWidgets.QWidget()
        self.PAGE_INTRO.setObjectName("PAGE_INTRO")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.PAGE_INTRO)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.LBL_HELP_TITLE = QtWidgets.QLabel(self.PAGE_INTRO)
        self.LBL_HELP_TITLE.setObjectName("LBL_HELP_TITLE")
        self.verticalLayout_4.addWidget(self.LBL_HELP_TITLE)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.stackedWidget.addWidget(self.PAGE_INTRO)
        self.PAGE_NAME = QtWidgets.QWidget()
        self.PAGE_NAME.setObjectName("PAGE_NAME")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.PAGE_NAME)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_15 = QtWidgets.QLabel(self.PAGE_NAME)
        self.label_15.setObjectName("label_15")
        self.verticalLayout_2.addWidget(self.label_15)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_12 = QtWidgets.QLabel(self.PAGE_NAME)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_2.addWidget(self.label_12)
        self.BTN_RECENT = QtWidgets.QPushButton(self.PAGE_NAME)
        self.BTN_RECENT.setAutoDefault(False)
        self.BTN_RECENT.setObjectName("BTN_RECENT")
        self.horizontalLayout_2.addWidget(self.BTN_RECENT)
        self.BTN_SAVE = QtWidgets.QPushButton(self.PAGE_NAME)
        self.BTN_SAVE.setAutoDefault(False)
        self.BTN_SAVE.setObjectName("BTN_SAVE")
        self.horizontalLayout_2.addWidget(self.BTN_SAVE)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.label_7 = QtWidgets.QLabel(self.PAGE_NAME)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_2.addWidget(self.label_7)
        self.label_10 = QtWidgets.QLabel(self.PAGE_NAME)
        self.label_10.setObjectName("label_10")
        self.verticalLayout_2.addWidget(self.label_10)
        self.TXT_FILENAME = QtWidgets.QLineEdit(self.PAGE_NAME)
        self.TXT_FILENAME.setObjectName("TXT_FILENAME")
        self.verticalLayout_2.addWidget(self.TXT_FILENAME)
        self.CHK_SAVE = QtWidgets.QCheckBox(self.PAGE_NAME)
        self.CHK_SAVE.setMinimumSize(QtCore.QSize(128, 0))
        self.CHK_SAVE.setChecked(True)
        self.CHK_SAVE.setObjectName("CHK_SAVE")
        self.verticalLayout_2.addWidget(self.CHK_SAVE)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.stackedWidget.addWidget(self.PAGE_NAME)
        self.PAGE_DATA = QtWidgets.QWidget()
        self.PAGE_DATA.setObjectName("PAGE_DATA")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.PAGE_DATA)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_8 = QtWidgets.QLabel(self.PAGE_DATA)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_5.addWidget(self.label_8)
        self.label_11 = QtWidgets.QLabel(self.PAGE_DATA)
        self.label_11.setObjectName("label_11")
        self.verticalLayout_5.addWidget(self.label_11)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem2, 2, 1, 1, 1)
        self.BTN_REMOVE_FILE = QtWidgets.QPushButton(self.PAGE_DATA)
        self.BTN_REMOVE_FILE.setAutoDefault(False)
        self.BTN_REMOVE_FILE.setObjectName("BTN_REMOVE_FILE")
        self.gridLayout_3.addWidget(self.BTN_REMOVE_FILE, 1, 1, 1, 1)
        self.BTN_ADD_FILE = QtWidgets.QPushButton(self.PAGE_DATA)
        self.BTN_ADD_FILE.setAutoDefault(False)
        self.BTN_ADD_FILE.setObjectName("BTN_ADD_FILE")
        self.gridLayout_3.addWidget(self.BTN_ADD_FILE, 0, 1, 1, 1)
        self.BTN_SAMPLES = QtWidgets.QPushButton(self.PAGE_DATA)
        self.BTN_SAMPLES.setAutoDefault(False)
        self.BTN_SAMPLES.setObjectName("BTN_SAMPLES")
        self.gridLayout_3.addWidget(self.BTN_SAMPLES, 3, 1, 1, 1)
        self.LST_FILES = QtWidgets.QTreeWidget(self.PAGE_DATA)
        self.LST_FILES.setObjectName("LST_FILES")
        self.LST_FILES.headerItem().setText(0, "1")
        self.LST_FILES.header().setVisible(False)
        self.gridLayout_3.addWidget(self.LST_FILES, 0, 0, 4, 1)
        self.verticalLayout_5.addLayout(self.gridLayout_3)
        self.stackedWidget.addWidget(self.PAGE_DATA)
        self.PAGE_METHODS = QtWidgets.QWidget()
        self.PAGE_METHODS.setObjectName("PAGE_METHODS")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.PAGE_METHODS)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_19 = QtWidgets.QLabel(self.PAGE_METHODS)
        self.label_19.setObjectName("label_19")
        self.verticalLayout.addWidget(self.label_19)
        self.label_13 = QtWidgets.QLabel(self.PAGE_METHODS)
        self.label_13.setObjectName("label_13")
        self.verticalLayout.addWidget(self.label_13)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.TXT_OUTGROUPS = QtWidgets.QLineEdit(self.PAGE_METHODS)
        self.TXT_OUTGROUPS.setObjectName("TXT_OUTGROUPS")
        self.gridLayout_2.addWidget(self.TXT_OUTGROUPS, 4, 1, 1, 1)
        self.label_23 = QtWidgets.QLabel(self.PAGE_METHODS)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_23.sizePolicy().hasHeightForWidth())
        self.label_23.setSizePolicy(sizePolicy)
        self.label_23.setMinimumSize(QtCore.QSize(140, 0))
        self.label_23.setObjectName("label_23")
        self.gridLayout_2.addWidget(self.label_23, 4, 0, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.PAGE_METHODS)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_20.sizePolicy().hasHeightForWidth())
        self.label_20.setSizePolicy(sizePolicy)
        self.label_20.setMinimumSize(QtCore.QSize(140, 0))
        self.label_20.setObjectName("label_20")
        self.gridLayout_2.addWidget(self.label_20, 0, 0, 1, 1)
        self.SPN_COMPONENT_TOLERANCE = QtWidgets.QSpinBox(self.PAGE_METHODS)
        self.SPN_COMPONENT_TOLERANCE.setMinimumSize(QtCore.QSize(128, 0))
        self.SPN_COMPONENT_TOLERANCE.setObjectName("SPN_COMPONENT_TOLERANCE")
        self.gridLayout_2.addWidget(self.SPN_COMPONENT_TOLERANCE, 0, 1, 1, 1)
        self.label_26 = QtWidgets.QLabel(self.PAGE_METHODS)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_26.sizePolicy().hasHeightForWidth())
        self.label_26.setSizePolicy(sizePolicy)
        self.label_26.setMinimumSize(QtCore.QSize(140, 0))
        self.label_26.setObjectName("label_26")
        self.gridLayout_2.addWidget(self.label_26, 3, 0, 1, 1)
        self.CMB_SUPERTREE_METHOD = QtWidgets.QComboBox(self.PAGE_METHODS)
        self.CMB_SUPERTREE_METHOD.setMinimumSize(QtCore.QSize(128, 0))
        self.CMB_SUPERTREE_METHOD.setObjectName("CMB_SUPERTREE_METHOD")
        self.gridLayout_2.addWidget(self.CMB_SUPERTREE_METHOD, 3, 1, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.PAGE_METHODS)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_21.sizePolicy().hasHeightForWidth())
        self.label_21.setSizePolicy(sizePolicy)
        self.label_21.setMinimumSize(QtCore.QSize(140, 0))
        self.label_21.setObjectName("label_21")
        self.gridLayout_2.addWidget(self.label_21, 1, 0, 1, 1)
        self.CMB_ALIGNMENT_METHOD = QtWidgets.QComboBox(self.PAGE_METHODS)
        self.CMB_ALIGNMENT_METHOD.setMinimumSize(QtCore.QSize(128, 0))
        self.CMB_ALIGNMENT_METHOD.setObjectName("CMB_ALIGNMENT_METHOD")
        self.gridLayout_2.addWidget(self.CMB_ALIGNMENT_METHOD, 1, 1, 1, 1)
        self.label_22 = QtWidgets.QLabel(self.PAGE_METHODS)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_22.sizePolicy().hasHeightForWidth())
        self.label_22.setSizePolicy(sizePolicy)
        self.label_22.setMinimumSize(QtCore.QSize(140, 0))
        self.label_22.setObjectName("label_22")
        self.gridLayout_2.addWidget(self.label_22, 2, 0, 1, 1)
        self.CMB_TREE_METHOD = QtWidgets.QComboBox(self.PAGE_METHODS)
        self.CMB_TREE_METHOD.setMinimumSize(QtCore.QSize(128, 0))
        self.CMB_TREE_METHOD.setObjectName("CMB_TREE_METHOD")
        self.gridLayout_2.addWidget(self.CMB_TREE_METHOD, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.stackedWidget.addWidget(self.PAGE_METHODS)
        self.PAGE_PAUSE = QtWidgets.QWidget()
        self.PAGE_PAUSE.setObjectName("PAGE_PAUSE")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.PAGE_PAUSE)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_25 = QtWidgets.QLabel(self.PAGE_PAUSE)
        self.label_25.setObjectName("label_25")
        self.verticalLayout_6.addWidget(self.label_25)
        self.label_16 = QtWidgets.QLabel(self.PAGE_PAUSE)
        self.label_16.setWordWrap(True)
        self.label_16.setObjectName("label_16")
        self.verticalLayout_6.addWidget(self.label_16)
        self.CHK_PAUSE_DATA = QtWidgets.QCheckBox(self.PAGE_PAUSE)
        self.CHK_PAUSE_DATA.setMinimumSize(QtCore.QSize(128, 0))
        self.CHK_PAUSE_DATA.setObjectName("CHK_PAUSE_DATA")
        self.verticalLayout_6.addWidget(self.CHK_PAUSE_DATA)
        self.CHK_PAUSE_COMPONENTS = QtWidgets.QCheckBox(self.PAGE_PAUSE)
        self.CHK_PAUSE_COMPONENTS.setMinimumSize(QtCore.QSize(128, 0))
        self.CHK_PAUSE_COMPONENTS.setObjectName("CHK_PAUSE_COMPONENTS")
        self.verticalLayout_6.addWidget(self.CHK_PAUSE_COMPONENTS)
        self.CHK_PAUSE_ALIGNMENTS = QtWidgets.QCheckBox(self.PAGE_PAUSE)
        self.CHK_PAUSE_ALIGNMENTS.setMinimumSize(QtCore.QSize(128, 0))
        self.CHK_PAUSE_ALIGNMENTS.setObjectName("CHK_PAUSE_ALIGNMENTS")
        self.verticalLayout_6.addWidget(self.CHK_PAUSE_ALIGNMENTS)
        self.CHK_PAUSE_TREES = QtWidgets.QCheckBox(self.PAGE_PAUSE)
        self.CHK_PAUSE_TREES.setMinimumSize(QtCore.QSize(128, 0))
        self.CHK_PAUSE_TREES.setObjectName("CHK_PAUSE_TREES")
        self.verticalLayout_6.addWidget(self.CHK_PAUSE_TREES)
        self.CHK_PAUSE_FUSIONS = QtWidgets.QCheckBox(self.PAGE_PAUSE)
        self.CHK_PAUSE_FUSIONS.setMinimumSize(QtCore.QSize(128, 0))
        self.CHK_PAUSE_FUSIONS.setObjectName("CHK_PAUSE_FUSIONS")
        self.verticalLayout_6.addWidget(self.CHK_PAUSE_FUSIONS)
        self.CHK_PAUSE_SPLITS = QtWidgets.QCheckBox(self.PAGE_PAUSE)
        self.CHK_PAUSE_SPLITS.setMinimumSize(QtCore.QSize(128, 0))
        self.CHK_PAUSE_SPLITS.setObjectName("CHK_PAUSE_SPLITS")
        self.verticalLayout_6.addWidget(self.CHK_PAUSE_SPLITS)
        self.CHK_PAUSE_CONSENSUS = QtWidgets.QCheckBox(self.PAGE_PAUSE)
        self.CHK_PAUSE_CONSENSUS.setMinimumSize(QtCore.QSize(128, 0))
        self.CHK_PAUSE_CONSENSUS.setObjectName("CHK_PAUSE_CONSENSUS")
        self.verticalLayout_6.addWidget(self.CHK_PAUSE_CONSENSUS)
        self.CHK_PAUSE_SUBSETS = QtWidgets.QCheckBox(self.PAGE_PAUSE)
        self.CHK_PAUSE_SUBSETS.setMinimumSize(QtCore.QSize(128, 0))
        self.CHK_PAUSE_SUBSETS.setObjectName("CHK_PAUSE_SUBSETS")
        self.verticalLayout_6.addWidget(self.CHK_PAUSE_SUBSETS)
        self.CHK_PAUSE_PREGRAPHS = QtWidgets.QCheckBox(self.PAGE_PAUSE)
        self.CHK_PAUSE_PREGRAPHS.setMinimumSize(QtCore.QSize(128, 0))
        self.CHK_PAUSE_PREGRAPHS.setObjectName("CHK_PAUSE_PREGRAPHS")
        self.verticalLayout_6.addWidget(self.CHK_PAUSE_PREGRAPHS)
        self.CHK_PAUSE_MINIGRAPHS = QtWidgets.QCheckBox(self.PAGE_PAUSE)
        self.CHK_PAUSE_MINIGRAPHS.setMinimumSize(QtCore.QSize(128, 0))
        self.CHK_PAUSE_MINIGRAPHS.setObjectName("CHK_PAUSE_MINIGRAPHS")
        self.verticalLayout_6.addWidget(self.CHK_PAUSE_MINIGRAPHS)
        self.CHK_PAUSE_RAW_NRFG = QtWidgets.QCheckBox(self.PAGE_PAUSE)
        self.CHK_PAUSE_RAW_NRFG.setMinimumSize(QtCore.QSize(128, 0))
        self.CHK_PAUSE_RAW_NRFG.setObjectName("CHK_PAUSE_RAW_NRFG")
        self.verticalLayout_6.addWidget(self.CHK_PAUSE_RAW_NRFG)
        self.CHK_PAUSE_CLEANED_NRFG = QtWidgets.QCheckBox(self.PAGE_PAUSE)
        self.CHK_PAUSE_CLEANED_NRFG.setMinimumSize(QtCore.QSize(128, 0))
        self.CHK_PAUSE_CLEANED_NRFG.setObjectName("CHK_PAUSE_CLEANED_NRFG")
        self.verticalLayout_6.addWidget(self.CHK_PAUSE_CLEANED_NRFG)
        self.CHK_PAUSE_CHECKED_NRFG = QtWidgets.QCheckBox(self.PAGE_PAUSE)
        self.CHK_PAUSE_CHECKED_NRFG.setMinimumSize(QtCore.QSize(128, 0))
        self.CHK_PAUSE_CHECKED_NRFG.setObjectName("CHK_PAUSE_CHECKED_NRFG")
        self.verticalLayout_6.addWidget(self.CHK_PAUSE_CHECKED_NRFG)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem4)
        self.stackedWidget.addWidget(self.PAGE_PAUSE)
        self.PAGE_READY = QtWidgets.QWidget()
        self.PAGE_READY.setObjectName("PAGE_READY")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.PAGE_READY)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_24 = QtWidgets.QLabel(self.PAGE_READY)
        self.label_24.setObjectName("label_24")
        self.verticalLayout_7.addWidget(self.label_24)
        self.label_14 = QtWidgets.QLabel(self.PAGE_READY)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)
        self.label_14.setObjectName("label_14")
        self.verticalLayout_7.addWidget(self.label_14)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_7.addItem(spacerItem5)
        self.stackedWidget.addWidget(self.PAGE_READY)
        self.verticalLayout_3.addWidget(self.stackedWidget)
        self.SPC_ERROR = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SPC_ERROR.sizePolicy().hasHeightForWidth())
        self.SPC_ERROR.setSizePolicy(sizePolicy)
        self.SPC_ERROR.setStyleSheet("background: silver")
        self.SPC_ERROR.setObjectName("SPC_ERROR")
        self.verticalLayout_3.addWidget(self.SPC_ERROR)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.BTN_HELP = QtWidgets.QPushButton(Dialog)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/groot/help.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_HELP.setIcon(icon)
        self.BTN_HELP.setObjectName("BTN_HELP")
        self.horizontalLayout_3.addWidget(self.BTN_HELP)
        self.BTN_CANCEL = QtWidgets.QPushButton(Dialog)
        self.BTN_CANCEL.setObjectName("BTN_CANCEL")
        self.horizontalLayout_3.addWidget(self.BTN_CANCEL)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem6)
        self.BTN_BACK = QtWidgets.QPushButton(Dialog)
        self.BTN_BACK.setObjectName("BTN_BACK")
        self.horizontalLayout_3.addWidget(self.BTN_BACK)
        self.BTN_NEXT = QtWidgets.QPushButton(Dialog)
        self.BTN_NEXT.setObjectName("BTN_NEXT")
        self.horizontalLayout_3.addWidget(self.BTN_NEXT)
        self.BTN_OK = QtWidgets.QPushButton(Dialog)
        self.BTN_OK.setObjectName("BTN_OK")
        self.horizontalLayout_3.addWidget(self.BTN_OK)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.retranslateUi(Dialog)
        self.stackedWidget.setCurrentIndex(5)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_9.setText(_translate("Dialog", "Groot Wizard"))
        self.label_9.setProperty("style", _translate("Dialog", "title"))
        self.LBL_WRN_ACTIVE.setText(_translate("Dialog", "The wizard is already active. You can control it from the <a href=\"action:view_workflow\">workflow</a> dialogue."))
        self.LBL_WRN_ACTIVE.setProperty("style", _translate("Dialog", "warning"))
        self.LBL_WRN_MODEL.setText(_translate("Dialog", "You already have an active model. Start a <a href=\"action:new_model\">new model</a> before beginning the wizard."))
        self.LBL_WRN_MODEL.setProperty("style", _translate("Dialog", "warning"))
        self.LBL_HELP_TITLE.setText(_translate("Dialog", "The wizard performs the complete Groot workflow at once. If you\'d like to play by yourself, or change advanced settings, consider using the <a href=\"action:view_workflow\">workflow</a> instead."))
        self.LBL_HELP_TITLE.setProperty("style", _translate("Dialog", "helpbox"))
        self.label_15.setText(_translate("Dialog", "History"))
        self.label_15.setProperty("style", _translate("Dialog", "heading"))
        self.label_12.setText(_translate("Dialog", "Already have a set of preferred settings? Select them here."))
        self.label_12.setProperty("style", _translate("Dialog", "helpbox"))
        self.BTN_RECENT.setText(_translate("Dialog", "Load"))
        self.BTN_RECENT.setProperty("style", _translate("Dialog", "dropdown"))
        self.BTN_SAVE.setText(_translate("Dialog", "Save"))
        self.label_7.setText(_translate("Dialog", "Name"))
        self.label_7.setProperty("style", _translate("Dialog", "heading"))
        self.label_10.setText(_translate("Dialog", "Give your session a name."))
        self.label_10.setProperty("style", _translate("Dialog", "helpbox"))
        self.CHK_SAVE.setText(_translate("Dialog", "Save to disk throughout the analysis"))
        self.label_8.setText(_translate("Dialog", "Data"))
        self.label_8.setProperty("style", _translate("Dialog", "heading"))
        self.label_11.setText(_translate("Dialog", "Specify at least one FASTA file and a corresponding BLAST file."))
        self.label_11.setProperty("style", _translate("Dialog", "helpbox"))
        self.BTN_REMOVE_FILE.setText(_translate("Dialog", "Remove"))
        self.BTN_ADD_FILE.setText(_translate("Dialog", "Add"))
        self.BTN_SAMPLES.setText(_translate("Dialog", "Sample"))
        self.BTN_SAMPLES.setProperty("style", _translate("Dialog", "dropdown"))
        self.label_19.setText(_translate("Dialog", "Methods and parameters"))
        self.label_19.setProperty("style", _translate("Dialog", "heading"))
        self.label_13.setText(_translate("Dialog", "Choose your tools."))
        self.label_13.setProperty("style", _translate("Dialog", "helpbox"))
        self.label_23.setText(_translate("Dialog", "Outgroups"))
        self.label_20.setText(_translate("Dialog", "Component tolerance"))
        self.label_26.setText(_translate("Dialog", "Supertree algorithm"))
        self.label_21.setText(_translate("Dialog", "Alignment algorithm"))
        self.label_22.setText(_translate("Dialog", "Tree algorithm"))
        self.label_25.setText(_translate("Dialog", "Pause to review"))
        self.label_25.setProperty("style", _translate("Dialog", "heading"))
        self.label_16.setText(_translate("Dialog", "The wizard can pause part-way for you to look at how things are progressing."))
        self.label_16.setProperty("style", _translate("Dialog", "helpbox"))
        self.CHK_PAUSE_DATA.setText(_translate("Dialog", "Data import"))
        self.CHK_PAUSE_COMPONENTS.setText(_translate("Dialog", "Components"))
        self.CHK_PAUSE_ALIGNMENTS.setText(_translate("Dialog", "Alignments"))
        self.CHK_PAUSE_TREES.setText(_translate("Dialog", "Trees"))
        self.CHK_PAUSE_FUSIONS.setText(_translate("Dialog", "Fusions"))
        self.CHK_PAUSE_SPLITS.setText(_translate("Dialog", "Splits"))
        self.CHK_PAUSE_CONSENSUS.setText(_translate("Dialog", "Consensus"))
        self.CHK_PAUSE_SUBSETS.setText(_translate("Dialog", "Subsets"))
        self.CHK_PAUSE_PREGRAPHS.setText(_translate("Dialog", "Pregraphs"))
        self.CHK_PAUSE_MINIGRAPHS.setText(_translate("Dialog", "Minigraphs"))
        self.CHK_PAUSE_RAW_NRFG.setText(_translate("Dialog", "Raw NRFG"))
        self.CHK_PAUSE_CLEANED_NRFG.setText(_translate("Dialog", "Cleaned NRFG"))
        self.CHK_PAUSE_CHECKED_NRFG.setText(_translate("Dialog", "Checked NRFG"))
        self.label_24.setText(_translate("Dialog", "Power on"))
        self.label_24.setProperty("style", _translate("Dialog", "heading"))
        self.label_14.setText(_translate("Dialog", "When you\'re ready, click begin. The wizard will start paused and you can come back to this screen to view the current settings at any time."))
        self.label_14.setProperty("style", _translate("Dialog", "helpbox"))
        self.BTN_HELP.setText(_translate("Dialog", "Help"))
        self.BTN_CANCEL.setText(_translate("Dialog", "Cancel"))
        self.BTN_BACK.setText(_translate("Dialog", "Back"))
        self.BTN_NEXT.setText(_translate("Dialog", "Next"))
        self.BTN_OK.setText(_translate("Dialog", "OK"))


