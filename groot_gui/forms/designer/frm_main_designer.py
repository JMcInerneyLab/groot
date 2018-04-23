# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/groot/groot_gui/forms/designer/frm_main_designer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1184, 805)
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.FRA_FILE = QtWidgets.QGroupBox(self.frame)
        self.FRA_FILE.setObjectName("FRA_FILE")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.FRA_FILE)
        self.horizontalLayout_2.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout.addWidget(self.FRA_FILE)
        self.FRA_VISUALISERS = QtWidgets.QGroupBox(self.frame)
        self.FRA_VISUALISERS.setObjectName("FRA_VISUALISERS")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.FRA_VISUALISERS)
        self.horizontalLayout_3.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout.addWidget(self.FRA_VISUALISERS)
        self.FRA_WORKFLOW = QtWidgets.QGroupBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.FRA_WORKFLOW.sizePolicy().hasHeightForWidth())
        self.FRA_WORKFLOW.setSizePolicy(sizePolicy)
        self.FRA_WORKFLOW.setObjectName("FRA_WORKFLOW")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.FRA_WORKFLOW)
        self.horizontalLayout_4.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout.addWidget(self.FRA_WORKFLOW)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)
        self.MDI_AREA = QtWidgets.QMdiArea(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MDI_AREA.sizePolicy().hasHeightForWidth())
        self.MDI_AREA.setSizePolicy(sizePolicy)
        self.MDI_AREA.setTabsClosable(True)
        self.MDI_AREA.setTabsMovable(True)
        self.MDI_AREA.setTabShape(QtWidgets.QTabWidget.Triangular)
        self.MDI_AREA.setObjectName("MDI_AREA")
        self.gridLayout.addWidget(self.MDI_AREA, 1, 0, 1, 1)
        self.FRA_STATUSBAR = QtWidgets.QFrame(self.centralwidget)
        self.FRA_STATUSBAR.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.FRA_STATUSBAR.setFrameShadow(QtWidgets.QFrame.Raised)
        self.FRA_STATUSBAR.setObjectName("FRA_STATUSBAR")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.FRA_STATUSBAR)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.BTN_STATUS = QtWidgets.QToolButton(self.FRA_STATUSBAR)
        self.BTN_STATUS.setMinimumSize(QtCore.QSize(24, 24))
        self.BTN_STATUS.setMaximumSize(QtCore.QSize(24, 24))
        self.BTN_STATUS.setStyleSheet("QToolButton\n"
"{\n"
"border:none;\n"
"}\n"
"\n"
"QToolButton:hover\n"
"{\n"
"border: 2px outset gray;\n"
"}\n"
"\n"
"QToolButton:pressed\n"
"{\n"
"border: 2px inset gray;\n"
"}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/groot/accept.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.BTN_STATUS.setIcon(icon)
        self.BTN_STATUS.setIconSize(QtCore.QSize(24, 24))
        self.BTN_STATUS.setAutoRaise(True)
        self.BTN_STATUS.setObjectName("BTN_STATUS")
        self.horizontalLayout_5.addWidget(self.BTN_STATUS)
        self.LBL_STATUS = QtWidgets.QLabel(self.FRA_STATUSBAR)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_STATUS.sizePolicy().hasHeightForWidth())
        self.LBL_STATUS.setSizePolicy(sizePolicy)
        self.LBL_STATUS.setObjectName("LBL_STATUS")
        self.horizontalLayout_5.addWidget(self.LBL_STATUS)
        self.LBL_FILENAME = QtWidgets.QLabel(self.FRA_STATUSBAR)
        self.LBL_FILENAME.setScaledContents(True)
        self.LBL_FILENAME.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.LBL_FILENAME.setObjectName("LBL_FILENAME")
        self.horizontalLayout_5.addWidget(self.LBL_FILENAME)
        self.gridLayout.addWidget(self.FRA_STATUSBAR, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1184, 22))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.FRA_FILE.setTitle(_translate("MainWindow", "File"))
        self.FRA_VISUALISERS.setTitle(_translate("MainWindow", "Visualisers"))
        self.FRA_WORKFLOW.setTitle(_translate("MainWindow", "Workflow"))
        self.LBL_STATUS.setText(_translate("MainWindow", "Everything is good."))
        self.LBL_FILENAME.setText(_translate("MainWindow", "."))


