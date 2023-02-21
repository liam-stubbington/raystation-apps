from structure_set_classes import CUHRTStructureSet
from os import path

# --------------------------------------------------------------------------- #

my_obj = CUHRTStructureSet(
    ss_index=1,
) 

rois = [roi for roi in my_obj.rois]

compare_roi_object = rois[0].compare_with_roi(rois[1].roi['label'])

print(f"ROI 1: {rois[0].roi['label']}")
print(f"ROI 2: {rois[1].roi['label']}")

print(f"Centroid match: {compare_roi_object.centroid_match}.")
print(f"Volume match: {compare_roi_object.volume_match}.")
for k,v in compare_roi_object.roi_comparison_results.items():
    print(f"{k}: {v}")

# my_obj.json_export(
#     f_out = "//GBCBGPPHFS001.net.addenbrookes.nhs.uk/ProjectData/User Data/Liam_ProjectData",
#     include_contours=True
#   )

# --------------------------------------------------------------------------- #


my_second_obj = CUHRTStructureSet(
    f_path = path.join(
        "//GBCBGPPHFS001.net.addenbrookes.nhs.uk/ProjectData/User Data/Liam_ProjectData",
        "zROILockTime_v2_Stubbington_Liam_02_21_2023_09_37_14_.json"

    )
    
)

# print(my_second_obj.locktime)
# print(my_second_obj.reviewer) 
# print([roi.roi['label'] for roi in my_second_obj.rois])

# my_second_obj.restore_all_contours()

# --------------------------------------------------------------------------- #