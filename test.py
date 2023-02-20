from connect import get_current 
from structure_set_classes import CUHRTStructureSetCompare
from os import path

case = get_current("Case") 
exam = get_current("Examination")

    
new_roi_name = case.PatientModel.GetUniqueRoiName(DesiredName="MODIFIED")

case.PatientModel.CreateRoi(
    Name = new_roi_name,
    Type = "Undefined",
    Color = "Blue" 
)

new_roi = case.PatientModel.RegionsOfInterest[new_roi_name]

new_roi.CreateBoxGeometry(
    Size={
        "x":2,
        "y":2,
        "z":2
    },
    Examination = exam,
    Center = {
        "x":0,
        "y":0,
        "z":0
    },
    Representation = 'Voxels',
    VoxelSize = None
)

new_roi_geometry = case.PatientModel.StructureSets[exam.Name].RoiGeometries[new_roi_name]
new_roi_geometry.SetRepresentation(Representation = "Contours")

my_second_obj = CUHRTStructureSetCompare(
    f_path = path.join(
        "//GBCBGPPHFS001.net.addenbrookes.nhs.uk/ProjectData/User Data/Liam_ProjectData",
        "zROILockTime_v2_Klodowska_Magdalena_02_06_2023_11_17_04_.json"
    )
)
    
a_roi = my_second_obj.rois[0]
print(a_roi["label"])
new_roi_geometry.PrimaryShape.Contours = a_roi["contours"] 
