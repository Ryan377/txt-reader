import sys
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QWidget,  \
    QApplication, QFileDialog, QTableWidget, QLabel, QMenu,  \
    QAbstractItemView
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from BookListWindow import Ui_MainWindow
from TxtReader import txtreader
import fitz
from utils import Size, Point, Book
from BookList import TabWidget
from database import maintain_db, read_db, save2db, remove_db
from tcp_client import tcp_client
import os


class Reader(QMainWindow,Ui_MainWindow):
    def __init__(self, parent=None):
        super(Reader, self).__init__(parent)
        self.tcp = tcp_client()
        print('[Client] asking for book information……')
        self.tcp.download("BOOKS.db", "BOOKS_1.db")
        maintain_db()
        print('[Client] successfully update book information')
        self.screen = QDesktopWidget().screenGeometry()
        self.setupUi(self)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.resize(self.screen.width(), self.screen.height() - 75)
        self.table = QTableWidget()
        self.tabwidget = TabWidget()
        self.tabwidget.addTab(self.table, '书架')
        self.setCentralWidget(self.tabwidget)
        self.tabwidget.setTabsClosable(True)
        self.tabwidget.setDocumentMode(True)
        self.tabwidget.tabCloseRequested[int].connect(self.remove_tab)
        self.initUi()


    def initUi(self):
        self.coord = Point(0, 0)
        self.crow = Point(-1, -1)
        self.size = Size(2.6, 2.6)
        self.width = self.screen.width() // 8
        self._set_table_style()
        self._init_bookset()


    def _init_bookset(self):
        self.booklist = [book for book in read_db()]
        self.read_list = [None]
        print('[Client] asking for book covers……')
        for book in self.booklist:
            self.set_icon(book.fname)
        print('[Client] successfully download book covers')


    def get_files(self):
        fnames, _ = QFileDialog.getOpenFileNames(self, 'Open files', './', '(*.pdf, *.txt)')
        return fnames


    def open(self):
        fnames = self.get_files()
        for fname in fnames:
            book = Book(fname)
            if self.filter_book(book):
                self.set_icon(fname)


    def _set_table_style(self):
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.table.setColumnCount(8)
        self.table.setRowCount(5)
        for i in range(8):
            self.table.setColumnWidth(i, self.width)
        for i in range(5):
            self.table.setRowHeight(i, self.width * 4 // 3)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.generate_menu)

    def set_icon(self, fname):
        fname = fname.replace(fname[-3:], 'jpg')
        self.tcp.download(fname)
        label = QLabel(self)
        label.setScaledContents(True)
        p = QPixmap(fname)
        p.scaled(self.width, self.width * 4 // 3, Qt.KeepAspectRatio)
        label.setPixmap(p)
        label.setFixedWidth(self.width)
        label.setFixedHeight(self.width * 4 // 3)
        self.table.setCellWidget(self.coord.x, self.coord.y, label)
        del label
        self.crow.update(self.coord.x, self.coord.y)
        if not self.coord.y % 7 and self.coord.y:
            self.coord.x += 1
            self.coord.y = 0
        else:
            self.coord.y += 1

    def generate_menu(self, pos):
        row_num = col_num = -1
        for i in self.table.selectionModel().selection().indexes():
            row_num = i.row()
            col_num = i.column()
        if (row_num < self.crow.x) or (row_num == self.crow.x and col_num <= self.crow.y):
            menu = QMenu()
            item1 = menu.addAction('开始阅读')
            action = menu.exec_(self.table.mapToGlobal(pos))
            if action == item1:
                index = row_num * 8 + col_num
                book = self.booklist[index]
                if book not in self.read_list and len(self.read_list) < 5:
                    self.read_book(book)


    def read_book(self, book):
        self.txt_reader = txtreader(self, book)

    def book_add_tab(self, title, vbox):
        tab = QWidget()
        tab.setLayout(vbox)
        self.tabwidget.addTab(tab, title)
        self.tabwidget.setCurrentIndex(self.tabwidget.count() - 1)

    def set_current_page(self, right):
        book = self.get_read_book()
        if right and book.page < book.total_page:
            book.page += 1

        elif not right and book.page:
            book.page -= 1

    def switch_page(self, right=True):
        self.set_current_page(right)
        self.set_page()

    def jmp_page(self, new_page=0):
        book = self.get_read_book()
        if 0 <= new_page <= book.total_page:
            book.page = new_page
            self.set_page()

    def get_read_book(self):
        index = self.tabwidget.currentIndex()
        book = self.read_list[index]
        return book
        

    def set_page(self):
        book = self.get_read_book()
        doc = fitz.open(book.fname)
        page = doc.loadPage(book.page)
        tab = self.tabwidget.currentWidget()
        layout = tab.layout()
        widget = layout.itemAt(0).widget()
        label = self.page_pixmap(page)
        doc.close()
        widget.setWidget(label)


    def zoom_book(self, plus=True):
        if plus:
            self.size.x += 0.4
            self.size.y += 0.4
            self.set_page()
        elif not plus:
            self.size.x -= 0.4
            self.size.y -= 0.4
            self.set_page()

    def remove_tab(self, index):
        if index:
            self.tabwidget.removeTab(index)
            
            book = self.read_list.pop(index)
            book.flag = False
     
    def closeEvent(self, event):
        del self.tcp
        remove_db()
        save2db(self.booklist)
        event.accept()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    app = QApplication(sys.argv)
    reader = Reader()
    reader.show()
    sys.exit(app.exec_())
