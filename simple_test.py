from pydicom import dcmread

def edit_test():
    tag_test = "PatientID"
    ds = dcmread(r"G:\아이디\SERIES1\0")
    ds[f"{tag_test}"].value = "qq"
    
    print(ds)

if __name__ == "__main__":
    edit_test()