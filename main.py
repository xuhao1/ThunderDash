from aircraft_game_control import game_aircraft_control
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QToolTip, QPushButton, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QBasicTimer
import sys



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        self.aircraft_con = game_aircraft_control()
        super(MainWindow, self).__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.FramelessWindowHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")

        self.trimroll = QLabel('TrimRoll 0%', self)
        self.trimroll.move(0, 0)
        self.trimroll.setFont(QFont('SansSerif', 15))
        self.trimroll.setFixedSize(400, 50)

        self.roc = QLabel('ROC:NA m/s', self)
        self.roc.move(0, 50)
        self.roc.setFont(QFont('SansSerif', 15))
        self.roc.setFixedSize(400, 50)

        self.aircraft_con.run()
        self.setGeometry(50, 500, 500, 200)

        self.timer = QBasicTimer()
        self.timer.start(10, self)

    def timerEvent(self, e):
        self.trimroll.setText('TrimAil {0:.1f}%'.format(self.aircraft_con.roll_trim))
        self.roc.setText("ROC: {:.1f} m/s".format(self.aircraft_con.get_roc()))

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
