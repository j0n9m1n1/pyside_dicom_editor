import sys, os
from pydicom import dcmread
from PySide6.QtCore import *
from PySide6.QtWidgets import *

list_tag = [
    "PatientID",
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
    "SOPInstanceUID",
    "WindowCenter",
    "WindowWidth",
]
list_ds = list()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui_init()
        self.ui_setup()

    def ui_init(self):
        self.tab_widget = QTabWidget()

        self.tab = QWidget()

        self.grid_layout = QGridLayout()

        self.table_widget = QTableWidget()

        self.label_source_path = QLabel()
        self.line_edit_source_path = QLineEdit()

        self.label_target_path = QLabel()
        self.line_edit_target_path = QLineEdit()

        self.check_load_pixel_data = QCheckBox()

        self.button_load_files = QPushButton()

        self.button_save = QPushButton()
        self.button_clear = QPushButton()

        self.label_tags = [QLabel() for x in range(len(list_tag))]
        self.line_edit_tags = [QLineEdit() for x in range(len(list_tag))]

        self.tab2 = QWidget()
        self.grid_layout2 = QGridLayout()
        self.label_tag_list = QLabel()
        self.list_widget_tag = QListWidget()
        self.line_edit_tag = QLineEdit()
        self.button_tag_add = QPushButton()
        self.button_tag_delete = QPushButton()
        self.button_tag_up = QPushButton()
        self.button_tag_down = QPushButton()

    def ui_setup(self):
        count_list_tag = len(list_tag)
        self.tab_widget.addTab(self.tab, "Edit")

        self.table_widget.setColumnCount(len(list_tag))
        self.table_widget.setHorizontalHeaderLabels(list_tag)
        self.table_widget.setRowCount(50)

        self.label_source_path.setText("Source")
        self.line_edit_source_path.setText(r"D:\jm")

        self.label_target_path.setText("Target")
        self.line_edit_target_path.setText(r"D:\jm\Modified")

        self.check_load_pixel_data.setText("Pixel Data")
        self.check_load_pixel_data.setChecked(True)

        self.button_load_files.setText("Load")
        self.button_load_files.clicked.connect(self.button_clicked_load_files)

        self.button_save.setText("Save")
        self.button_save.clicked.connect(self.button_clicked_save)
        self.button_clear.setText("Clear")
        self.button_clear.clicked.connect(self.button_clicked_clear)

        # 호기심 해결겸 list comp
        [self.label_tags[i].setText(tag) for i, tag in enumerate(list_tag)]

        self.grid_layout.addWidget(self.label_source_path, 0, 0)
        self.grid_layout.addWidget(self.line_edit_source_path, 0, 1)
        self.grid_layout.addWidget(self.label_target_path, 0, 2)
        self.grid_layout.addWidget(self.line_edit_target_path, 0, 3)
        self.grid_layout.addWidget(self.check_load_pixel_data, 0, 4)
        self.grid_layout.addWidget(self.button_load_files, 0, 5)

        # 호기심 해결겸 list comp
        [
            self.grid_layout.addWidget(self.label_tags[i], i + 1, 4)
            for i in range(count_list_tag)
        ]
        [
            self.grid_layout.addWidget(self.line_edit_tags[i], i + 1, 5)
            for i in range(count_list_tag)
        ]

        self.grid_layout.addWidget(
            self.table_widget, 1, 0, count_list_tag + 1, 4
        )
        self.grid_layout.addWidget(self.button_save, count_list_tag + 1, 4)
        self.grid_layout.addWidget(self.button_clear, count_list_tag + 1, 5)

        self.tab.setLayout(self.grid_layout)

        self.tab_widget.addTab(self.tab2, "Setting")
        self.label_tag_list.setText("Tag List")
        self.list_widget_tag.addItems(list_tag)

        self.button_tag_add.setText("Add")
        self.button_tag_delete.setText("Delete")
        self.button_tag_up.setText("Up")
        self.button_tag_down.setText("Down")

        self.grid_layout2.addWidget(self.label_tag_list, 0, 0)
        self.grid_layout2.addWidget(self.list_widget_tag, 1, 0)
        self.grid_layout2.addWidget(self.line_edit_tag, 1, 1)

        self.grid_layout2.addWidget(self.button_tag_add, 1, 1)
        self.grid_layout2.addWidget(self.button_tag_delete, 2, 1)
        self.grid_layout2.addWidget(self.button_tag_up, 3, 1)
        self.grid_layout2.addWidget(self.button_tag_down, 4, 1)

        self.tab2.setLayout(self.grid_layout2)

        # self.setFixedWidth(800)
        # self.setFixedHeight(600)
        self.setCentralWidget(self.tab_widget)
        self.setWindowTitle("DICOM Header Editor")

    def button_clicked_load_files(self):
        input_path = self.line_edit_source_path.text()
        print(input_path)
        self.insert_file_list_to_table_widget(input_path)

    def button_clicked_save(self):
        if not os.path.exists(self.line_edit_target_path.text()):
            os.makedirs(self.line_edit_target_path.text())

        list_selected_index = self.table_widget.selectedIndexes()
        for i, item in enumerate(list_selected_index):
            for j, tag in enumerate(list_tag):
                if self.line_edit_tags[j].text() != "":
                    print(
                        f"[{tag}]Before: {list_ds[item.row()][tag].value}",
                        end=" ",
                    )
                    list_ds[item.row()][tag].value = self.line_edit_tags[
                        j
                    ].text()
                    print(f"After: {list_ds[item.row()][tag].value}")
                    # 생각해보니 파일명을 가지고 있지 않음
                    str_out_file_name = f'{item.row()}_{list_ds[item.row()]["PatientID"].value}_{list_ds[item.row()]["PatientName"].value}_{list_ds[item.row()]["SOPInstanceUID"].value}.dcm'
                    list_ds[item.row()].save_as(
                        os.path.join(
                            self.line_edit_target_path.text(), str_out_file_name
                        )
                    )

    def reload_table_widget(self):
        pass

    def button_clicked_clear(self):
        [self.line_edit_tags[i].clear() for i in range(len(list_tag))]
        self.line_edit_tags[0].setFocus()

    def insert_file_list_to_table_widget(self, path):
        self.table_widget.clear()
        list_ds.clear()

        b_check_pixel_data = self.check_load_pixel_data.isChecked()
        self.table_widget.setColumnCount(len(list_tag))
        self.table_widget.setHorizontalHeaderLabels(list_tag)

        dict_files = os.listdir(path)

        self.table_widget.setRowCount(len(dict_files))

        for i, file_name in enumerate(dict_files):
            file_path = os.path.join(path, file_name)
            list_ds.append(
                dcmread(
                    file_path,
                    stop_before_pixels=not b_check_pixel_data,
                    force=True,
                )
            )

            for j, tag in enumerate(list_tag):
                self.table_widget.setItem(
                    i, j, QTableWidgetItem(str(list_ds[i][list_tag[j]].value))
                )
                # print(ds[list_tag[j]].value)

        self.table_widget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
