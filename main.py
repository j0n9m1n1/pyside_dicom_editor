import sys, os
from pydicom import dcmread
from PySide6.QtCore import *
from PySide6.QtWidgets import *

list_tag = ["PatientID", 
            "PatientName",  
            "PatientBirthDate",  
            "PatientAge",
            "StudyDate",
            "StudyTime",
            "SeriesDate",
            "SeriesTime",
            "ContentDate",
            "ContentTime",
            "StudyInstanceUID",
            "WindowCenter",
            "WindowWidth"
            ]

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        # layout = QVBoxLayout()
        self.ui()
        
    def ui(self):
        
        self.grid_layout = QGridLayout()
        self.table_widget = QTableWidget()
        
        # button = QPushButton("TEST")

        self.table_widget.setColumnCount(len(list_tag))
        self.table_widget.setHorizontalHeaderLabels(list_tag)
        self.table_widget.setRowCount(50)

        self.line_edit_dcm_path = QLineEdit(r"G:\아이디\SERIES1")
        self.button_confirm_path = QPushButton("GET")
        self.button_confirm_path.clicked.connect(self.button_clicked_confirm_path)
        
        self.grid_layout.addWidget(self.line_edit_dcm_path, 0, 0)
        self.grid_layout.addWidget(self.button_confirm_path, 0, 1)
        


        # layout.addWidget(text_edit_dcm_path)
        self.grid_layout.addWidget(self.table_widget, 1, 0, 1, 0)
        # layout.addWidget(table_widget)
        # layout.addWidget(button)

        # grid_layout.addLayout(layout, 0, 0)
        self.widget = QWidget()
        self.widget.setLayout(self.grid_layout)
        
        self.setFixedWidth(800)
        self.setFixedHeight(600)
        
        self.setCentralWidget(self.widget)
        self.setWindowTitle("My App")
        # line_edit_dcm_path.toPlainText()

    def button_clicked_confirm_path(self):
        # print(path)
        # sender = self.sender()
        input_path = self.line_edit_dcm_path.text()
        print(input_path)
        self.insert_file_list_to_table_widget(input_path)
        
    def insert_file_list_to_table_widget(self, path):
        dict_files = os.listdir(path)
        print(dict_files)
        for i, file_name in enumerate(dict_files):
            file_path = os.path.join(path, file_name)
            ds = dcmread(file_path, stop_before_pixels=True, force=True)
            # print(ds)
            for j, tag in enumerate(list_tag):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(ds[list_tag[j]].value)))
        
                # print(ds[list_tag[j]].value)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()