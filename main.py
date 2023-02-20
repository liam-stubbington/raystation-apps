from structure_set_classes import CUHRTStructureSetCompare
from os import path

# --------------------------------------------------------------------------- #

# my_obj = CUHRTStructureSetCompare(
#     ss_index=1,
#     include_contours=True
# ) 

# print(my_obj.reviewer)

# my_obj.json_export(
#     f_out = "//GBCBGPPHFS001.net.addenbrookes.nhs.uk/ProjectData/User Data/Liam_ProjectData",
#   )

# --------------------------------------------------------------------------- #


my_second_obj = CUHRTStructureSetCompare(
    f_path = path.join(
        "//GBCBGPPHFS001.net.addenbrookes.nhs.uk/ProjectData/User Data/Liam_ProjectData",
        "zROILockTime_v2_Klodowska_Magdalena_02_06_2023_11_17_04_.json"

    )
    
)

my_second_obj.restore_contours()

# --------------------------------------------------------------------------- #