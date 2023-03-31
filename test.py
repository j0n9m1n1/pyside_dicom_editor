import unittest
import os, sys
from pydicom import dcmread
import logging
from pathlib import Path


class TestStringMethods(unittest.TestCase):
    def test_upper(self):
        self.assertEqual("foo".upper(), "FOO")

    def test_isupper(self):
        self.assertTrue("FOO".isupper())
        self.assertFalse("Foo".isupper())

    def test_split(self):
        s = "hello world"
        self.assertEqual(s.split(), ["hello", "world"])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

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
        a = Path(r"D:\icon_list\black-24dp (2)\2x\filename~~.dcm")
        output_path = r"D:\modified"
        if len(a.parts()) == 2:  # mean D:\\file.dcm
            pass

    def test_load_with_hex(self):
        hex_tag = "0x0010, 0x0040"
        f, s = map(lambda z: int(z, 16), hex_tag.replace(" ", "").split(","))
        ds = dcmread(r"G:\아이디\SERIES1\0")
        a = ds[f, s].value
        print(a)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # logging.getLogger("test_find_files").setLevel(logging.DEBUG)
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
