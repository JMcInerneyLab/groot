# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_alignment_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(948, 671)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout.setSpacing(8)
        self.verticalLayout.setObjectName("verticalLayout")
        self.FRA_TOOLBAR = QtWidgets.QFrame(Dialog)
        self.FRA_TOOLBAR.setObjectName("FRA_TOOLBAR")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.FRA_TOOLBAR)
        self.horizontalLayout_3.setContentsMargins(8, 8, 8, 8)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.CHK_ALIGNED = QtWidgets.QCheckBox(self.FRA_TOOLBAR)
        self.CHK_ALIGNED.setChecked(True)
        self.CHK_ALIGNED.setTristate(True)
        self.CHK_ALIGNED.setObjectName("CHK_ALIGNED")
        self.gridLayout_3.addWidget(self.CHK_ALIGNED, 0, 0, 1, 1)
        self.CHK_ACCESSIONS = QtWidgets.QCheckBox(self.FRA_TOOLBAR)
        self.CHK_ACCESSIONS.setChecked(True)
        self.CHK_ACCESSIONS.setTristate(True)
        self.CHK_ACCESSIONS.setObjectName("CHK_ACCESSIONS")
        self.gridLayout_3.addWidget(self.CHK_ACCESSIONS, 1, 0, 1, 1)
        self.horizontalLayout_3.addLayout(self.gridLayout_3)
        self.BTN_START = QtWidgets.QToolButton(self.FRA_TOOLBAR)
        self.BTN_START.setMinimumSize(QtCore.QSize(64, 64))
        self.BTN_START.setMaximumSize(QtCore.QSize(64, 64))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/intermake/previous.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_START.setIcon(icon)
        self.BTN_START.setIconSize(QtCore.QSize(32, 32))
        self.BTN_START.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_START.setObjectName("BTN_START")
        self.horizontalLayout_3.addWidget(self.BTN_START)
        self.BTN_END = QtWidgets.QToolButton(self.FRA_TOOLBAR)
        self.BTN_END.setMinimumSize(QtCore.QSize(64, 64))
        self.BTN_END.setMaximumSize(QtCore.QSize(64, 64))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/intermake/next.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_END.setIcon(icon1)
        self.BTN_END.setIconSize(QtCore.QSize(32, 32))
        self.BTN_END.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_END.setObjectName("BTN_END")
        self.horizontalLayout_3.addWidget(self.BTN_END)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.LBL_POSITION_START = QtWidgets.QLabel(self.FRA_TOOLBAR)
        self.LBL_POSITION_START.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LBL_POSITION_START.setObjectName("LBL_POSITION_START")
        self.gridLayout_2.addWidget(self.LBL_POSITION_START, 1, 0, 1, 1)
        self.SCR_MAIN = QtWidgets.QScrollBar(self.FRA_TOOLBAR)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SCR_MAIN.sizePolicy().hasHeightForWidth())
        self.SCR_MAIN.setSizePolicy(sizePolicy)
        self.SCR_MAIN.setOrientation(QtCore.Qt.Horizontal)
        self.SCR_MAIN.setObjectName("SCR_MAIN")
        self.gridLayout_2.addWidget(self.SCR_MAIN, 1, 1, 1, 1)
        self.LBL_POSITION_END = QtWidgets.QLabel(self.FRA_TOOLBAR)
        self.LBL_POSITION_END.setObjectName("LBL_POSITION_END")
        self.gridLayout_2.addWidget(self.LBL_POSITION_END, 1, 2, 1, 1)
        self.LBL_POSITION_START_2 = QtWidgets.QLabel(self.FRA_TOOLBAR)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_POSITION_START_2.sizePolicy().hasHeightForWidth())
        self.LBL_POSITION_START_2.setSizePolicy(sizePolicy)
        self.LBL_POSITION_START_2.setObjectName("LBL_POSITION_START_2")
        self.gridLayout_2.addWidget(self.LBL_POSITION_START_2, 0, 0, 1, 1)
        self.LBL_POSITION_START_3 = QtWidgets.QLabel(self.FRA_TOOLBAR)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_POSITION_START_3.sizePolicy().hasHeightForWidth())
        self.LBL_POSITION_START_3.setSizePolicy(sizePolicy)
        self.LBL_POSITION_START_3.setObjectName("LBL_POSITION_START_3")
        self.gridLayout_2.addWidget(self.LBL_POSITION_START_3, 0, 2, 1, 1)
        self.LBL_SCRPOS = QtWidgets.QLabel(self.FRA_TOOLBAR)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_SCRPOS.sizePolicy().hasHeightForWidth())
        self.LBL_SCRPOS.setSizePolicy(sizePolicy)
        self.LBL_SCRPOS.setAlignment(QtCore.Qt.AlignCenter)
        self.LBL_SCRPOS.setObjectName("LBL_SCRPOS")
        self.gridLayout_2.addWidget(self.LBL_SCRPOS, 0, 1, 1, 1)
        self.horizontalLayout_3.addLayout(self.gridLayout_2)
        self.verticalLayout.addWidget(self.FRA_TOOLBAR)
        self.LBL_SELECTION_WARNING = QtWidgets.QLabel(Dialog)
        self.LBL_SELECTION_WARNING.setObjectName("LBL_SELECTION_WARNING")
        self.verticalLayout.addWidget(self.LBL_SELECTION_WARNING)
        self.LBL_ERROR = QtWidgets.QLabel(Dialog)
        self.LBL_ERROR.setObjectName("LBL_ERROR")
        self.verticalLayout.addWidget(self.LBL_ERROR)
        self.scrollArea = QtWidgets.QScrollArea(Dialog)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 930, 467))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.GRID_MAIN = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.GRID_MAIN.setContentsMargins(0, 0, 0, 0)
        self.GRID_MAIN.setSpacing(0)
        self.GRID_MAIN.setObjectName("GRID_MAIN")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.frame_2 = QtWidgets.QFrame(Dialog)
        self.frame_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.LBL_POSITION = QtWidgets.QLabel(self.frame_2)
        self.LBL_POSITION.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.LBL_POSITION.setText("")
        self.LBL_POSITION.setObjectName("LBL_POSITION")
        self.gridLayout.addWidget(self.LBL_POSITION, 1, 1, 1, 1)
        self.LBL_INFO_3 = QtWidgets.QLabel(self.frame_2)
        self.LBL_INFO_3.setObjectName("LBL_INFO_3")
        self.gridLayout.addWidget(self.LBL_INFO_3, 0, 1, 1, 1)
        self.LBL_INFO_2 = QtWidgets.QLabel(self.frame_2)
        self.LBL_INFO_2.setObjectName("LBL_INFO_2")
        self.gridLayout.addWidget(self.LBL_INFO_2, 0, 0, 1, 1)
        self.LBL_SEQUENCE = QtWidgets.QLabel(self.frame_2)
        self.LBL_SEQUENCE.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.LBL_SEQUENCE.setText("")
        self.LBL_SEQUENCE.setObjectName("LBL_SEQUENCE")
        self.gridLayout.addWidget(self.LBL_SEQUENCE, 1, 0, 1, 1)
        self.LBL_INFO_5 = QtWidgets.QLabel(self.frame_2)
        self.LBL_INFO_5.setObjectName("LBL_INFO_5")
        self.gridLayout.addWidget(self.LBL_INFO_5, 0, 2, 1, 1)
        self.LBL_SITE = QtWidgets.QLabel(self.frame_2)
        self.LBL_SITE.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.LBL_SITE.setText("")
        self.LBL_SITE.setObjectName("LBL_SITE")
        self.gridLayout.addWidget(self.LBL_SITE, 1, 2, 1, 1)
        self.verticalLayout.addWidget(self.frame_2)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.CHK_ALIGNED.setText(_translate("Dialog", "Aligned"))
        self.CHK_ACCESSIONS.setText(_translate("Dialog", "Accessions"))
        self.BTN_START.setText(_translate("Dialog", "Start"))
        self.BTN_END.setText(_translate("Dialog", "End"))
        self.LBL_POSITION_START.setText(_translate("Dialog", "0"))
        self.LBL_POSITION_END.setText(_translate("Dialog", "0"))
        self.LBL_POSITION_START_2.setText(_translate("Dialog", "Start"))
        self.LBL_POSITION_START_3.setText(_translate("Dialog", "End"))
        self.LBL_SCRPOS.setText(_translate("Dialog", "End"))
        self.LBL_SELECTION_WARNING.setText(_translate("Dialog", "<a href=\"action:show_selection\">Select</a> a single component to view its alignment."))
        self.LBL_SELECTION_WARNING.setProperty("style", _translate("Dialog", "warning"))
        self.LBL_ERROR.setText(_translate("Dialog", "Message."))
        self.LBL_ERROR.setProperty("style", _translate("Dialog", "warning"))
        self.LBL_INFO_3.setText(_translate("Dialog", "Position"))
        self.LBL_INFO_2.setText(_translate("Dialog", "Sequence"))
        self.LBL_INFO_5.setText(_translate("Dialog", "Site"))


