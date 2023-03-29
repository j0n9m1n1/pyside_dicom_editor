from pydicom import dcmread
import os
def edit_test():
    tag_test = "PatientID"
    # ds = dcmread(r"G:\아이디\SERIES1\0")
    # ds[f"{tag_test}"].value = "qq"
    
    # print(ds)

def boolean_test():
    abc = True
    print(not abc)

def find_files():
    root_dir = r"D:\jm"
    # root_dir = "./test/"
    for (root, dirs, files) in os.walk(root_dir):
        print("# root : " + root)
        if len(dirs) > 0:
            for dir_name in dirs:
                print("dir: " + dir_name)

        if len(files) > 0:
            for file_name in files:
                print("file: " + file_name)
                
if __name__ == "__main__":
    # edit_test()
    # boolean_test()
    find_files()