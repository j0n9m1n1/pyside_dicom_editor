import pickle

list_currnet_tags = [
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

list_available_tags = ["SeriesNo", "ImageNo"]

with open("list_currnet_tags.pickle", "wb") as f:  # wb : 바이트 형식으로 쓰기
    pickle.dump(list_currnet_tags, f)  # (저장하고자 하는 객체, 파일)

with open("list_available_tags.pickle", "wb") as f:  # wb : 바이트 형식으로 쓰기
    pickle.dump(list_available_tags, f)  # (저장하고자 하는 객체, 파일)
