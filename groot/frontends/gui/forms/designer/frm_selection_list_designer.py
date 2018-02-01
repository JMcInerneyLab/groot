# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_selection_list_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1049, 770)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setContentsMargins(8, 8, 8, 8)
        self.gridLayout.setSpacing(8)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_22 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_22.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_22.setSpacing(8)
        self.horizontalLayout_22.setObjectName("horizontalLayout_22")
        self.LBL_SELECTION_INFO = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_SELECTION_INFO.sizePolicy().hasHeightForWidth())
        self.LBL_SELECTION_INFO.setSizePolicy(sizePolicy)
        self.LBL_SELECTION_INFO.setObjectName("LBL_SELECTION_INFO")
        self.horizontalLayout_22.addWidget(self.LBL_SELECTION_INFO)
        self.RAD_GENES = QtWidgets.QRadioButton(self.frame)
        self.RAD_GENES.setChecked(True)
        self.RAD_GENES.setObjectName("RAD_GENES")
        self.horizontalLayout_22.addWidget(self.RAD_GENES)
        self.RAD_DOMAINS = QtWidgets.QRadioButton(self.frame)
        self.RAD_DOMAINS.setObjectName("RAD_DOMAINS")
        self.horizontalLayout_22.addWidget(self.RAD_DOMAINS)
        self.RAD_EDGES = QtWidgets.QRadioButton(self.frame)
        self.RAD_EDGES.setObjectName("RAD_EDGES")
        self.horizontalLayout_22.addWidget(self.RAD_EDGES)
        self.RAD_COMPONENTS = QtWidgets.QRadioButton(self.frame)
        self.RAD_COMPONENTS.setObjectName("RAD_COMPONENTS")
        self.horizontalLayout_22.addWidget(self.RAD_COMPONENTS)
        self.RAD_OTHER = QtWidgets.QRadioButton(self.frame)
        self.RAD_OTHER.setObjectName("RAD_OTHER")
        self.horizontalLayout_22.addWidget(self.RAD_OTHER)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 2)
        self.LST_MAIN = QtWidgets.QTreeWidget(Dialog)
        self.LST_MAIN.setObjectName("LST_MAIN")
        self.LST_MAIN.headerItem().setText(0, "1")
        self.LST_MAIN.header().setVisible(False)
        self.gridLayout.addWidget(self.LST_MAIN, 2, 0, 1, 1)
        self.LBL_NO_DATA_WARNING = QtWidgets.QLabel(Dialog)
        self.LBL_NO_DATA_WARNING.setObjectName("LBL_NO_DATA_WARNING")
        self.gridLayout.addWidget(self.LBL_NO_DATA_WARNING, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.LBL_SELECTION_INFO.setText(_translate("Dialog", "TextLabel"))
        self.LBL_SELECTION_INFO.setProperty("style", _translate("Dialog", "heading"))
        self.RAD_GENES.setText(_translate("Dialog", "Genes"))
        self.RAD_DOMAINS.setText(_translate("Dialog", "Domains"))
        self.RAD_EDGES.setText(_translate("Dialog", "Edges"))
        self.RAD_COMPONENTS.setText(_translate("Dialog", "Components"))
        self.RAD_OTHER.setText(_translate("Dialog", "Other"))
        self.LBL_NO_DATA_WARNING.setText(_translate("Dialog", "<html><head/><body><p>There is no data. <a href=\"file_load\"><span style=\" text-decoration: underline; color:#0000ff;\">Load</span></a> some data first.</p></body></html>"))
        self.LBL_NO_DATA_WARNING.setProperty("style", _translate("Dialog", "warning"))

