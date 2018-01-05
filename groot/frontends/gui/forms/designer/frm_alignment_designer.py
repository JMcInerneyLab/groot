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
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.BTN_START = QtWidgets.QPushButton(Dialog)
        self.BTN_START.setObjectName("BTN_START")
        self.horizontalLayout.addWidget(self.BTN_START)
        self.SCR_MAIN = QtWidgets.QScrollBar(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.SCR_MAIN.sizePolicy().hasHeightForWidth())
        self.SCR_MAIN.setSizePolicy(sizePolicy)
        self.SCR_MAIN.setOrientation(QtCore.Qt.Horizontal)
        self.SCR_MAIN.setObjectName("SCR_MAIN")
        self.horizontalLayout.addWidget(self.SCR_MAIN)
        self.BTN_END = QtWidgets.QPushButton(Dialog)
        self.BTN_END.setObjectName("BTN_END")
        self.horizontalLayout.addWidget(self.BTN_END)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.scrollArea = QtWidgets.QScrollArea(Dialog)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 847, 588))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.GRID_MAIN = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.GRID_MAIN.setContentsMargins(0, 0, 0, 0)
        self.GRID_MAIN.setSpacing(0)
        self.GRID_MAIN.setObjectName("GRID_MAIN")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.LBL_INFO = QtWidgets.QLabel(Dialog)
        self.LBL_INFO.setText("")
        self.LBL_INFO.setObjectName("LBL_INFO")
        self.horizontalLayout_2.addWidget(self.LBL_INFO)
        self.BTNBOX_MAIN = QtWidgets.QDialogButtonBox(Dialog)
        self.BTNBOX_MAIN.setOrientation(QtCore.Qt.Horizontal)
        self.BTNBOX_MAIN.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.BTNBOX_MAIN.setObjectName("BTNBOX_MAIN")
        self.horizontalLayout_2.addWidget(self.BTNBOX_MAIN)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(Dialog)
        self.BTNBOX_MAIN.accepted.connect(Dialog.accept)
        self.BTNBOX_MAIN.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.BTN_START.setText(_translate("Dialog", "Start"))
        self.BTN_END.setText(_translate("Dialog", "End"))

