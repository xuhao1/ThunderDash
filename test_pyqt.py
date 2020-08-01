# import sys
# from PyQt5 import QtGui, QtCore
#
# class mymainwindow(QtGui.QMainWindow):
#     def __init__(self):
#         QtGui.QMainWindow.__init__(self, None, QtCore.Qt.WindowStaysOnTopHint)
#
# app = QtGui.QApplication(sys.argv)
# mywindow = mymainwindow()
# mywindow.show()
# app.exec_()
# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial

In this example, we create a simple
window in PyQt5.

Author: Jan Bodnar
Website: zetcode.com
Last edited: August 2017
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QToolTip,QPushButton,QLabel
from PyQt5.QtGui import QFont
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        #self.setupUi(self)
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowStaysOnTopHint|
            QtCore.Qt.FramelessWindowHint
        )
        #self.setWindowFlags()
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")

        btn = QLabel('Its Label', self)
        btn.move(50, 50)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
