# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './Designer/FrmImport_designer.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(884, 386)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.TXT_FILENAME = QtWidgets.QLineEdit(Dialog)
        self.TXT_FILENAME.setObjectName("TXT_FILENAME")
        self.horizontalLayout.addWidget(self.TXT_FILENAME)
        self.BTN_FILENAME = QtWidgets.QToolButton(Dialog)
        self.BTN_FILENAME.setObjectName("BTN_FILENAME")
        self.horizontalLayout.addWidget(self.BTN_FILENAME)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.RAD_FASTA = QtWidgets.QRadioButton(Dialog)
        self.RAD_FASTA.setObjectName("RAD_FASTA")
        self.verticalLayout.addWidget(self.RAD_FASTA)
        self.RAD_BLAST = QtWidgets.QRadioButton(Dialog)
        self.RAD_BLAST.setObjectName("RAD_BLAST")
        self.verticalLayout.addWidget(self.RAD_BLAST)
        self.RAD_COMPOSITES = QtWidgets.QRadioButton(Dialog)
        self.RAD_COMPOSITES.setObjectName("RAD_COMPOSITES")
        self.verticalLayout.addWidget(self.RAD_COMPOSITES)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.BTN_LOAD = QtWidgets.QPushButton(Dialog)
        self.BTN_LOAD.setObjectName("BTN_LOAD")
        self.horizontalLayout_2.addWidget(self.BTN_LOAD)
        self.BTN_CLEAR = QtWidgets.QPushButton(Dialog)
        self.BTN_CLEAR.setObjectName("BTN_CLEAR")
        self.horizontalLayout_2.addWidget(self.BTN_CLEAR)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.TVW_FILES = QtWidgets.QTreeWidget(Dialog)
        self.TVW_FILES.setObjectName("TVW_FILES")
        self.TVW_FILES.headerItem().setText(0, "1")
        self.verticalLayout.addWidget(self.TVW_FILES)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.BTNBOX_MAIN = QtWidgets.QDialogButtonBox(Dialog)
        self.BTNBOX_MAIN.setOrientation(QtCore.Qt.Horizontal)
        self.BTNBOX_MAIN.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BTNBOX_MAIN.setObjectName("BTNBOX_MAIN")
        self.verticalLayout.addWidget(self.BTNBOX_MAIN)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_3.setStatusTip(_translate("Dialog", "Name of the file to load. This should be BLAST output in TSV format."))
        self.label_3.setWhatsThis(_translate("Dialog", "Name of the file to load. This should be BLAST output in TSV format."))
        self.label_3.setText(_translate("Dialog", "Filename"))
        self.TXT_FILENAME.setStatusTip(_translate("Dialog", "Name of the file to load. This should be BLAST output in TSV format."))
        self.TXT_FILENAME.setWhatsThis(_translate("Dialog", "Name of the file to load. This should be BLAST output in TSV format."))
        self.BTN_FILENAME.setStatusTip(_translate("Dialog", "Name of the file to load. This should be BLAST output in TSV format."))
        self.BTN_FILENAME.setWhatsThis(_translate("Dialog", "Name of the file to load. This should be BLAST output in TSV format."))
        self.BTN_FILENAME.setText(_translate("Dialog", "..."))
        self.RAD_FASTA.setText(_translate("Dialog", "FASTA"))
        self.RAD_BLAST.setText(_translate("Dialog", "BLAST"))
        self.RAD_COMPOSITES.setText(_translate("Dialog", "Composite finder"))
        self.BTN_LOAD.setText(_translate("Dialog", "Load"))
        self.BTN_CLEAR.setText(_translate("Dialog", "Clear"))

