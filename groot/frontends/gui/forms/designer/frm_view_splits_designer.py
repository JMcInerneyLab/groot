# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_view_splits_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1171, 822)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.FRA_TOOLBAR = QtWidgets.QFrame(Dialog)
        self.FRA_TOOLBAR.setObjectName("FRA_TOOLBAR")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.FRA_TOOLBAR)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.BTN_CLEAR_ = QtWidgets.QToolButton(self.FRA_TOOLBAR)
        self.BTN_CLEAR_.setMinimumSize(QtCore.QSize(64, 64))
        self.BTN_CLEAR_.setMaximumSize(QtCore.QSize(64, 64))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/groot/empty.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_CLEAR_.setIcon(icon)
        self.BTN_CLEAR_.setIconSize(QtCore.QSize(32, 32))
        self.BTN_CLEAR_.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_CLEAR_.setObjectName("BTN_CLEAR_")
        self.horizontalLayout_3.addWidget(self.BTN_CLEAR_)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.verticalLayout.addItem(spacerItem)
        self.LBL_ADDFILTER = QtWidgets.QLabel(self.FRA_TOOLBAR)
        self.LBL_ADDFILTER.setAlignment(QtCore.Qt.AlignCenter)
        self.LBL_ADDFILTER.setObjectName("LBL_ADDFILTER")
        self.verticalLayout.addWidget(self.LBL_ADDFILTER)
        self.TXT_ADDFILTER = QtWidgets.QLineEdit(self.FRA_TOOLBAR)
        self.TXT_ADDFILTER.setObjectName("TXT_ADDFILTER")
        self.verticalLayout.addWidget(self.TXT_ADDFILTER)
        spacerItem1 = QtWidgets.QSpacerItem(20, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.BTN_REFRESH = QtWidgets.QToolButton(self.FRA_TOOLBAR)
        self.BTN_REFRESH.setMinimumSize(QtCore.QSize(64, 64))
        self.BTN_REFRESH.setMaximumSize(QtCore.QSize(64, 64))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/groot/refresh.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_REFRESH.setIcon(icon1)
        self.BTN_REFRESH.setIconSize(QtCore.QSize(32, 32))
        self.BTN_REFRESH.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_REFRESH.setObjectName("BTN_REFRESH")
        self.horizontalLayout_3.addWidget(self.BTN_REFRESH)
        self.verticalLayout_2.addWidget(self.FRA_TOOLBAR)
        self.LBL_TITLE = QtWidgets.QLabel(Dialog)
        self.LBL_TITLE.setObjectName("LBL_TITLE")
        self.verticalLayout_2.addWidget(self.LBL_TITLE)
        self.LST_MAIN = QtWidgets.QTreeWidget(Dialog)
        self.LST_MAIN.setAlternatingRowColors(True)
        self.LST_MAIN.setRootIsDecorated(False)
        self.LST_MAIN.setItemsExpandable(False)
        self.LST_MAIN.setExpandsOnDoubleClick(False)
        self.LST_MAIN.setObjectName("LST_MAIN")
        self.LST_MAIN.headerItem().setText(0, "1")
        self.verticalLayout_2.addWidget(self.LST_MAIN)
        self.LBL_SELECTION_INFO = QtWidgets.QLabel(Dialog)
        self.LBL_SELECTION_INFO.setFrameShape(QtWidgets.QFrame.Box)
        self.LBL_SELECTION_INFO.setFrameShadow(QtWidgets.QFrame.Raised)
        self.LBL_SELECTION_INFO.setAlignment(QtCore.Qt.AlignCenter)
        self.LBL_SELECTION_INFO.setObjectName("LBL_SELECTION_INFO")
        self.verticalLayout_2.addWidget(self.LBL_SELECTION_INFO)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.BTN_CLEAR_.setToolTip(_translate("Dialog", "<html><head/><body><p>Switch to edge edit mode.</p></body></html>"))
        self.BTN_CLEAR_.setStatusTip(_translate("Dialog", "Remove edge"))
        self.BTN_CLEAR_.setText(_translate("Dialog", "Clear"))
        self.LBL_ADDFILTER.setText(_translate("Dialog", "Additional filter"))
        self.BTN_REFRESH.setToolTip(_translate("Dialog", "<html><head/><body><p>Switch to edge edit mode.</p></body></html>"))
        self.BTN_REFRESH.setStatusTip(_translate("Dialog", "Remove edge"))
        self.BTN_REFRESH.setText(_translate("Dialog", "Refresh"))
        self.LBL_TITLE.setText(_translate("Dialog", "Text goes here"))
        self.LBL_TITLE.setProperty("style", _translate("Dialog", "title"))
        self.LBL_SELECTION_INFO.setToolTip(_translate("Dialog", "Baum-Ragan representation"))
        self.LBL_SELECTION_INFO.setText(_translate("Dialog", "Text goes here"))


