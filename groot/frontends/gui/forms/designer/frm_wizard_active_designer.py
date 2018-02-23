# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_wizard_active_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1131, 959)
        Dialog.setStyleSheet("\n"
"\n"
"QWidget\n"
"{\n"
"    background  : #FFFFFF;\n"
"    font-family : \"American Typewriter\", \"Courier New\", \"Courier\";\n"
"    font-size   : 16pt;\n"
"}\n"
"\n"
"QTabBar::tab\n"
"{\n"
"    background    : #FFFFFF;\n"
"    color         : #000000;\n"
"    border-bottom : 4px solid #0080C0;\n"
"    padding       : 4px;\n"
"    margin        : 2px;\n"
"}\n"
"\n"
"QTabWidget::pane\n"
"{\n"
"    background : #FFFFFF;\n"
"}\n"
"\n"
"QTabBar::tab:selected\n"
"{\n"
"    border-bottom : 4px solid #00C000;\n"
"}\n"
"\n"
"QTabBar::tab:hover\n"
"{\n"
"    border-bottom : 4px solid #0060C0;\n"
"}\n"
"\n"
"QTabBar::tab:selected:hover\n"
"{\n"
"    border-bottom : 4px solid #00C040;\n"
"}\n"
"\n"
"QMdiArea\n"
"{\n"
"    background : #6495ED;\n"
"}\n"
"\n"
"QDialog\n"
"{\n"
"    background : #FFFFFF;\n"
"}\n"
"\n"
"QToolButton\n"
"{\n"
"    background    : #0080C0;\n"
"    color         : #FFFFFF;\n"
"    border-radius : 4px;\n"
"    margin        : 2px;\n"
"    padding       : 2px;\n"
"    font-weight   : bold;\n"
"    border        : 3px solid #0080C0;\n"
"}\n"
"\n"
"QPushButton\n"
"{\n"
"    background     : #0080C0;\n"
"    color          : #FFFFFF;\n"
"    font-weight    : bold;\n"
"    padding-left   : 16px;\n"
"    padding-right  : 16px;\n"
"    padding-top    : 8px;\n"
"    padding-bottom : 8px;\n"
"    border         : 3px solid #0080C0;\n"
"    border-radius  : 8px;\n"
"}\n"
"\n"
"QPushButton:hover, QToolButton:hover, QTextEdit:hover, QLineEdit:hover, QComboBox:hover\n"
"{\n"
"    border : 3px solid #FF8000;\n"
"}\n"
"\n"
"QPushButton:pressed, QToolButton:pressed\n"
"{\n"
"    background : #0060C0;\n"
"}\n"
"\n"
"QPushButton:disabled, QToolButton:disabled\n"
"{\n"
"    background : #D0D0D0;\n"
"}\n"
"\n"
"QTreeWidget\n"
"{\n"
"    background    : #EEEEFF;\n"
"    color         : black;\n"
"    border-style  : solid;\n"
"    border-width  : 1px;\n"
"    border-color  : #808080;\n"
"    border-radius : 0px;\n"
"}\n"
"\n"
"QTextEdit, QLineEdit, QComboBox, QSpinBox\n"
"{\n"
"    background    : #EEEEFF;\n"
"    color         : #000000;\n"
"    border        : 3px solid #0080C0;\n"
"    border-radius : 8px;\n"
"    padding       : 5px;\n"
"}\n"
"\n"
"/* Buttons for spin box, combo box */\n"
"\n"
"QSpinBox::up-button,QSpinBox::down-button,QComboBox::drop-down\n"
"{\n"
"    subcontrol-origin   : padding;\n"
"    width               : 24px;\n"
"    margin              : 5px;\n"
"    border-radius       : 4px;\n"
"    background          : #0080C0;\n"
"}\n"
"\n"
"QSpinBox::up-button\n"
"{\n"
"    subcontrol-position : top right;\n"
"    height              : 12px;\n"
"}\n"
"\n"
"QSpinBox::down-button\n"
"{\n"
"    subcontrol-position : bottom right;\n"
"    height              : 12px;\n"
"}\n"
"\n"
"QComboBox::drop-down\n"
"{\n"
"    subcontrol-position : right;\n"
"    height              : 24px;\n"
"}\n"
"\n"
"QSpinBox::up-arrow,QSpinBox::down-arrow,QComboBox::down-arrow\n"
"{\n"
"    width  : 16px;\n"
"    height : 16px;\n"
"}\n"
"\n"
"QSpinBox::down-arrow\n"
"{\n"
"    image  : url(:/down_arrow.svg);\n"
"}\n"
"\n"
"QSpinBox::up-arrow\n"
"{\n"
"    image  : url(:/up_arrow.svg);\n"
"}\n"
"\n"
"QComboBox::down-arrow\n"
"{\n"
"    image  : url(:/dropdown.svg);\n"
"}\n"
"\n"
"/* Menu */\n"
"\n"
"QMenuBar\n"
"{\n"
"    background-color : #0080C0;\n"
"    color            : white;\n"
"    border-width     : 1px;\n"
"    border-style     : transparent;\n"
"    border-color     : black;\n"
"}\n"
"\n"
"QMenuBar::item\n"
"{\n"
"    background-color : #0080C0;\n"
"    color            : #FFFFFF;\n"
"    border-width     : 1px;\n"
"    border-style     : solid;\n"
"    border-color     : #0080C0;\n"
"    border-radius    : 8px;\n"
"    padding          : 2px;\n"
"    margin           : 2px;\n"
"}\n"
"\n"
"QMenu\n"
"{\n"
"    background-color : #0080C0;\n"
"    color            : #FFFFFF;\n"
"    border-width     : 1px;\n"
"    border-style     : transparent;\n"
"    border-color     : black;\n"
"    border-radius    : 8px;\n"
"}\n"
"\n"
"QMenu::item\n"
"{\n"
"    background-color : #0080C0;\n"
"    color            : #FFFFFF;\n"
"    border     : 3px solid #0080C0;\n"
"    border-radius    : 8px;\n"
"    padding          : 8px;\n"
"    padding-left     : 32px;\n"
"    margin           : 1px;\n"
"}\n"
"\n"
"QMenu::indicator:non-exclusive:!checked\n"
"{\n"
"    image: url(:/check_indeterminate.svg);\n"
"    width: 16px;\n"
"    height: 16px;\n"
"}\n"
"\n"
"QMenu::indicator:non-exclusive:checked\n"
"{\n"
"    image: url(:/check_yes.svg);\n"
"    width: 16px;\n"
"    height: 16px;\n"
"}\n"
"\n"
"QMenu::item:selected\n"
"{\n"
"    border-color : #FF8000;\n"
"}\n"
"\n"
"/* Checkable buttons */\n"
"\n"
"QPushButton:checked, QToolButton:checked\n"
"{\n"
"    background : #00C000;\n"
"}\n"
"\n"
"QPushButton:checked:pressed, QToolButton:checked:pressed\n"
"{\n"
"    background : #00C040;\n"
"}\n"
"\n"
"/* Scroll bars */\n"
"\n"
"QScrollBar\n"
"{\n"
"    background : #FFFFFF;\n"
"}\n"
"\n"
"QScrollBar:vertical\n"
"{\n"
"    width : 8px;\n"
"}\n"
"\n"
"QScrollBar:horizontal\n"
"{\n"
"    height : 8px;\n"
"}\n"
"\n"
"QScrollBar::handle\n"
"{\n"
"    background    : #90C0D0;\n"
"    border-radius : 4px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical\n"
"{\n"
"    min-width : 8px;\n"
"    margin    : 8px 0px 8px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal\n"
"{\n"
"    min-height : 8px;\n"
"    margin     : 0px 8px 0px 8px;\n"
"}\n"
"\n"
"QScrollBar:up-arrow, QScrollBar::down-arrow, QScrollBar::left-arrow, QScrollBar::right-arrow\n"
"{\n"
"    border-size   : 1px;\n"
"    border-radius : 4px;\n"
"    width         : 8px;\n"
"    height        : 8px;\n"
"    background    : #0080C0;\n"
"}\n"
"\n"
"QScrollBar::sub-line, QScrollBar::add-line\n"
"{\n"
"    background : #C0C0C0;\n"
"}\n"
"\n"
"/* Radio button and checkbox */\n"
"\n"
"QRadioButton, QCheckBox\n"
"{\n"
"    padding : 2px;\n"
"}\n"
"\n"
"QRadioButton::indicator, QCheckBox::indicator\n"
"{\n"
"    background : #0080C0;\n"
"    width      : 16px;\n"
"    height     : 16px;\n"
"}\n"
"\n"
"QCheckBox::indicator\n"
"{\n"
"    border-radius : 4px;\n"
"}\n"
"\n"
"QRadioButton::indicator\n"
"{\n"
"    border-radius : 8px;\n"
"}\n"
"\n"
"QRadioButton::indicator:checked, QCheckBox::indicator:checked\n"
"{\n"
"    background : #00C000;\n"
"    image      : url(:/check_yes.svg);\n"
"}\n"
"\n"
"QRadioButton::indicator:unchecked, QCheckBox::indicator:unchecked\n"
"{\n"
"    image : none;\n"
"}\n"
"\n"
"QRadioButton::indicator:indeterminate, QCheckBox::indicator:indeterminate\n"
"{\n"
"    image : url(:/check_indeterminate.svg);\n"
"}\n"
"\n"
"/* Special styles $(MINIMAL) */\n"
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
"QLabel[style=\"heading\"], QPushButton[style=\"heading\"]\n"
"{\n"
"    background     : #FFFFFF;\n"
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
"    font-size      : 16px;\n"
"}\n"
"\n"
"QLabel[style=\"subheading\"]\n"
"{\n"
"    background : #FF0000;\n"
"}\n"
"\n"
"QLabel[style=\"helpbox\"]\n"
"{\n"
"    background    : #FFFFD0;\n"
"    padding       : 8px;\n"
"    border-radius : 4px;\n"
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
"    border-color:#00C080; \n"
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
"    background : #092049;\n"
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
"}")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.BTN_REFRESH = QtWidgets.QToolButton(self.frame)
        self.BTN_REFRESH.setText("")
        self.BTN_REFRESH.setObjectName("BTN_REFRESH")
        self.horizontalLayout_3.addWidget(self.BTN_REFRESH)
        self.verticalLayout_2.addWidget(self.frame)
        self.LBL_WARN_INACTIVE = QtWidgets.QLabel(Dialog)
        self.LBL_WARN_INACTIVE.setObjectName("LBL_WARN_INACTIVE")
        self.verticalLayout_2.addWidget(self.LBL_WARN_INACTIVE)
        self.LBL_FILENAME = QtWidgets.QLabel(Dialog)
        self.LBL_FILENAME.setObjectName("LBL_FILENAME")
        self.verticalLayout_2.addWidget(self.LBL_FILENAME)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.TXT_FILENAME = QtWidgets.QLineEdit(Dialog)
        self.TXT_FILENAME.setObjectName("TXT_FILENAME")
        self.horizontalLayout.addWidget(self.TXT_FILENAME)
        self.BTN_FILENAME = QtWidgets.QPushButton(Dialog)
        self.BTN_FILENAME.setObjectName("BTN_FILENAME")
        self.horizontalLayout.addWidget(self.BTN_FILENAME)
        self.BTN_COPY_FILE = QtWidgets.QPushButton(Dialog)
        self.BTN_COPY_FILE.setObjectName("BTN_COPY_FILE")
        self.horizontalLayout.addWidget(self.BTN_COPY_FILE)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.LBL_P_DATA = QtWidgets.QLabel(Dialog)
        self.LBL_P_DATA.setObjectName("LBL_P_DATA")
        self.verticalLayout_2.addWidget(self.LBL_P_DATA)
        self.LBL_DATA = QtWidgets.QLabel(Dialog)
        self.LBL_DATA.setObjectName("LBL_DATA")
        self.verticalLayout_2.addWidget(self.LBL_DATA)
        self.LBL_P_COMP = QtWidgets.QLabel(Dialog)
        self.LBL_P_COMP.setObjectName("LBL_P_COMP")
        self.verticalLayout_2.addWidget(self.LBL_P_COMP)
        self.LBL_COMPONENTS = QtWidgets.QLabel(Dialog)
        self.LBL_COMPONENTS.setObjectName("LBL_COMPONENTS")
        self.verticalLayout_2.addWidget(self.LBL_COMPONENTS)
        self.LBL_P_SEQ = QtWidgets.QLabel(Dialog)
        self.LBL_P_SEQ.setObjectName("LBL_P_SEQ")
        self.verticalLayout_2.addWidget(self.LBL_P_SEQ)
        self.LBL_SEQUENCES = QtWidgets.QLabel(Dialog)
        self.LBL_SEQUENCES.setObjectName("LBL_SEQUENCES")
        self.verticalLayout_2.addWidget(self.LBL_SEQUENCES)
        self.LBL_P_TREE = QtWidgets.QLabel(Dialog)
        self.LBL_P_TREE.setObjectName("LBL_P_TREE")
        self.verticalLayout_2.addWidget(self.LBL_P_TREE)
        self.LBL_TREES = QtWidgets.QLabel(Dialog)
        self.LBL_TREES.setObjectName("LBL_TREES")
        self.verticalLayout_2.addWidget(self.LBL_TREES)
        self.LBL_P_FUS = QtWidgets.QLabel(Dialog)
        self.LBL_P_FUS.setObjectName("LBL_P_FUS")
        self.verticalLayout_2.addWidget(self.LBL_P_FUS)
        self.LBL_FUSIONS = QtWidgets.QLabel(Dialog)
        self.LBL_FUSIONS.setObjectName("LBL_FUSIONS")
        self.verticalLayout_2.addWidget(self.LBL_FUSIONS)
        self.LBL_P_NRFG = QtWidgets.QLabel(Dialog)
        self.LBL_P_NRFG.setObjectName("LBL_P_NRFG")
        self.verticalLayout_2.addWidget(self.LBL_P_NRFG)
        self.LBL_NRFG = QtWidgets.QLabel(Dialog)
        self.LBL_NRFG.setObjectName("LBL_NRFG")
        self.verticalLayout_2.addWidget(self.LBL_NRFG)
        self.FRA_PAUSED = QtWidgets.QFrame(Dialog)
        self.FRA_PAUSED.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FRA_PAUSED.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FRA_PAUSED.setObjectName("FRA_PAUSED")
        self.gridLayout = QtWidgets.QGridLayout(self.FRA_PAUSED)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.BTN_CONTINUE = QtWidgets.QPushButton(self.FRA_PAUSED)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN_CONTINUE.sizePolicy().hasHeightForWidth())
        self.BTN_CONTINUE.setSizePolicy(sizePolicy)
        self.BTN_CONTINUE.setObjectName("BTN_CONTINUE")
        self.horizontalLayout_2.addWidget(self.BTN_CONTINUE)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 1, 1, 1)
        self.LBL_NEXT = QtWidgets.QLabel(self.FRA_PAUSED)
        self.LBL_NEXT.setAlignment(QtCore.Qt.AlignCenter)
        self.LBL_NEXT.setObjectName("LBL_NEXT")
        self.gridLayout.addWidget(self.LBL_NEXT, 2, 1, 1, 1)
        self.LBL_PAUSED = QtWidgets.QLabel(self.FRA_PAUSED)
        self.LBL_PAUSED.setAlignment(QtCore.Qt.AlignCenter)
        self.LBL_PAUSED.setObjectName("LBL_PAUSED")
        self.gridLayout.addWidget(self.LBL_PAUSED, 0, 1, 1, 1)
        self.LBL_CLOSE = QtWidgets.QLabel(self.FRA_PAUSED)
        self.LBL_CLOSE.setAlignment(QtCore.Qt.AlignCenter)
        self.LBL_CLOSE.setObjectName("LBL_CLOSE")
        self.gridLayout.addWidget(self.LBL_CLOSE, 4, 1, 1, 1)
        self.line = QtWidgets.QFrame(self.FRA_PAUSED)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 3, 1, 1, 1)
        self.verticalLayout_2.addWidget(self.FRA_PAUSED)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.frame.setProperty("style", _translate("Dialog", "title"))
        self.label.setText(_translate("Dialog", "Wizard status"))
        self.label.setProperty("style", _translate("Dialog", "title-embeded"))
        self.BTN_REFRESH.setProperty("style", _translate("Dialog", "refresh"))
        self.LBL_WARN_INACTIVE.setText(_translate("Dialog", "The wizard is not running. Open the <a href=\"action:show_wizard\">wizard window</a>."))
        self.LBL_WARN_INACTIVE.setProperty("style", _translate("Dialog", "warning"))
        self.LBL_FILENAME.setText(_translate("Dialog", "The file has been saved to:"))
        self.BTN_FILENAME.setText(_translate("Dialog", "Open in workflow"))
        self.BTN_COPY_FILE.setText(_translate("Dialog", "Copy to..."))
        self.LBL_P_DATA.setText(_translate("Dialog", "Data will be loaded from {} files."))
        self.LBL_P_DATA.setProperty("style", _translate("Dialog", "helpbox"))
        self.LBL_DATA.setText(_translate("Dialog", "Data has been loaded. View the <a href=\"action:show_text_data\">raw data</a>."))
        self.LBL_DATA.setProperty("style", _translate("Dialog", "helpbox"))
        self.LBL_P_COMP.setText(_translate("Dialog", "Components will be generated using a tolerance of {}."))
        self.LBL_P_COMP.setProperty("style", _translate("Dialog", "helpbox"))
        self.LBL_COMPONENTS.setText(_translate("Dialog", "Components have been generated, view the <a href=\"action:show_entities\">summary</a> or draw a <a href=\"action:show_lego\">lego diagram</a>."))
        self.LBL_COMPONENTS.setProperty("style", _translate("Dialog", "helpbox"))
        self.LBL_P_SEQ.setText(_translate("Dialog", "Sequences will be aligned using the {} method."))
        self.LBL_P_SEQ.setProperty("style", _translate("Dialog", "helpbox"))
        self.LBL_SEQUENCES.setText(_translate("Dialog", "Sequences have been aligned, open the <a href=\"action:show_alignments\">alignment viewer</a>."))
        self.LBL_SEQUENCES.setProperty("style", _translate("Dialog", "helpbox"))
        self.LBL_P_TREE.setText(_translate("Dialog", "Trees will be grown using the {} method."))
        self.LBL_P_TREE.setProperty("style", _translate("Dialog", "helpbox"))
        self.LBL_TREES.setText(_translate("Dialog", "Trees have been grown, open the <a href=\"action:show_trees\">tree view</a>."))
        self.LBL_TREES.setProperty("style", _translate("Dialog", "helpbox"))
        self.LBL_P_FUS.setText(_translate("Dialog", "Fusions will be found using the default method."))
        self.LBL_P_FUS.setProperty("style", _translate("Dialog", "helpbox"))
        self.LBL_FUSIONS.setText(_translate("Dialog", "Fusions have been found, view the <a href=\"action:show_fusions\">raw data</a> or show them in the <a href=\"action:show_trees\">trees</a>."))
        self.LBL_FUSIONS.setProperty("style", _translate("Dialog", "helpbox"))
        self.LBL_P_NRFG.setText(_translate("Dialog", "The NRFG will be crafted using the default method."))
        self.LBL_P_NRFG.setProperty("style", _translate("Dialog", "helpbox"))
        self.LBL_NRFG.setText(_translate("Dialog", "The NRFG has been crafted. View the <a href=\"action:show_trees\">NRFG</a>."))
        self.LBL_NRFG.setProperty("style", _translate("Dialog", "helpbox"))
        self.BTN_CONTINUE.setText(_translate("Dialog", "CLICK TO CONTINUE"))
        self.BTN_CONTINUE.setProperty("style", _translate("Dialog", "completed"))
        self.LBL_NEXT.setText(_translate("Dialog", "Next step: <a href=\"action:wizard_next\">{}</a>."))
        self.LBL_PAUSED.setText(_translate("Dialog", "The process has been paused for you to review its progress."))
        self.LBL_CLOSE.setText(_translate("Dialog", "You can always <a href=\"action:close_window\">close</a> the wizard and continue manually."))

