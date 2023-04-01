import sys, os, time, pickle
from pathlib import Path
from threading import Thread
from pydicom import dcmread
from PySide6.QtCore import *
from PySide6.QtWidgets import *

MAX_LOAD_COUNT = 500


class LoadingFiles(QThread):
    tt = Signal()

    def __init__(self):
        super().__init__()

    def run(self):
        pass


class LoadDataset(QThread):
    tt = Signal()

    def __init__(self):
        super().__init()

    def run(self):
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.list_ds = list()
        self.list_files = list()
        self.list_current_tags = list()
        self.list_available_tags = list()

        self.load_tag_files()
        self.ui_init()
        self.ui_init2()
        self.focus_list_widget = None

    def ui_init(self):
        self.tab_widget = QTabWidget()

        self.tab = QWidget()

        self.grid_layout = QGridLayout()

        self.table_widget_dicom = QTableWidget()
        self.list_widget_log = QListWidget()
        self.progress_bar = QProgressBar()

        self.label_source_path = QLabel()
        self.line_edit_source_path = QLineEdit()

        self.label_target_path = QLabel()
        self.line_edit_target_path = QLineEdit()

        self.check_load_pixel_data = QCheckBox()

        self.button_load_files = QPushButton()

        self.button_select_source_dir = QPushButton()
        self.button_select_target_dir = QPushButton()

        self.button_save_dcm = QPushButton()
        self.button_clear = QPushButton()

        self.label_tags = [QLabel() for x in range(len(self.list_current_tags))]
        self.line_edit_tags = [
            QLineEdit() for x in range(len(self.list_current_tags))
        ]

        self.tab2 = QWidget()
        self.grid_layout2 = QGridLayout()

        self.label_current_tags = QLabel()
        self.label_available_tags = QLabel()

        self.list_widget_current_tags = QListWidget()
        self.list_widget_available_tags = QListWidget()

        self.line_edit_current_tag_add = QLineEdit()
        self.button_tag_add_current = QPushButton()

        self.line_edit_available_tag_add = QLineEdit()
        self.button_tag_add_available = QPushButton()

        self.button_tag_delete = QPushButton()
        self.button_tag_up = QPushButton()
        self.button_tag_down = QPushButton()
        self.button_tag_move_to_current = QPushButton()
        self.button_tag_move_to_available = QPushButton()
        self.button_save_tag = QPushButton()

    def ui_init2(self):
        self.table_widget_dicom.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.table_widget_dicom.doubleClicked.connect(
            self.table_widget_dicom_double_clicked
        )
        self.table_widget_dicom.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        count_list_tag = len(self.list_current_tags)
        self.tab_widget.addTab(self.tab, "Edit")

        self.table_widget_dicom.setColumnCount(len(self.list_current_tags))
        self.table_widget_dicom.setHorizontalHeaderLabels(
            self.list_current_tags
        )
        self.table_widget_dicom.setRowCount(50)

        self.label_source_path.setText("Source")
        # self.line_edit_source_path.setText(r"/users/j0n9m1n1/vscode/python/dicom_samples")
        self.line_edit_source_path.setText(r"G:\STORAGE")

        self.label_target_path.setText("Target")
        # self.line_edit_target_path.setText(r"/users/j0n9m1n1/vscode/python/dicom_samples/modified")
        self.line_edit_target_path.setText(r"G:\STORAGE\modified")

        self.check_load_pixel_data.setText("Pixel Data")
        self.check_load_pixel_data.setChecked(True)

        self.button_select_source_dir.setText("...")
        self.button_select_source_dir.clicked.connect(
            self.button_clicked_select_source_path
        )
        self.button_select_target_dir.setText("...")
        self.button_select_target_dir.clicked.connect(
            self.button_clicked_select_target_path
        )

        self.button_load_files.setText("Load")
        self.button_load_files.clicked.connect(self.button_clicked_load_files)

        self.button_save_dcm.setText("Save")
        self.button_save_dcm.clicked.connect(self.button_clicked_save)

        self.button_clear.setText("Clear")
        self.button_clear.clicked.connect(self.button_clicked_clear)

        # 호기심 해결겸 list comp
        [
            self.label_tags[i].setText(tag)
            for i, tag in enumerate(self.list_current_tags)
        ]

        self.grid_layout.addWidget(self.label_source_path, 0, 0)
        self.grid_layout.addWidget(self.line_edit_source_path, 0, 1)
        self.grid_layout.addWidget(self.button_select_source_dir, 0, 2)

        self.grid_layout.addWidget(self.label_target_path, 0, 3)
        self.grid_layout.addWidget(self.line_edit_target_path, 0, 4)
        self.grid_layout.addWidget(self.button_select_target_dir, 0, 5)

        self.grid_layout.addWidget(self.check_load_pixel_data, 0, 6)
        self.grid_layout.addWidget(self.button_load_files, 0, 7)

        # 호기심 해결겸 list comp
        [
            self.grid_layout.addWidget(self.label_tags[i], i + 1, 6)
            for i in range(count_list_tag)
        ]
        [
            self.grid_layout.addWidget(self.line_edit_tags[i], i + 1, 7)
            for i in range(count_list_tag)
        ]

        self.grid_layout.addWidget(
            self.table_widget_dicom,
            1,
            0,
            count_list_tag // 2,
            6,
        )
        self.grid_layout.addWidget(
            self.list_widget_log,
            (count_list_tag // 2) + 1,
            0,
            count_list_tag - (count_list_tag // 2),
            6,
        )

        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.grid_layout.addWidget(
            self.progress_bar, count_list_tag + 1, 0, 1, 6
        )
        # self.statusBar().insertWidget(0, self.progress_bar)

        self.grid_layout.addWidget(self.button_save_dcm, count_list_tag + 1, 6)
        self.grid_layout.addWidget(self.button_clear, count_list_tag + 1, 7)

        self.tab.setLayout(self.grid_layout)

        #
        self.tab_widget.addTab(self.tab2, "Setting")

        self.label_current_tags.setText("Current Tags")
        self.label_available_tags.setText("Available Tags")

        self.list_widget_current_tags.itemClicked.connect(
            self.list_widget_current_tags_item_clicked
        )
        self.list_widget_available_tags.itemClicked.connect(
            self.list_widget_available_tags_item_clicked
        )
        self.list_widget_current_tags.addItems(self.list_current_tags)
        self.list_widget_available_tags.addItems(self.list_available_tags)

        self.button_tag_add_current.setText("Add")
        self.button_tag_add_current.clicked.connect(
            self.button_clicked_tag_add_current
        )

        self.button_tag_add_available.setText("Add")
        self.button_tag_add_available.clicked.connect(
            self.button_clicked_tag_add_available
        )
        self.button_tag_delete.setText("Delete")
        self.button_tag_delete.clicked.connect(self.button_clicked_tag_delete)
        self.button_tag_up.setText("Up")
        self.button_tag_up.clicked.connect(self.button_clicked_tag_up)
        self.button_tag_down.setText("Down")
        self.button_tag_down.clicked.connect(self.button_clicked_tag_down)
        self.button_save_tag.setText("Save")
        self.button_save_tag.clicked.connect(self.button_clicked_tag_save)
        self.button_tag_move_to_current.setText("<<")
        self.button_tag_move_to_current.clicked.connect(
            self.button_clicked_tag_move_to_current
        )
        self.button_tag_move_to_available.setText(">>")
        self.button_tag_move_to_available.clicked.connect(
            self.button_clicked_tag_move_to_available
        )

        self.grid_layout2.addWidget(self.label_current_tags, 0, 0)
        self.grid_layout2.addWidget(self.label_available_tags, 0, 5)

        self.grid_layout2.addWidget(self.list_widget_current_tags, 1, 0, 5, 2)
        self.grid_layout2.addWidget(self.list_widget_available_tags, 1, 5, 5, 2)

        self.grid_layout2.addWidget(self.button_tag_up, 2, 3)
        self.grid_layout2.addWidget(self.button_tag_move_to_current, 3, 4)
        self.grid_layout2.addWidget(self.button_tag_delete, 3, 3)
        self.grid_layout2.addWidget(self.button_tag_move_to_available, 3, 2)
        self.grid_layout2.addWidget(self.button_tag_down, 4, 3)

        self.grid_layout2.addWidget(self.line_edit_current_tag_add, 6, 0)
        self.grid_layout2.addWidget(self.button_tag_add_current, 6, 1)

        self.grid_layout2.addWidget(self.line_edit_available_tag_add, 6, 5)
        self.grid_layout2.addWidget(self.button_tag_add_available, 6, 6)

        self.grid_layout2.addWidget(self.button_save_tag, 6, 2, 1, 3)

        self.tab2.setLayout(self.grid_layout2)

        self.setCentralWidget(self.tab_widget)
        self.setWindowTitle("DICOM Header Editor")

    def table_widget_dicom_double_clicked(self):
        print("dbl", self.table_widget_dicom.currentRow())

    def load_tag_files(self):
        with open("list_current_tags.pickle", "rb") as f:
            self.list_current_tags = pickle.load(f)  # (파일)

        with open("list_available_tags.pickle", "rb") as f:
            self.list_available_tags = pickle.load(f)  # (파일)

    def button_clicked_load_files(self):
        self.t1 = Thread(target=self.insert_file_list_to_table_widget)
        self.t1.start()

    def button_clicked_save(self):
        self.t2 = Thread(target=self.create_modified_dcm)
        self.t2.start()

    def create_modified_dcm(self):
        list_selected_index = self.table_widget_dicom.selectedIndexes()
        for i, item in enumerate(list_selected_index):
            for j, tag in enumerate(self.list_current_tags):
                try:
                    if self.line_edit_tags[j].text() != "":
                        if "," in tag:
                            f, s = map(
                                lambda z: int(z, 16),
                                tag.replace(" ", "").split(","),
                            )
                            print(
                                f"[{tag}]Before: {self.list_ds[item.row()][f, s].value}",
                                end=" ",
                            )
                            self.list_ds[item.row()][
                                f, s
                            ].value = self.line_edit_tags[j].text()
                            print(
                                f"After: {self.list_ds[item.row()][f, s].value}"
                            )
                        else:
                            print(
                                f"[{tag}]Before: {self.list_ds[item.row()][tag].value}",
                                end=" ",
                            )
                            self.list_ds[item.row()][
                                tag
                            ].value = self.line_edit_tags[j].text()
                            print(
                                f"After: {self.list_ds[item.row()][tag].value}"
                            )
                except Exception:
                    pass
            # will be a checkbox option
            maintain_original_directory_structure = False

            file_path = Path(self.list_files[item.row()])

            if maintain_original_directory_structure:
                output_path = self.line_edit_target_path

                count_parts = len(file_path.parts)
                if count_parts == 2:
                    output_path = os.path.join(output_path, file_path.parts[1])
                elif count_parts > 2:
                    for p in range(1, count_parts):
                        output_path = os.path.join(
                            output_path, file_path.parts[p]
                        )
                else:
                    pass  # something wrong loaded file path
            else:
                str_out_file_name = file_path.stem + file_path.suffix
                output_path = os.path.join(
                    self.line_edit_target_path.text(),
                    str_out_file_name,
                )
            try:
                if not os.path.exists(os.path.dirname(output_path)):
                    os.makedirs(os.path.dirname(output_path))

                self.progress_bar.setValue(
                    int(((i + 1) / len(list_selected_index) * 100))
                )
                self.list_ds[item.row()].save_as(output_path)
                self.progress_bar.setFormat(
                    f"Saving {i+1}/{len(list_selected_index)} {self.progress_bar.value()}%"
                )
                print(f"saved: {output_path}")
            except:
                pass

    def button_clicked_select_source_path(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Source Directory"
        )
        self.line_edit_source_path.setText(directory)

    def button_clicked_select_target_path(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Target Directory"
        )
        self.line_edit_target_path.setText(directory)

    def list_widget_current_tags_item_clicked(self):
        self.focus_list_widget = self.list_widget_current_tags

    def list_widget_available_tags_item_clicked(self):
        self.focus_list_widget = self.list_widget_available_tags

    def button_clicked_tag_add_current(self):
        self.focus_list_widget = self.list_widget_current_tags
        tag = self.line_edit_current_tag_add.text()
        if tag is not None:
            self.list_widget_current_tags.addItem(tag)
            self.list_widget_current_tags.setCurrentRow(
                self.list_widget_current_tags.count() - 1
            )

    def button_clicked_tag_add_available(self):
        self.focus_list_widget = self.list_widget_available_tags
        tag = self.line_edit_available_tag_add.text()
        if tag is not None:
            self.list_widget_available_tags.addItem(tag)
            self.list_widget_available_tags.setCurrentRow(
                self.list_widget_available_tags.count() - 1
            )

    def reload_table_widget(self):
        pass

    def find_tag(self):
        pass

    def fetch_next(self):
        pass

    def add_log(self):
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

        if current_row > 0:
            selected_item = self.focus_list_widget.takeItem(current_row)
            self.focus_list_widget.insertItem(current_row - 1, selected_item)
            self.focus_list_widget.setCurrentRow(current_row - 1)

        self.focus_list_widget.setFocus()

    def button_clicked_tag_down(self):
        current_row = self.focus_list_widget.currentRow()

        if current_row < self.focus_list_widget.count() - 1:
            selected_item = self.focus_list_widget.takeItem(current_row)
            self.focus_list_widget.insertItem(current_row + 1, selected_item)
            self.focus_list_widget.setCurrentRow(current_row + 1)

        self.focus_list_widget.setFocus()

    def button_clicked_tag_save(self):
        self.list_current_tags = [
            self.list_widget_current_tags.item(x).text()
            for x in range(self.list_widget_current_tags.count())
        ]
        with open("list_current_tags.pickle", "wb") as f:
            pickle.dump(self.list_current_tags, f)

        self.list_available_tags = [
            self.list_widget_available_tags.item(x).text()
            for x in range(self.list_widget_available_tags.count())
        ]
        with open("list_available_tags.pickle", "wb") as f:
            pickle.dump(self.list_available_tags, f)

        self.set_table_widget_headers()

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

    def button_clicked_clear(self):
        [
            self.line_edit_tags[i].clear()
            for i in range(len(self.list_current_tags))
        ]
        self.line_edit_tags[0].setFocus()

    def set_table_widget_headers(self):
        self.table_widget_dicom.clear()
        self.table_widget_dicom.setColumnCount(len(self.list_current_tags))
        self.table_widget_dicom.setHorizontalHeaderLabels(
            self.list_current_tags
        )

    def insert_file_list_to_table_widget(self):
        self.button_load_files.setEnabled(False)
        path = self.line_edit_source_path.text()

        self.table_widget_dicom.clear()
        self.list_ds.clear()
        self.list_files.clear()

        b_check_pixel_data = self.check_load_pixel_data.isChecked()

        self.set_table_widget_headers()

        # 구조가 복잡한 경우도 있어서 walk로 바꿈
        # 근데 확장자가 아예 없는 경우도 있어서 고민중
        # 일단 .dcm만
        for root, dirs, files in os.walk(path):
            if len(files) > 0:
                for file_name in files:
                    if (
                        file_name.lower().endswith("dcm")
                        and len(self.list_files) < MAX_LOAD_COUNT
                    ):
                        self.list_files.append(os.path.join(root, file_name))
        print(len(self.list_files))
        self.table_widget_dicom.setRowCount(len(self.list_files))

        for i, file_path in enumerate(self.list_files):
            self.list_ds.append(
                dcmread(
                    file_path,
                    stop_before_pixels=not b_check_pixel_data,
                    force=True,
                )
            )

            self.progress_bar.setValue(
                int(((i + 1) / (len(self.list_files)) * 100))
            )
            self.progress_bar.setFormat(
                f"Loading {i+1}/{len(self.list_files)} {self.progress_bar.value()}%"
            )
            # self.progress_bar.update()
            for j, tag in enumerate(self.list_current_tags):
                try:
                    if "," in tag:
                        f, s = map(
                            lambda z: int(z, 16),
                            tag.replace(" ", "").split(","),
                        )
                        self.table_widget_dicom.setItem(
                            i,
                            j,
                            QTableWidgetItem(str(self.list_ds[i][f, s].value)),
                        )
                    else:
                        self.table_widget_dicom.setItem(
                            i,
                            j,
                            QTableWidgetItem(str(self.list_ds[i][tag].value)),
                        )
                except KeyError:
                    self.table_widget_dicom.setItem(
                        i,
                        j,
                        QTableWidgetItem(""),
                    )
        self.button_load_files.setEnabled(True)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

# G:\STORAGE\STO01\2022\02\15\CR\
# 00023010_2022-02-15_145906_CR\
# 00023010_2022-02-15_145906_CR\
# 1.2.643.18619941.103772.92022215.91453560.1.4.4.dcm
