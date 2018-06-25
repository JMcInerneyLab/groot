# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot_gui/forms/designer/frm_sample_browser_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1066, 738)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.FRA_SAMPLES = QtWidgets.QFrame(self.splitter)
        self.FRA_SAMPLES.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FRA_SAMPLES.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FRA_SAMPLES.setObjectName("FRA_SAMPLES")
        self.gridLayout = QtWidgets.QGridLayout(self.FRA_SAMPLES)
        self.gridLayout.setObjectName("gridLayout")
        self.LBL_SAMPLE_2 = QtWidgets.QLabel(self.FRA_SAMPLES)
        self.LBL_SAMPLE_2.setProperty("style", "heading")
        self.LBL_SAMPLE_2.setObjectName("LBL_SAMPLE_2")
        self.gridLayout.addWidget(self.LBL_SAMPLE_2, 0, 0, 1, 1)
        self.TVW_SAMPLES = QtWidgets.QTreeWidget(self.FRA_SAMPLES)
        self.TVW_SAMPLES.setObjectName("TVW_SAMPLES")
        self.TVW_SAMPLES.headerItem().setText(0, "1")
        self.TVW_SAMPLES.header().setVisible(False)
        self.gridLayout.addWidget(self.TVW_SAMPLES, 1, 0, 1, 1)
        self.frame_2 = QtWidgets.QFrame(self.splitter)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LBL_SAMPLE = QtWidgets.QLabel(self.frame_2)
        self.LBL_SAMPLE.setProperty("style", "heading")
        self.LBL_SAMPLE.setObjectName("LBL_SAMPLE")
        self.verticalLayout.addWidget(self.LBL_SAMPLE)
        self.CMB_FILES = QtWidgets.QComboBox(self.frame_2)
        self.CMB_FILES.setObjectName("CMB_FILES")
        self.verticalLayout.addWidget(self.CMB_FILES)
        self.TXT_DATA = QtWidgets.QTextBrowser(self.frame_2)
        self.TXT_DATA.setTabChangesFocus(True)
        self.TXT_DATA.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.TXT_DATA.setObjectName("TXT_DATA")
        self.verticalLayout.addWidget(self.TXT_DATA)
        self.verticalLayout_2.addWidget(self.splitter)
        self.BTNBOX_MAIN = QtWidgets.QDialogButtonBox(Dialog)
        self.BTNBOX_MAIN.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Help|QtWidgets.QDialogButtonBox.Ok)
        self.BTNBOX_MAIN.setObjectName("BTNBOX_MAIN")
        self.verticalLayout_2.addWidget(self.BTNBOX_MAIN)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.LBL_SAMPLE_2.setText(_translate("Dialog", "Samples"))
        self.LBL_SAMPLE.setText(_translate("Dialog", "Selected"))
        self.TXT_DATA.setProperty("style", _translate("Dialog", "monospaced"))

