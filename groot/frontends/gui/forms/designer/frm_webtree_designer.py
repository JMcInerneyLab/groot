# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot/frontends/gui/forms/designer/frm_webtree_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1150, 842)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.FRA_TOOLBAR = QtWidgets.QFrame(Dialog)
        self.FRA_TOOLBAR.setObjectName("FRA_TOOLBAR")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.FRA_TOOLBAR)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.BTN_SYSTEM_BROWSER = QtWidgets.QToolButton(self.FRA_TOOLBAR)
        self.BTN_SYSTEM_BROWSER.setMinimumSize(QtCore.QSize(64, 64))
        self.BTN_SYSTEM_BROWSER.setMaximumSize(QtCore.QSize(64, 64))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/groot/external.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_SYSTEM_BROWSER.setIcon(icon)
        self.BTN_SYSTEM_BROWSER.setIconSize(QtCore.QSize(32, 32))
        self.BTN_SYSTEM_BROWSER.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_SYSTEM_BROWSER.setObjectName("BTN_SYSTEM_BROWSER")
        self.horizontalLayout.addWidget(self.BTN_SYSTEM_BROWSER)
        self.BTN_BROWSE_HERE = QtWidgets.QToolButton(self.FRA_TOOLBAR)
        self.BTN_BROWSE_HERE.setMinimumSize(QtCore.QSize(64, 64))
        self.BTN_BROWSE_HERE.setMaximumSize(QtCore.QSize(64, 64))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/groot/internal.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_BROWSE_HERE.setIcon(icon1)
        self.BTN_BROWSE_HERE.setIconSize(QtCore.QSize(32, 32))
        self.BTN_BROWSE_HERE.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_BROWSE_HERE.setObjectName("BTN_BROWSE_HERE")
        self.horizontalLayout.addWidget(self.BTN_BROWSE_HERE)
        self.BTN_SAVE_TO_FILE = QtWidgets.QToolButton(self.FRA_TOOLBAR)
        self.BTN_SAVE_TO_FILE.setMinimumSize(QtCore.QSize(64, 64))
        self.BTN_SAVE_TO_FILE.setMaximumSize(QtCore.QSize(64, 64))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/groot/save.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_SAVE_TO_FILE.setIcon(icon2)
        self.BTN_SAVE_TO_FILE.setIconSize(QtCore.QSize(32, 32))
        self.BTN_SAVE_TO_FILE.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.BTN_SAVE_TO_FILE.setObjectName("BTN_SAVE_TO_FILE")
        self.horizontalLayout.addWidget(self.BTN_SAVE_TO_FILE)
        self.verticalLayout.addWidget(self.FRA_TOOLBAR)
        self.LBL_NO_TREES_WARNING = QtWidgets.QLabel(Dialog)
        self.LBL_NO_TREES_WARNING.setObjectName("LBL_NO_TREES_WARNING")
        self.verticalLayout.addWidget(self.LBL_NO_TREES_WARNING)
        self.LBL_SELECTION_WARNING = QtWidgets.QLabel(Dialog)
        self.LBL_SELECTION_WARNING.setObjectName("LBL_SELECTION_WARNING")
        self.verticalLayout.addWidget(self.LBL_SELECTION_WARNING)
        self.LBL_TITLE = QtWidgets.QLabel(Dialog)
        self.LBL_TITLE.setObjectName("LBL_TITLE")
        self.verticalLayout.addWidget(self.LBL_TITLE)
        self.WIDGET_OTHER = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.WIDGET_OTHER.sizePolicy().hasHeightForWidth())
        self.WIDGET_OTHER.setSizePolicy(sizePolicy)
        self.WIDGET_OTHER.setObjectName("WIDGET_OTHER")
        self.gridLayout = QtWidgets.QGridLayout(self.WIDGET_OTHER)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.LBL_NO_INBUILT = QtWidgets.QLabel(self.WIDGET_OTHER)
        self.LBL_NO_INBUILT.setAlignment(QtCore.Qt.AlignCenter)
        self.LBL_NO_INBUILT.setObjectName("LBL_NO_INBUILT")
        self.gridLayout.addWidget(self.LBL_NO_INBUILT, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.WIDGET_OTHER)
        self.WIDGET_MAIN = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.WIDGET_MAIN.sizePolicy().hasHeightForWidth())
        self.WIDGET_MAIN.setSizePolicy(sizePolicy)
        self.WIDGET_MAIN.setObjectName("WIDGET_MAIN")
        self.verticalLayout.addWidget(self.WIDGET_MAIN)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.BTN_SYSTEM_BROWSER.setText(_translate("Dialog", "System\n"
"browser"))
        self.BTN_BROWSE_HERE.setText(_translate("Dialog", "View\n"
"here"))
        self.BTN_SAVE_TO_FILE.setText(_translate("Dialog", "Save"))
        self.LBL_NO_TREES_WARNING.setText(_translate("Dialog", "You have no trees or graphs, go to the <a href=\"action:view_workflow\">workflow</a>."))
        self.LBL_NO_TREES_WARNING.setProperty("style", _translate("Dialog", "warning"))
        self.LBL_SELECTION_WARNING.setText(_translate("Dialog", "There are no trees in the <a href=\"action:show_selection\">current selection</a>."))
        self.LBL_SELECTION_WARNING.setProperty("style", _translate("Dialog", "warning"))
        self.LBL_TITLE.setText(_translate("Dialog", "TextLabel"))
        self.LBL_TITLE.setProperty("style", _translate("Dialog", "title"))
        self.LBL_NO_INBUILT.setText(_translate("Dialog", "<p>The inbuilt browser has been turned off in the <a href=\"action:view_options\">settings</a>.</p>\n"
"<p>Either <a href=\"action:enable_inbuilt_browser\">enable</a> the inbuilt browser or use the external browser.</p>"))


