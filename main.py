#!/usr/bin/python

from PyQt4 import QtGui, QtCore
from random import randint
import sys
from threading import Thread
from time import sleep

class Painter(QtGui.QWidget):
    def __init__(self, parent, GRIDWIDTH, GRIDHEIGHT):
        super(Painter, self).__init__()
        self.parent = parent
        self.TILE = 5
        self.GRIDWIDTH = GRIDWIDTH
        self.GRIDHEIGHT = GRIDHEIGHT

    def sizeHint(self):
        return QtCore.QSize((self.GRIDWIDTH<<self.TILE)+1, (self.GRIDHEIGHT<<self.TILE)+1)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setPen(QtGui.QPen(QtCore.Qt.black, 1))
        LUT = {-1: QtCore.Qt.darkGray, 0:QtCore.Qt.transparent, 1:QtCore.Qt.darkRed, 2:QtCore.Qt.darkGreen, 3:QtCore.Qt.darkBlue}
        for x in xrange(self.GRIDWIDTH):
            for y in xrange(self.GRIDHEIGHT):
                qp.setBrush(LUT[self.parent.grid[x][y]])
                qp.drawRect(x<<self.TILE, y<<self.TILE, 1<<self.TILE, 1<<self.TILE)
        qp.setBrush(QtCore.Qt.darkMagenta)
        (probeX, probeY) = self.parent.probe.location()
        qp.drawEllipse(probeX<<self.TILE, probeY<<self.TILE, 1<<self.TILE, 1<<self.TILE)
        qp.end()

class Probe():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.status = "alive"
        self.NUMORES = 3
        self.load = [0]*self.NUMORES
        self.loadmax = [1]*self.NUMORES

    def move(self, dx, dy):
        if self.status == "alive":
            if dx < -1 or dx > 1 or dy < -1 or dy > 1:
                self.invalid("bad move order")
            else:
                self.x += dx
                self.y += dy
        return self.x, self.y

    def location(self):
        return (self.x, self.y)

    def loot(self, item):
        if self.load[item-1] < self.loadmax[item-1]:
            self.load[item-1] += 1
            return True
        return False

    def unload(self):
        print self.load # TODO score ore
        self.load = [0]*self.NUMORES

    def invalid(self, error):
        self.status = "dead: {}".format(error)

    def __str__(self):
        load = [str(self.load[i])+"/"+str(self.loadmax[i]) for i in range(self.NUMORES)]
        return "Probe status: {}\nLocation ({},{})\nLoad ({})".format(self.status, self.x, self.y, load)

class Main(QtGui.QWidget):
    def __init__(self):
        super(Main, self).__init__()
        self.setWindowTitle("Micro Game");
        self.GRIDWIDTH = 16
        self.GRIDHEIGHT = 16
        self.grid = []
        for x in xrange(self.GRIDWIDTH):
            self.grid.append([0]*self.GRIDHEIGHT)
        for i in xrange(10):
            x = randint(0, self.GRIDWIDTH-1)
            y = randint(0, self.GRIDHEIGHT-1)
            self.grid[x][y] = randint(1,3)
        self.grid[0][0] = -1
        self.probe = Probe(0, 0)
        self.runButton = QtGui.QPushButton("Run")
        self.runButton.clicked.connect(self.clickRunStop)
        self.clearButton = QtGui.QPushButton("Clear")
        self.clearButton.clicked.connect(self.clickClearReset)
        self.statusLabel = QtGui.QLabel()
        self.textBox = QtGui.QTextEdit("def function():")
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.runButton)
        vbox.addWidget(self.clearButton)
        vbox.addWidget(self.statusLabel)
        vbox.addWidget(self.textBox)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(Painter(self, self.GRIDWIDTH, self.GRIDHEIGHT))
        hbox.addLayout(vbox)
        self.setLayout(hbox)
        self.show()
        self.threadIsRunning = False
        self.threadShouldRun = False

    def paintEvent(self, event):
        self.statusLabel.setText(str(self.probe))

    def closeEvent(self, event):
        self.threadShouldRun = False
        if hasattr(self, "runThread"):
            self.runThread.join()
        event.accept()

    def clickRunStop(self):
        if self.runButton.text() == "Run":
            if not self.threadIsRunning:
                self.threadIsRunning = True
                self.threadShouldRun = True
                self.runThread = Thread(name='Run thread')
                self.runThread.run = self.run
                self.runThread.start()
                self.runButton.setText("Stop")
        else:
            self.threadShouldRun = False
            self.runButton.setText("Stopping...")

    def clickClearReset(self):
        if self.clearButton.text() == "Clear":
            self.clearButton.setText("Reset")
        else:
            self.clearButton.setText("Clear")

    def run(self):
        try:
            exec(self.textBox.toPlainText().toUtf8().data())
            while self.threadShouldRun:
                (dx,dy) = function()
                (x, y) = self.probe.move(dx, dy)
                if x < 0 or x >= self.GRIDWIDTH or y < 0 or y >= self.GRIDHEIGHT:
                    self.probe.invalid("went out of bounds")
                    break
                if self.grid[x][y] > 0:
                    if self.probe.loot(self.grid[x][y]):
                        self.grid[x][y] = 0
                elif self.grid[x][y] == -1:
                    self.probe.unload()
                self.update()
                sleep(1.0)
        except Exception as e:
            print e
        finally:
            self.update()
            self.threadIsRunning = False
            self.runButton.setText("Run")

def main():
    app = QtGui.QApplication(sys.argv)
    m = Main()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

