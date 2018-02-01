# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_big_text_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(977, 655)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_2.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_2.setSpacing(8)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.BTN_SELECTION = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN_SELECTION.sizePolicy().hasHeightForWidth())
        self.BTN_SELECTION.setSizePolicy(sizePolicy)
        self.BTN_SELECTION.setObjectName("BTN_SELECTION")
        self.horizontalLayout_2.addWidget(self.BTN_SELECTION)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.RAD_FASTA = QtWidgets.QRadioButton(self.frame)
        self.RAD_FASTA.setChecked(True)
        self.RAD_FASTA.setObjectName("RAD_FASTA")
        self.horizontalLayout_2.addWidget(self.RAD_FASTA)
        self.RAD_BLAST = QtWidgets.QRadioButton(self.frame)
        self.RAD_BLAST.setObjectName("RAD_BLAST")
        self.horizontalLayout_2.addWidget(self.RAD_BLAST)
        self.BTN_SAVE = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN_SAVE.sizePolicy().hasHeightForWidth())
        self.BTN_SAVE.setSizePolicy(sizePolicy)
        self.BTN_SAVE.setObjectName("BTN_SAVE")
        self.horizontalLayout_2.addWidget(self.BTN_SAVE)
        self.verticalLayout.addWidget(self.frame)
        self.TXT_MAIN = QtWidgets.QTextBrowser(Dialog)
        self.TXT_MAIN.setObjectName("TXT_MAIN")
        self.verticalLayout.addWidget(self.TXT_MAIN)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.BTN_SELECTION.setText(_translate("Dialog", "Selection"))
        self.BTN_SELECTION.setProperty("style", _translate("Dialog", "dropdown"))
        self.RAD_FASTA.setText(_translate("Dialog", "FASTA"))
        self.RAD_BLAST.setText(_translate("Dialog", "BLAST"))
        self.BTN_SAVE.setText(_translate("Dialog", "Save"))
        self.BTN_SAVE.setProperty("style", _translate("Dialog", "dropdown"))
        self.TXT_MAIN.setProperty("style", _translate("Dialog", "console"))

