import unittest
import time
import os, sys
from pydicom import dcmread
import logging
from pathlib import Path


class TestStringMethods(unittest.TestCase):
    def test_edit(self):
        tag_test = "PatientID"
        # ds = dcmread(r"G:\아이디\SERIES1\0")
        # ds[f"{tag_test}"].value = "qq"

        # print(ds)

    def test_boolean(self):
        abc = True
        abc = not abc
        self.assertFalse(abc)

    def test_find_files(self):
        # log = logging.getLogger("test_find_files")
        root_dir = r"G:\STORAGE"
        # root_dir = "./test/"
        for root, dirs, files in os.walk(root_dir):
            # logging.debug("# root : " + root)
            # print("# root : " + root)
            if len(dirs) > 0:
                for dir_name in dirs:
                    pass
                    # logging.debug("dir: " + dir_name)
                    # print("dir: " + dir_name)

            if len(files) > 0:
                for file_name in files:
                    if not file_name.lower().endswith(("dcm", "xml")):
                        path = os.path.join(root, dir_name, file_name)
                        logging.debug(path)

    def test_directory_change(self):
        # file_path = Path(r"D:\icon_list\black-24dp (2)\2x\filename~~.dcm")
        file_path = Path(r"D:\hello.dcm")
        output_path = r"D:\modified"

        count_parts = len(file_path.parts)
        if count_parts == 2:
            output_path = os.path.join(output_path, file_path.parts[1])
        elif count_parts > 2:
            for p in range(1, count_parts):
                output_path = os.path.join(output_path, file_path.parts[p])
        else:
            pass  # something wrong loaded file path
        aa = 1

    def test_load_with_hex(self):
        hex_tag = "0x0010, 0x0040"
        f, s = map(lambda z: int(z, 16), hex_tag.replace(" ", "").split(","))
        ds = dcmread(r"G:\아이디\SERIES1\0")
        a = ds[f, s].value
        print(a)

    def test_check_directory(self):
        output_path = r"G:\220805\05\1-12949\123454\085633\I.1.2.410.200038.20220805.085633.123454.1.001.001.bmp"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        aa = 3

    def test_walk(self):
        list_files = []
        for root, dirs, files in os.walk(r"G:\STORAGE"):
            if len(files) > 0:
                for file_name in files:
                    if file_name.lower().endswith("dcm"):
                        list_files.append(os.path.join(root, file_name))

    def test_scan_files_recursively(self, folder_path=r"G:\STORAGE"):
        list_files = []
        for entry in os.scandir(folder_path):
            if (
                entry.is_file()
                and os.path.splitext(entry.name)[1].lower() == ".dcm"
            ):
                list_files.append(os.path.join(r"G:\STORAGE", entry.name))
            elif entry.is_dir():
                self.test_scan_files_recursively(entry.path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # logging.getLogger("test_find_files").setLevel(logging.DEBUG)
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
