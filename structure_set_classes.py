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

ss = case.PatientModel.StructureSets[exam.Name]

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

class CUHRTROI():
    ''' 
        Workhorse of ROILockTime script and other script tools.

        Instantiated from: 
            • JSON 
            • RayStation RoiStructure script object 

        Attributes: 
            • has_contours: bool
            • roi: dict 
                label, volume, centroid, colour, contours 

        Methods: 
            • load_contours 
                loads contours into memory if not called at init 
            • restore_contours
                adds structures back in to current structure set from file
            
    '''

    def __init__(
        self, roi: dict, has_contours: bool = False, 
        ):

        self.roi = roi 
        self.has_contours = has_contours 

        if self.has_contours:
            self.load_contours() 
            
    def load_contours(self):
        '''
            Attempts to load contours into memory from RayStation get_current
            Patient Model object. 
        '''
        roi = ss.RoiGeometries[self.roi['label']]

        if hasattr(roi.PrimaryShape, "Contours"):
            self.roi['contours'] = [
                 contour for contour in roi.PrimaryShape.Contours
            ]
        else:
            print(f"No contours for roi: {roi['label']}.")
            self.roi['contours'] = None

    def restore_contours(self):
        '''
            Attempts to add contours from the CUHRTROI object 
            onto the current examination. 
        '''        
        print(f"Attempting to recreate ROI: {self.roi['label']}")

        new_roi_name = case.PatientModel.GetUniqueRoiName(
            DesiredName = self.roi["label"]
            )

        case.PatientModel.CreateRoi(
            Name = new_roi_name,Type = "Undefined",Color = self.roi['colour'] 
        )

        new_roi = case.PatientModel.RegionsOfInterest[new_roi_name]

        new_roi.CreateBoxGeometry(
            Size={"x":2,"y":2,"z":2},Examination = exam,
            Center = {"x":0,"y":0,"z":0},Representation = 'Voxels',
            VoxelSize = None
        )

        new_roi_geometry = ss.RoiGeometries[new_roi_name]
        new_roi_geometry.SetRepresentation(Representation = "Contours")

        if self.roi["contours"]:
            new_roi_geometry.PrimaryShape.Contours = self.roi["contours"]
        else:
            print(f"ROI: {self.roi['label']} has no contours.")  
            

class CUHRTStructureSet():
    ''' 
        Workhorse of ROILockTime script.

        Instantiated from:
            • SubStructureSet object 
            • JSON export

        Attributes:
            • locktime 
            • reviewer
            • f_name 
            • has_contours: bool
            • rois: list 
                list of CUHRTROI objects 

        Methods:
            • json_export
                exports rudimentary structure set data to json 


    '''

    def __init__(self, f_path = None, ss_index: int = None):

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
            sub_s = ss.SubStructureSets[ss_index]

            try:
                rev = sub_s.Review.ReviewTime
                self.locktime = dt(
                    year = rev.Year, month = rev.Month, day = rev.Day, 
                    hour = rev.Hour, minute = rev.Minute, 
                    second = rev.Second).strftime("%m_%d_%Y_%H_%M_%S")
                self.reviewer = sub_s.Review.ReviewerFullName.replace("^"," ")
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


            self.rois = [
                CUHRTROI(
                    roi = {
                        'label':roi.OfRoi.Name,
                        'colour': roi.OfRoi.Color,
                        'centroid': roi.GetCenterOfRoi(), 
                        'volume': roi.GetRoiVolume() 

                    },

                ) for roi in sub_s.RoiStructures
            ]


        else:
            raise CUHRTStructureSetException(
                    message = (
                        "No Sub-StructureSet index selected. \n"
                        "Or json file path provided."
                ))


    def json_export(self, f_out: str, include_contours: bool = False):
        '''
            Write contents of CUHRTStructureSetCompare to 
            JSON.
        '''

        if include_contours:
            self.rois = [
                r.load_contours() for r in self.rois
            ]

        try: 
            with open(path.join(f_out, self.f_name), 
            'w',encoding='utf-8') as f:
                dump(self.__dict__, f, indent=4, sort_keys=True) 
        except:
            raise CUHRTStructureSetException(
                message = "Could not write RT SS to json."
            ) 