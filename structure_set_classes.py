from connect import get_current 
from os import path
from sys import exit
from json import load, dump
from datetime import datetime as dt
from tkinter import Tk
from tkinter import messagebox as mb

exam = get_current("Examination")
patientID = get_current("Patient").PatientID
case = get_current("Case")

class CUHRTStructureSetException(Exception):
    '''
        Super exception class - raised if any of the following classes fail. 

        Attributes: 
            • message: str 
    '''
    def __init__(self, message: str = "Default ERROR."):
        self.message = message
        root = Tk()
        root.iconbitmap(
            "//MOSAIQAPP-20/mosaiq_app/TOOLS/RayStation/microscope_io/microscope.ico"
            )
        root.withdraw() 
        mb.showerror(
            title = "ERROR: CUHRTStructureSetException",
            message = self.message
        ) 
        super().__init__(self.message)
        exit()


class CUHRTStructureSetCompare():
    ''' 
        Workhorse of ROILockTime v2.x.x

        Instantiated from:
            • case.PatientModel.StructureSets[exam.Name].SubStructureSets object 
            • JSON export

        Attributes:
            • locktime 
            • reviewer
            • f_name 
            • has_contours: bool
            • rois: dict 
                label, volume, com, contours 

        Methods:
            • load_contours 
                loads contours into memory if not called at init 
            • json_export
                exports rudimentary structure set data to json 
            • restore_contours
                adds structures back in to current structure set from file

    '''

    def __init__(self, 
    f_path = None, ss_index: int = None, include_contours: bool = False):

        self.has_contours = include_contours

        if f_path:
            try: 
                with open(path.normpath(f_path), 'r', encoding='utf-8') as f:
                    data = load(f)
                self.locktime = data['locktime']
                self.reviewer = data['reviewer']
                self.has_contours = data['has_contours']
                self.f_name = path.split(f_path)[-1]
                self.rois = data['rois']
            except:
                raise CUHRTStructureSetException(
                    message = "Cannot load RT SS from file."
                )
                     
        elif ss_index is not None:
            ss = case.PatientModel.StructureSets[exam.Name].SubStructureSets[ss_index]

            try:
                rev = ss.Review.ReviewTime
                self.locktime = dt(
                    year = rev.Year, month = rev.Month, day = rev.Day, 
                    hour = rev.Hour, minute = rev.Minute, 
                    second = rev.Second).strftime("%m_%d_%Y_%H_%M_%S")
                self.reviewer = ss.Review.ReviewerFullName.replace("^"," ")
                self.f_name = "_".join(
                    [
                        patientID,
                        self.reviewer.replace(" ","_"),
                        self.locktime,
                        ".json"
                    ]
                )
            except:
                self.locktime = None 
                self.reviewer = None 
                self.f_name = "_".join(
                    [
                        patientID,
                        "UNNAPPROVED",
                        ".json"
                    ]
                )


            if self.has_contours:
                self.load_contours(ss.RoiStructures)

            else:
                self.rois = [
                    {
                        "label":roi.OfRoi.Name,
                        "volume": roi.GetRoiVolume(), 
                        "com": roi.GetCenterOfRoi(), 
                        "contours": None
                    }
                    for roi in ss.RoiStructures
                ]


        else:
            raise CUHRTStructureSetException(
                    message = (
                        "No Sub-StructureSet index selected. \n"
                        "Or json file path provided."
                ))

    def load_contours(self, rois):
        '''
            Params:
                rois - list of RayStation Roi script object 
        '''
        self.has_contours = True
 
        self.rois = [
                {
                    "label":roi.OfRoi.Name,
                    "volume": roi.GetRoiVolume(), 
                    "com": roi.GetCenterOfRoi(), 
                    "contours": [
                        contour for contour in roi.PrimaryShape.Contours],
                }
                for roi in rois 
                if hasattr(roi.PrimaryShape, "Contours") 
            ]


    def json_export(self, f_out: str):
        '''
            Write contents of CUHRTStructureSetCompare to 
            JSON.
        '''

        print(self.__dict__)

        try: 
            with open(path.join(f_out, self.f_name), 
            'w',encoding='utf-8') as f:
                dump(self.__dict__, f, indent=4, sort_keys=True) 
        except:
            raise CUHRTStructureSetException(
                message = "Could not write RT SS to json."
            ) 

    def restore_contours(self):
        '''
            Attempts to add the contours from the CUHRTStructrureSetCompare 
            onto the current examination. 
        '''

        for roi in self.rois:
            print(f"Attempting to recreate ROI: {roi['label']}")

            new_roi_name = case.PatientModel.GetUniqueRoiName(
                DesiredName = roi["label"]
                )

            case.PatientModel.CreateRoi(
                Name = new_roi_name,Type = "Undefined",Color = "Blue" 
            )

            new_roi = case.PatientModel.RegionsOfInterest[new_roi_name]

            new_roi.CreateBoxGeometry(
                Size={"x":2,"y":2,"z":2},Examination = exam,
                Center = {"x":0,"y":0,"z":0},Representation = 'Voxels',
                VoxelSize = None
            )

            new_roi_geometry = case.PatientModel.StructureSets[exam.Name].RoiGeometries[new_roi_name]
            new_roi_geometry.SetRepresentation(Representation = "Contours")

            if roi["contours"]:
                new_roi_geometry.PrimaryShape.Contours = roi["contours"]
            else:
                print(f"ROI: {roi['label']} has no contours.")  