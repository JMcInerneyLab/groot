# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_lego_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1071, 864)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout.setSpacing(8)
        self.verticalLayout.setObjectName("verticalLayout")
        self.FRA_TOOLBAR = QtWidgets.QFrame(Dialog)
        self.FRA_TOOLBAR.setFrameShape(QtWidgets.QFrame.Panel)
        self.FRA_TOOLBAR.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FRA_TOOLBAR.setObjectName("FRA_TOOLBAR")
        self.horizontalLayout_23 = QtWidgets.QHBoxLayout(self.FRA_TOOLBAR)
        self.horizontalLayout_23.setContentsMargins(1, 1, 1, 1)
        self.horizontalLayout_23.setSpacing(8)
        self.horizontalLayout_23.setObjectName("horizontalLayout_23")
        self.BTN_REFRESH = QtWidgets.QToolButton(self.FRA_TOOLBAR)
        self.BTN_REFRESH.setMinimumSize(QtCore.QSize(64, 64))
        self.BTN_REFRESH.setMaximumSize(QtCore.QSize(64, 64))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/groot/refresh.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_REFRESH.setIcon(icon)
        self.BTN_REFRESH.setIconSize(QtCore.QSize(32, 32))
        self.BTN_REFRESH.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_REFRESH.setObjectName("BTN_REFRESH")
        self.horizontalLayout_23.addWidget(self.BTN_REFRESH)
        self.BTN_ALIGN = QtWidgets.QToolButton(self.FRA_TOOLBAR)
        self.BTN_ALIGN.setMinimumSize(QtCore.QSize(64, 64))
        self.BTN_ALIGN.setMaximumSize(QtCore.QSize(64, 64))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/groot/move.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_ALIGN.setIcon(icon1)
        self.BTN_ALIGN.setIconSize(QtCore.QSize(32, 32))
        self.BTN_ALIGN.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_ALIGN.setObjectName("BTN_ALIGN")
        self.horizontalLayout_23.addWidget(self.BTN_ALIGN)
        self.BTN_OPTIONS = QtWidgets.QToolButton(self.FRA_TOOLBAR)
        self.BTN_OPTIONS.setMinimumSize(QtCore.QSize(64, 64))
        self.BTN_OPTIONS.setMaximumSize(QtCore.QSize(64, 64))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/groot/settings.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_OPTIONS.setIcon(icon2)
        self.BTN_OPTIONS.setIconSize(QtCore.QSize(32, 32))
        self.BTN_OPTIONS.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_OPTIONS.setObjectName("BTN_OPTIONS")
        self.horizontalLayout_23.addWidget(self.BTN_OPTIONS)
        self.verticalLayout.addWidget(self.FRA_TOOLBAR)
        self.FRA_MAIN = QtWidgets.QFrame(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FRA_MAIN.sizePolicy().hasHeightForWidth())
        self.FRA_MAIN.setSizePolicy(sizePolicy)
        self.FRA_MAIN.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FRA_MAIN.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FRA_MAIN.setObjectName("FRA_MAIN")
        self.verticalLayout.addWidget(self.FRA_MAIN)
        self.LBL_NO_DOMAINS = QtWidgets.QLabel(Dialog)
        self.LBL_NO_DOMAINS.setObjectName("LBL_NO_DOMAINS")
        self.verticalLayout.addWidget(self.LBL_NO_DOMAINS)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.BTN_REFRESH.setToolTip(_translate("Dialog", "<html><head/><body><p>Switch to edge edit mode.</p></body></html>"))
        self.BTN_REFRESH.setStatusTip(_translate("Dialog", "Remove edge"))
        self.BTN_REFRESH.setText(_translate("Dialog", "Refresh"))
        self.BTN_ALIGN.setText(_translate("Dialog", "Move"))
        self.BTN_OPTIONS.setText(_translate("Dialog", "Options"))
        self.LBL_NO_DOMAINS.setText(_translate("Dialog", "<html><head/><body><p>You have no <a href=\"action:view_domains\">domains</a> defined, all genes will be shown as one domain.</p></body></html>"))
        self.LBL_NO_DOMAINS.setProperty("style", _translate("Dialog", "warning"))


