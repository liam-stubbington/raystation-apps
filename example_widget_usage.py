#from structure_set_classes import CUHRTStructureSet
from os import path
import tkinter as tk 
from widgets.cuh_tkinter import *

# --------------------------------------------------------------------------- #

# my_obj = CUHRTStructureSet(
#     ss_index=1,
# ) 

# rois = [roi for roi in my_obj.rois]

# compare_roi_object = rois[0].compare_with_roi(rois[1].roi['label'])

# print(f"ROI 1: {rois[0].roi['label']}")
# print(f"ROI 2: {rois[1].roi['label']}")

# print(f"Centroid match: {compare_roi_object.centroid_match}.")
# print(f"Volume match: {compare_roi_object.volume_match}.")
# for k,v in compare_roi_object.roi_comparison_results.items():
#     print(f"{k}: {v}")

# my_obj.json_export(
#     f_out = "//GBCBGPPHFS001.net.addenbrookes.nhs.uk/ProjectData/User Data/Liam_ProjectData",
#     include_contours=True
#   )

# --------------------------------------------------------------------------- #


# my_second_obj = CUHRTStructureSet(
#     f_path = path.join(
#         "//GBCBGPPHFS001.net.addenbrookes.nhs.uk/ProjectData/User Data/Liam_ProjectData",
#         "zROILockTime_v2_Stubbington_Liam_02_21_2023_09_37_14_.json"

#     )
    
# )

# print(my_second_obj.locktime)
# print(my_second_obj.reviewer) 
# print([roi.roi['label'] for roi in my_second_obj.rois])

# my_second_obj.restore_all_contours()

# --------------------------------------------------------------------------- #

__title__ = "ROI LockTime App"
__version__ = "v0.0.0"

root = tk.Tk() 
root.title = (__title__ + " " + __version__)
root.configure(background="black")
root.columnconfigure((0,1,2), weight =1)
root.rowconfigure((0,1,2), weight = 1)
root.iconbitmap(
    "//Mosaiqapp-20/mosaiq_app/TOOLS/RayStation/radioactive_favicon_io/favicon.ico"
)

title_text = CUHTitleText(
    root, __title__ + " " + __version__, columnspan = 3
)

text_label = CUHLabelText(
    root, "Some text", 1, 0, "info"
)

a_button = CUHAppButton(
    root, "Click me!", lambda: print("Button pressed"), 1, 1
)

a_drop_down = CUHDropDownMenu(root, ["option "+str(i) for i in range(1,20)], 
1, 2)

a_radio_button = CUHCheckBox(root, 'Selection',2,0, columnspan=3 )


root.mainloop()