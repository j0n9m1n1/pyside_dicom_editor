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
list_files = list()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui_init()
        self.ui_setup()

    def ui_init(self):
        self.tab_widget = QTabWidget()

        self.tab = QWidget()

        self.grid_layout = QGridLayout()

        self.table_widget_image = QTableWidget()
        self.list_widget_log = QListWidget()
        self.progress_image = QProgressBar()

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

        self.table_widget_image.setColumnCount(len(list_tag))
        self.table_widget_image.setHorizontalHeaderLabels(list_tag)
        self.table_widget_image.setRowCount(50)

        self.label_source_path.setText("Source")
        self.line_edit_source_path.setText(r"G:\STORAGE")

        self.label_target_path.setText("Target")
        self.line_edit_target_path.setText(r"G:\STORAGE\modified")

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
            self.table_widget_image,
            1,
            0,
            count_list_tag // 2,
            4,
        )
        self.grid_layout.addWidget(
            self.list_widget_log,
            (count_list_tag // 2) + 1,
            0,
            count_list_tag - (count_list_tag // 2),
            4,
        )

        # 4하면 부족하고, 5하면 넘치고??, 4가 맞음
        self.grid_layout.addWidget(
            self.progress_image, count_list_tag + 1, 0, 1, 4
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
        self.grid_layout2.addWidget(self.list_widget_tag, 1, 0, 5, 1)
        self.grid_layout2.addWidget(self.line_edit_tag, 1, 1)

        self.grid_layout2.addWidget(self.button_tag_add, 2, 1)
        self.grid_layout2.addWidget(self.button_tag_delete, 3, 1)
        self.grid_layout2.addWidget(self.button_tag_up, 4, 1)
        self.grid_layout2.addWidget(self.button_tag_down, 5, 1)

        self.tab2.setLayout(self.grid_layout2)

        # self.setFixedWidth(800)
        # self.setFixedHeight(600)
        self.setCentralWidget(self.tab_widget)
        self.setWindowTitle("DICOM Header Editor")

    def button_clicked_load_files(self):
        input_path = self.line_edit_source_path.text()
        self.insert_file_list_to_table_widget(input_path)

    def button_clicked_save(self):
        if not os.path.exists(self.line_edit_target_path.text()):
            os.makedirs(self.line_edit_target_path.text())

        list_selected_index = self.table_widget_image.selectedIndexes()
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

    def load_progress_bar(self):
        pass

    def save_progress_bar(self):
        pass

    def fetch_next(self):
        pass

    def button_clicked_clear(self):
        [self.line_edit_tags[i].clear() for i in range(len(list_tag))]
        self.line_edit_tags[0].setFocus()

    def insert_file_list_to_table_widget(self, path):
        self.table_widget_image.clear()
        list_ds.clear()

        b_check_pixel_data = self.check_load_pixel_data.isChecked()
        self.table_widget_image.setColumnCount(len(list_tag))
        self.table_widget_image.setHorizontalHeaderLabels(list_tag)

        # 구조가 복잡한 경우도 있어서 walk로 바꿈
        # 근데 확장자가 아예 없는 경우도 있어서 고민중
        # 일단 .dcm만
        for root, dirs, files in os.walk(path):
            if len(files) > 0:
                for file_name in files:
                    if (
                        file_name.lower().endswith("dcm")
                        and len(list_files) < 500
                    ):
                        list_files.append(os.path.join(root, file_name))
        print(len(list_files))
        self.table_widget_image.setRowCount(len(list_files))

        for i, file_path in enumerate(list_files):
            list_ds.append(
                dcmread(
                    file_path,
                    stop_before_pixels=not b_check_pixel_data,
                    force=True,
                )
            )

            for j, tag in enumerate(list_tag):
                try:
                    self.table_widget_image.setItem(
                        i,
                        j,
                        QTableWidgetItem(str(list_ds[i][list_tag[j]].value)),
                    )
                except KeyError:
                    self.table_widget_image.setItem(
                        i,
                        j,
                        QTableWidgetItem(""),
                    )

        # self.table_widget.horizontalHeader().setSectionResizeMode(
        #     QHeaderView.
        # )


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()

# G:\STORAGE\STO01\2022\02\15\CR\
# 00023010_2022-02-15_145906_CR\
# 00023010_2022-02-15_145906_CR\
# 1.2.643.18619941.103772.92022215.91453560.1.4.4.dcm
