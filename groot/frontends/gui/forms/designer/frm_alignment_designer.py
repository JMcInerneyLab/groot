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
        Dialog.resize(873, 698)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout.setSpacing(8)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(8)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.BTN_SELECTION = QtWidgets.QPushButton(self.frame)
        self.BTN_SELECTION.setAutoDefault(False)
        self.BTN_SELECTION.setObjectName("BTN_SELECTION")
        self.horizontalLayout.addWidget(self.BTN_SELECTION)
        self.BTN_START = QtWidgets.QPushButton(self.frame)
        self.BTN_START.setAutoDefault(False)
        self.BTN_START.setObjectName("BTN_START")
        self.horizontalLayout.addWidget(self.BTN_START)
        self.LBL_POSITION_START = QtWidgets.QLabel(self.frame)
        self.LBL_POSITION_START.setObjectName("LBL_POSITION_START")
        self.horizontalLayout.addWidget(self.LBL_POSITION_START)
        self.SCR_MAIN = QtWidgets.QScrollBar(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SCR_MAIN.sizePolicy().hasHeightForWidth())
        self.SCR_MAIN.setSizePolicy(sizePolicy)
        self.SCR_MAIN.setOrientation(QtCore.Qt.Horizontal)
        self.SCR_MAIN.setObjectName("SCR_MAIN")
        self.horizontalLayout.addWidget(self.SCR_MAIN)
        self.LBL_POSITION_END = QtWidgets.QLabel(self.frame)
        self.LBL_POSITION_END.setObjectName("LBL_POSITION_END")
        self.horizontalLayout.addWidget(self.LBL_POSITION_END)
        self.BTN_END = QtWidgets.QPushButton(self.frame)
        self.BTN_END.setAutoDefault(False)
        self.BTN_END.setObjectName("BTN_END")
        self.horizontalLayout.addWidget(self.BTN_END)
        self.verticalLayout.addWidget(self.frame)
        self.LBL_SELECTION_WARNING = QtWidgets.QLabel(Dialog)
        self.LBL_SELECTION_WARNING.setObjectName("LBL_SELECTION_WARNING")
        self.verticalLayout.addWidget(self.LBL_SELECTION_WARNING)
        self.scrollArea = QtWidgets.QScrollArea(Dialog)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 855, 578))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.GRID_MAIN = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.GRID_MAIN.setContentsMargins(0, 0, 0, 0)
        self.GRID_MAIN.setSpacing(0)
        self.GRID_MAIN.setObjectName("GRID_MAIN")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.LBL_INFO = QtWidgets.QLabel(Dialog)
        self.LBL_INFO.setObjectName("LBL_INFO")
        self.verticalLayout.addWidget(self.LBL_INFO)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.BTN_SELECTION.setText(_translate("Dialog", "Selection"))
        self.BTN_SELECTION.setProperty("style", _translate("Dialog", "dropdown"))
        self.BTN_START.setText(_translate("Dialog", "Start"))
        self.LBL_POSITION_START.setText(_translate("Dialog", "0"))
        self.LBL_POSITION_END.setText(_translate("Dialog", "0"))
        self.BTN_END.setText(_translate("Dialog", "End"))
        self.LBL_SELECTION_WARNING.setText(_translate("Dialog", "<a href=\"action:show_selection\">Select</a> a single component to view its alignment."))
        self.LBL_SELECTION_WARNING.setProperty("style", _translate("Dialog", "warning"))
        self.LBL_INFO.setText(_translate("Dialog", "Alignment information"))


