import sys, os, time, pickle
from threading import Thread
from pydicom import dcmread
from PySide6.QtCore import *
from PySide6.QtWidgets import *

with open("list_current_tags.pickle", "rb") as f:
    list_current_tags = pickle.load(f)  # (파일)

with open("list_available_tags.pickle", "rb") as f:
    list_available_tags = pickle.load(f)  # (파일)

list_ds = list()
list_files = list()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui_init()
        self.ui_init2()
        self.focus_list_widget = None

    def ui_init(self):
        self.tab_widget = QTabWidget()

        self.tab = QWidget()

        self.grid_layout = QGridLayout()

        self.table_widget_image = QTableWidget()
        self.list_widget_log = QListWidget()
        self.progress_bar = QProgressBar()

        self.label_source_path = QLabel()
        self.line_edit_source_path = QLineEdit()

        self.label_target_path = QLabel()
        self.line_edit_target_path = QLineEdit()

        self.check_load_pixel_data = QCheckBox()

        self.button_load_files = QPushButton()

        self.button_save_dcm = QPushButton()
        self.button_clear = QPushButton()

        self.label_tags = [QLabel() for x in range(len(list_current_tags))]
        self.line_edit_tags = [
            QLineEdit() for x in range(len(list_current_tags))
        ]

        self.tab2 = QWidget()
        self.grid_layout2 = QGridLayout()

        self.label_current_tags = QLabel()
        self.label_available_tags = QLabel()

        self.list_widget_current_tags = QListWidget()
        self.list_widget_available_tags = QListWidget()

        self.line_edit_tag = QLineEdit()

        self.button_tag_add = QPushButton()
        self.button_tag_delete = QPushButton()
        self.button_tag_up = QPushButton()
        self.button_tag_down = QPushButton()
        self.button_tag_move_to_current = QPushButton()
        self.button_tag_move_to_available = QPushButton()
        self.button_save_tag = QPushButton()

    def ui_init2(self):
        count_list_tag = len(list_current_tags)
        self.tab_widget.addTab(self.tab, "Edit")

        self.table_widget_image.setColumnCount(len(list_current_tags))
        self.table_widget_image.setHorizontalHeaderLabels(list_current_tags)
        self.table_widget_image.setRowCount(50)

        self.label_source_path.setText("Source")
        self.line_edit_source_path.setText(r"G:\STORAGE")

        self.label_target_path.setText("Target")
        self.line_edit_target_path.setText(r"G:\STORAGE\modified")

        self.check_load_pixel_data.setText("Pixel Data")
        self.check_load_pixel_data.setChecked(True)

        self.button_load_files.setText("Load")
        self.button_load_files.clicked.connect(self.button_clicked_load_files)

        self.button_save_dcm.setText("Save")
        self.button_save_dcm.clicked.connect(self.button_clicked_save)

        self.button_clear.setText("Clear")
        self.button_clear.clicked.connect(self.button_clicked_clear)

        # 호기심 해결겸 list comp
        [
            self.label_tags[i].setText(tag)
            for i, tag in enumerate(list_current_tags)
        ]

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
            self.progress_bar, count_list_tag + 1, 0, 1, 4
        )

        self.grid_layout.addWidget(self.button_save_dcm, count_list_tag + 1, 4)
        self.grid_layout.addWidget(self.button_clear, count_list_tag + 1, 5)

        self.tab.setLayout(self.grid_layout)

        self.tab_widget.addTab(self.tab2, "Setting")

        self.label_current_tags.setText("Current Tags")
        self.label_available_tags.setText("Available Tags")

        self.list_widget_current_tags.itemClicked.connect(
            self.list_widget_current_tags_item_clicked
        )
        self.list_widget_available_tags.itemClicked.connect(
            self.list_widget_available_tags_item_clicked
        )
        self.list_widget_current_tags.addItems(list_current_tags)
        self.list_widget_available_tags.addItems(list_available_tags)

        self.button_tag_add.setText("Add")
        self.button_tag_add.clicked.connect(self.button_clicked_tag_add)
        self.button_tag_delete.setText("Delete")
        self.button_tag_delete.clicked.connect(self.button_clicked_tag_delete)
        self.button_tag_up.setText("Up")
        self.button_tag_up.clicked.connect(self.button_clicked_tag_up)
        self.button_tag_down.setText("Down")
        self.button_tag_down.clicked.connect(self.button_clicked_tag_down)
        self.button_save_tag.setText("Save")
        self.button_save_tag.clicked.connect(self.button_clicked_tag_save)
        self.button_tag_move_to_current.setText("Move to Current")
        self.button_tag_move_to_current.clicked.connect(
            self.button_clicked_tag_move_to_current
        )
        self.button_tag_move_to_available.setText("Move to Available")
        self.button_tag_move_to_available.clicked.connect(
            self.button_clicked_tag_move_to_available
        )

        self.grid_layout2.addWidget(self.label_current_tags, 0, 0)
        self.grid_layout2.addWidget(self.list_widget_current_tags, 1, 0)

        self.grid_layout2.addWidget(self.label_available_tags, 0, 1)
        self.grid_layout2.addWidget(self.list_widget_available_tags, 1, 1)

        self.grid_layout2.addWidget(self.line_edit_tag, 1, 2)
        self.grid_layout2.addWidget(self.button_tag_add, 2, 2)
        self.grid_layout2.addWidget(self.button_tag_delete, 3, 2)
        self.grid_layout2.addWidget(self.button_tag_up, 4, 2)
        self.grid_layout2.addWidget(self.button_tag_down, 5, 2)
        self.grid_layout2.addWidget(self.button_save_tag, 6, 2)
        self.grid_layout2.addWidget(self.button_tag_move_to_current, 7, 2)
        self.grid_layout2.addWidget(self.button_tag_move_to_available, 8, 2)

        self.tab2.setLayout(self.grid_layout2)

        self.setCentralWidget(self.tab_widget)
        self.setWindowTitle("DICOM Header Editor")

    def button_clicked_load_files(self):
        self.t1 = Thread(target=self.insert_file_list_to_table_widget)
        self.t1.start()

    def button_clicked_save(self):
        if not os.path.exists(self.line_edit_target_path.text()):
            os.makedirs(self.line_edit_target_path.text())

        list_selected_index = self.table_widget_image.selectedIndexes()
        for i, item in enumerate(list_selected_index):
            for j, tag in enumerate(list_current_tags):
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

    def list_widget_current_tags_item_clicked(self):
        self.focus_list_widget = self.list_widget_current_tags

    def list_widget_available_tags_item_clicked(self):
        self.focus_list_widget = self.list_widget_available_tags

    def reload_table_widget(self):
        pass

    def button_clicked_tag_add(self):
        pass

    def button_clicked_tag_delete(self):
        current_row = self.focus_list_widget.currentRow()

        self.focus_list_widget.takeItem(current_row)

        if current_row != self.focus_list_widget.count():
            self.focus_list_widget.setCurrentRow(current_row)
        else:
            self.focus_list_widget.setCurrentRow(current_row - 1)

        self.focus_list_widget.setFocus()

    def button_clicked_tag_up(self):
        current_row = self.focus_list_widget.currentRow()

        if current_row != 0:
            selected_item = self.focus_list_widget.currentItem()
            above_item = self.focus_list_widget.itemAt(current_row - 1, 0)

            self.focus_list_widget.takeItem(current_row)
            self.focus_list_widget.insertItem(current_row, above_item)
            self.focus_list_widget.insertItem(current_row - 1, selected_item)
            self.focus_list_widget.setCurrentRow(current_row - 1)

        self.focus_list_widget.setFocus()

    def button_clicked_tag_down(self):
        current_row = self.focus_list_widget.currentRow()

        if current_row is not self.focus_list_widget.count() - 1:
            selected_item = self.focus_list_widget.currentItem()
            below_item = self.focus_list_widget.itemAt(current_row + 1, 0)

            self.focus_list_widget.takeItem(current_row)
            self.focus_list_widget.insertItem(current_row, below_item)
            self.focus_list_widget.insertItem(current_row + 1, selected_item)
            self.focus_list_widget.setCurrentRow(current_row + 1)

        self.focus_list_widget.setFocus()

    def button_clicked_tag_save(self):
        with open("list_current_tags.pickle", "wb") as f:
            pickle.dump(list_current_tags, f)

        with open("list_available_tags.pickle", "wb") as f:
            pickle.dump(list_available_tags, f)

    def button_clicked_tag_move_to_current(self):
        if self.focus_list_widget != self.list_widget_current_tags:
            current_row = self.focus_list_widget.currentRow()
            selected_item = self.focus_list_widget.currentItem()
            self.focus_list_widget.takeItem(current_row)
            self.list_widget_current_tags.addItem(selected_item)
            self.list_widget_current_tags.setCurrentRow(
                self.list_widget_current_tags.count() - 1
            )
        self.focus_list_widget.setFocus()

    def button_clicked_tag_move_to_available(self):
        if self.focus_list_widget != self.list_widget_available_tags:
            current_row = self.focus_list_widget.currentRow()
            selected_item = self.focus_list_widget.currentItem()
            self.focus_list_widget.takeItem(current_row)
            self.list_widget_available_tags.addItem(selected_item)
            self.list_widget_available_tags.setCurrentRow(
                self.list_widget_available_tags.count() - 1
            )
        self.focus_list_widget.setFocus()

    def save_progress_bar(self):
        pass

    def find_tag(self):
        pass

    def fetch_next(self):
        pass

    def button_clicked_clear(self):
        [self.line_edit_tags[i].clear() for i in range(len(list_current_tags))]
        self.line_edit_tags[0].setFocus()

    def insert_file_list_to_table_widget(self):
        path = self.line_edit_source_path.text()
        self.table_widget_image.clear()
        list_ds.clear()

        b_check_pixel_data = self.check_load_pixel_data.isChecked()
        self.table_widget_image.setColumnCount(len(list_current_tags))
        self.table_widget_image.setHorizontalHeaderLabels(list_current_tags)

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
            # self.progress_bar.setUpdatesEnabled(True)
            # self.progress_bar.setValue(int(i / len(list_files)) * 100)
            # print(int((i / (len(list_files) - 1) * 100)))
            # 499, 500(-1), 0.98(*100)
            self.progress_bar.setValue(int((i / (len(list_files) - 1) * 100)))
            self.progress_bar.update()
            for j, tag in enumerate(list_current_tags):
                try:
                    self.table_widget_image.setItem(
                        i,
                        j,
                        QTableWidgetItem(
                            str(list_ds[i][list_current_tags[j]].value)
                        ),
                    )
                except KeyError:
                    self.table_widget_image.setItem(
                        i,
                        j,
                        QTableWidgetItem(""),
                    )


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

# G:\STORAGE\STO01\2022\02\15\CR\
# 00023010_2022-02-15_145906_CR\
# 00023010_2022-02-15_145906_CR\
# 1.2.643.18619941.103772.92022215.91453560.1.4.4.dcm
