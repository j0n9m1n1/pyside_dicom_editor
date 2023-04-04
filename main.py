# pyinstaller -F --hiddenimport=pydicom.encoders.gdcm --hiddenimport=pydicom.encoders.pylibjpeg --onefile --console main.py
import sys, os, time, pickle
from PIL import Image, ImageQt
import numpy as np
from pathlib import Path
from threading import Thread
from pydicom import dcmread, datadict, _dicom_dict
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtWidgets import *
import qdarkstyle

MAX_LOAD_COUNT = 500


class LoadDcmThread(QThread):
    load_dcm_done_signal = Signal(list, list)
    update_table_widget_signal = Signal(int, int, str)
    progress_bar_update_signal = Signal(str, int, int)

    def __init__(self, source_path, list_current_tags, b_check_pixel_data):
        super().__init__()
        self.list_files = list()
        self.list_ds = list()

        self.source_path = source_path
        self.list_current_tags = list_current_tags
        self.b_check_pixel_data = b_check_pixel_data

    def run(self):
        # mostly scandir is faster than os.walk
        for root, dirs, files in os.walk(self.source_path):
            if len(files) > 0:
                for file_name in files:
                    if (
                        file_name.lower().endswith("dcm")
                        and len(self.list_files) < MAX_LOAD_COUNT
                    ):
                        self.list_files.append(os.path.join(root, file_name))

        total = len(self.list_files)
        for i, file_path in enumerate(self.list_files):
            self.list_ds.append(
                dcmread(
                    file_path,
                    stop_before_pixels=not self.b_check_pixel_data,
                    force=True,
                )
            )
            self.progress_bar_update_signal.emit("Reading", i + 1, total)
            for j, tag in enumerate(self.list_current_tags):
                try:
                    if "," in tag:
                        f, s = map(
                            lambda z: int(z, 16),
                            tag.replace(" ", "").split(","),
                        )
                        self.update_table_widget_signal.emit(
                            i,
                            j,
                            str(self.list_ds[i][f, s].value),
                        )

                    else:
                        # QMetaObject.invokeMethod(Q_ARG(int, i))
                        self.update_table_widget_signal.emit(
                            i,
                            j,
                            str(self.list_ds[i][tag].value),
                        )
                except KeyError:
                    self.update_table_widget_signal.emit(
                        i,
                        j,
                        "",
                    )

        self.load_dcm_done_signal.emit(self.list_files, self.list_ds)


class SaveDcmThread(QThread):
    save_dcm_done_signal = Signal()
    progress_bar_update_signal = Signal(str, int, int)
    update_cell_signal = Signal(bool, int, int, str, str)

    def __init__(
        self,
        list_selected_rows,
        list_current_tags,
        line_edit_tags,
        list_ds,
        list_file,
        line_edit_target_path,
    ):
        super().__init__()
        self.list_selected_rows = list_selected_rows
        self.list_current_tags = list_current_tags
        self.line_edit_tags = line_edit_tags
        self.list_ds = list_ds
        self.list_file = list_file
        self.line_edit_target_path = line_edit_target_path

    def run(self):
        for i, row in enumerate(self.list_selected_rows):
            total = len(self.list_selected_rows)
            for j, tag in enumerate(self.list_current_tags):
                try:
                    if self.line_edit_tags[j].text() != "":
                        if "," in tag:
                            f, s = map(
                                lambda z: int(z, 16),
                                tag.replace(" ", "").split(","),
                            )
                            before = str(self.list_ds[row.row()][f, s].value)

                            self.list_ds[row.row()][
                                f, s
                            ].value = self.line_edit_tags[j].text()
                            after = str(self.list_ds[row.row()][f, s].value)
                            
                            self.update_cell_signal.emit(
                                True,
                                row.row(),
                                j,
                                before,
                                after
                            )
                        else:
                            
                            before = str(self.list_ds[row.row()][tag].value)
                                
                            self.list_ds[row.row()][
                                tag
                            ].value = self.line_edit_tags[j].text()
                        
                            after = str(self.list_ds[row.row()][tag].value)
                            
                            self.update_cell_signal.emit(
                                True,
                                row.row(),
                                j,
                                before,
                                after
                            )
                except Exception:
                    self.update_cell_signal.emit(
                                False,
                                row.row(),
                                j,
                                before,
                                after
                            )
            # will be a checkbox option
            kepp_dir_structure = False

            file_path = Path(self.list_file[row.row()])

            if kepp_dir_structure:
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
                    self.line_edit_target_path,
                    str_out_file_name,
                )
            try:
                if not os.path.exists(os.path.dirname(output_path)):
                    os.makedirs(os.path.dirname(output_path))

                self.progress_bar_update_signal.emit("Saving", i + 1, total)
                # self.progress_bar.setValue(
                #     int(((i + 1) / len(self.list_selected_index) * 100))
                # )
                self.list_ds[row.row()].save_as(output_path)
                # self.progress_bar.setFormat(
                #     f"Saving {i+1}/{len(self.list_selected_index)} {self.progress_bar.value()}%"
                # )
                print(f"saved: {output_path}")
            except:
                pass
        self.save_dcm_done_signal.emit()


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

        # for data in _dicom_dict.DicomDictionary.items():
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

        self.button_load_file = QPushButton()

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

        self.dialog_view = QDialog()
        self.tab_view = QTabWidget()
        self.vbox_layout_view = QVBoxLayout()

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
        # self.table_widget_dicom.setRowCount(50)

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

        self.button_load_file.setText("Load")
        self.button_load_file.clicked.connect(self.load_dcm)

        self.button_save_dcm.setText("Save")
        self.button_save_dcm.clicked.connect(self.save_dcm)

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
        self.grid_layout.addWidget(self.button_load_file, 0, 7)

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

        self.dialog_view.setWindowTitle("Simple view")
        self.vbox_layout_view.addWidget(self.tab_view)
        self.vbox_layout_view.setAlignment(Qt.AlignCenter)
        self.dialog_view.setLayout(self.vbox_layout_view)

        self.setCentralWidget(self.tab_widget)
        self.setWindowTitle("DICOM Header Editor")

    # https://github.com/pydicom/contrib-pydicom/blob/master/viewers/pydicom_PIL.py
    def get_LUT_value(self, data, window, level):
        """Apply the RGB Look-Up Table for the given
        data and window/level value."""
        return np.piecewise(
            data,
            [
                data <= (level - 0.5 - (window - 1) / 2),
                data > (level - 0.5 + (window - 1) / 2),
            ],
            [
                0,
                255,
                lambda data: ((data - (level - 0.5)) / (window - 1) + 0.5)
                * (255 - 0),
            ],
        )

    # https://github.com/pydicom/contrib-pydicom/blob/master/viewers/pydicom_PIL.py
    def get_image(self):
        row = self.table_widget_dicom.currentRow()
        if "PixelData" not in self.list_ds[row]:
            raise TypeError(
                "Cannot show image -- DICOM dataset does not have " "pixel data"
            )
        # can only apply LUT if these window info exists
        if ("WindowWidth" not in self.list_ds[row]) or (
            "WindowCenter" not in self.list_ds[row]
        ):
            bits = self.list_ds[row].BitsAllocated
            samples = self.list_ds[row].SamplesPerPixel
            if bits == 8 and samples == 1:
                mode = "L"
            elif bits == 8 and samples == 3:
                mode = "RGB"
            elif bits == 16:
                # not sure about this -- PIL source says is 'experimental'
                # and no documentation. Also, should bytes swap depending
                # on endian of file and system??
                mode = "I;16"
            else:
                raise TypeError(
                    "Don't know PIL mode for %d BitsAllocated "
                    "and %d SamplesPerPixel" % (bits, samples)
                )

            # PIL size = (width, height)
            size = (self.list_ds[row].Columns, self.list_ds[row].Rows)

            # Recommended to specify all details
            # by http://www.pythonware.com/library/pil/handbook/image.htm
            im = Image.frombuffer(
                mode, size, self.list_ds[row].PixelData, "raw", mode, 0, 1
            )

        else:
            ew = self.list_ds[row]["WindowWidth"]
            ec = self.list_ds[row]["WindowCenter"]
            ww = int(ew.value[0] if ew.VM > 1 else ew.value)
            wc = int(ec.value[0] if ec.VM > 1 else ec.value)
            image = self.get_LUT_value(self.list_ds[row].pixel_array, ww, wc)
            # Convert mode to L since LUT has only 256 values:
            #   http://www.pythonware.com/library/pil/handbook/image.htm
            im = Image.fromarray(image).convert("L")
        return im

    def table_widget_dicom_double_clicked(self):
        row = self.table_widget_dicom.currentRow()

        image = self.get_image()
        q_image = QPixmap.fromImage(ImageQt.ImageQt(image))
        label = QLabel()
        label.setPixmap(q_image)
        label.setFixedSize(q_image.width(), q_image.height())

        screen = app.primaryScreen()
        size = screen.size()
        width = size.width() * 0.8
        height = size.height() * 0.8

        # self.dialog_view.setMaximumSize(width, height)

        if q_image.width() > width or q_image.height() > height:
            q_image = q_image.scaled(
                width, height, Qt.KeepAspectRatio, Qt.FastTransformation
            )
            label.setPixmap(q_image)
            label.setFixedSize(q_image.width(), q_image.height())

        self.tab_view.addTab(
            label, str(row) + "_" + self.list_ds[row]["PatientID"].value
        )

        self.tab_view.setCurrentIndex(self.tab_view.count() - 1)
        self.dialog_view.show()
        self.dialog_view.raise_()

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
    def create_modified_dcm(self):
        pass

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

    def load_dcm(self):
        self.tab.setEnabled(False)
        b_check_pixel_data = self.check_load_pixel_data.isChecked()
        source_path = self.line_edit_source_path.text()

        self.load_dcm_thread = LoadDcmThread(
            source_path,
            self.list_current_tags,
            b_check_pixel_data,
        )
        self.load_dcm_thread.load_dcm_done_signal.connect(
            self.load_dcm_done_slot
        )
        self.load_dcm_thread.update_table_widget_signal.connect(
            self.update_table_widget_slot
        )
        self.load_dcm_thread.progress_bar_update_signal.connect(
            self.update_progress_bar_slot
        )

        self.load_dcm_thread.start()
        # self.load_dcm_thread.wait()

    def save_dcm(self):
        self.tab.setEnabled(False)
      
        self.save_dcm_thread = SaveDcmThread(
            self.table_widget_dicom.selectionModel().selectedRows(),
            self.list_current_tags,
            self.line_edit_tags,
            self.list_ds,
            self.list_file,
            self.line_edit_target_path.text(),
        )
        self.save_dcm_thread.save_dcm_done_signal.connect(
            self.save_dcm_done_slot
        )
        self.save_dcm_thread.progress_bar_update_signal.connect(
            self.update_progress_bar_slot
        )
        self.save_dcm_thread.update_cell_signal.connect(self.update_cell)

        self.save_dcm_thread.start()

    def load_dcm_done_slot(self, list_file, list_ds):
        self.list_ds = list_ds
        self.list_file = list_file
        self.tab.setEnabled(True)

    def save_dcm_done_slot(self):
        self.tab.setEnabled(True)
        self.table_widget_dicom.clearSelection()

    def update_table_widget_slot(self, row, column, item):
        self.table_widget_dicom.setRowCount(row + 1)
        # utf8_string = str(item).encode('utf-8')
        # print(utf8_string)
        self.table_widget_dicom.setItem(
            row, column, QTableWidgetItem(str(item))
        )

    def update_progress_bar_slot(self, name, i, total):
        self.progress_bar.setValue(int((i / total * 100)))
        self.progress_bar.setFormat(
            f"{name} {i}/{total} {self.progress_bar.value()}%"
        )

    def update_cell(self, b_success, row, column, before, after):
        if b_success:
            self.table_widget_dicom.item(row, column).setBackground(
                QColor(0, 192, 0)
            )

            self.table_widget_dicom.item(row, column).setToolTip(f"before: \"{before}\"")
            self.table_widget_dicom.item(row, column).setText(after)
        else:
            self.table_widget_dicom.item(row, column).setBackground(
                QColor(192, 0, 0)
            )
    
    def closeEvent(self, event):
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog):
                widget.close()
        event.accept()


app = QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))
window = MainWindow()
window.resize(1200, 600)
window.show()
app.exec()
