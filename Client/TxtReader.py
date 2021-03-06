from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget,QGridLayout,QTextBrowser,\
    QShortcut, QInputDialog

class txtreader(QWidget):
    def __init__(self, parent, book):
        super().__init__()
        filename = book.fname
        self.book = book
        self.book._total_page = 0
        self.widget = parent
        self.content = ""
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.initUI()
        self.open_txt(filename)
        
    def initUI(self):
        self.setGeometry(0,0,3500,3500)
        self.setWindowTitle('txt reader')
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.grid = QGridLayout()

        self.textpart=QTextBrowser()

        self.grid.addWidget(self.textpart)
 
        self.setLayout(self.grid)
        self.show()
        self.init_action()

    def init_action(self):
        ctrl_g = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_G), self)
        ctrl_g.activated.connect(self.jmp_page)
        pgdn = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_M), self)
        pgdn.activated.connect(self.page_down)
        pgup = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Z), self)
        pgup.activated.connect(self.page_up)

    def setContent(self, content):
        self.content = content
        self.showText()

    def showText(self):
        self.textpart.setText(self.content)

    def open_txt(self, filename):
        totpg = int(self.widget.tcp.sendrecv('1 ' + filename))
        self.book._total_page = totpg + 1
        if self.book.page == 1:
            text = self.widget.tcp.sendrecv('2 0')
            self.setContent(text)
        else:
            self.set_page(self.book.page)

    def set_page(self, pgnum):
        if pgnum < 1 or pgnum > self.book.total_page:
            return False
        text = self.widget.tcp.sendrecv('2 ' + str(pgnum))
        self.book.page = pgnum
        self.setContent(text)
        return True

    def page_down(self):
        if self.book.page >= self.book.total_page:
            return
        text = self.widget.tcp.sendrecv('2 0')
        self.book.page = self.book.page + 1
        self.setContent(text)

    def page_up(self):
        self.set_page(self.book.page - 1)

    def close_txt(self):
        print('[Reader]exit txt reader')
        print('[Reader]', self.widget.tcp.sendrecv('3'))

    def jmp_page(self):
        i, okPressed = QInputDialog.getInt(self, "??????", "???????????????(1~%d):" % self.book.total_page, self.book.page)
        if not okPressed:
            return
        self.set_page(i)

    def closeEvent(self, event):
        self.close_txt()
