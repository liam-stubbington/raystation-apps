from connect import get_current 
from os import path
from sys import exit
from json import load, dump, dumps
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
            • err: str
                TraceBack error message. 
    '''
    def __init__(self, error: str = None, message: str = "Default ERROR."):
        if error:
            self.message = message + f"\n{error}."
        else: 
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
            • roi: dict 
                label, volume, centroid, colour, contours, has_contours

        Methods: 
            • load_contours 
                loads contours into memory if not called at init 
            • restore_contours
                adds structures back in to current structure set from file
            
    '''

    def __init__(self, roi: dict, ):

        self.roi = roi 
            
    def load_contours(self):
        '''
            Attempts to load contours into memory from RayStation get_current
            Patient Model object. 
        '''
        roi = ss.RoiGeometries[self.roi['label']]

        try:
            if hasattr(roi.PrimaryShape, "Contours"):
                self.roi['contours'] = [
                    contour for contour in roi.PrimaryShape.Contours
                ]
                self.roi['has_contours'] = True
            else:
                print(f"No contours for roi: {self.roi['label']}.")
                self.roi['contours'] = None
                self.roi['has_contours'] = False
        except:
            raise CUHRTStructureSetException(
                message = (
                    "ERROR: Could not load contours for "
                    f"{self.roi['label']}."
                )
            )

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
            Name = new_roi_name,Type = "Undefined",
            Color = self.roi['colour'],
        )

        new_roi = case.PatientModel.RegionsOfInterest[new_roi_name]

        new_roi.CreateBoxGeometry(
            Size={"x":2,"y":2,"z":2},Examination = exam,
            Center = {"x":0,"y":0,"z":0},Representation = 'Voxels',
            VoxelSize = None
        )

        new_roi_geometry = ss.RoiGeometries[new_roi_name]
        new_roi_geometry.SetRepresentation(Representation = "Contours")

        try:
            if self.roi["contours"]:
                new_roi_geometry.PrimaryShape.Contours = self.roi["contours"]
            else:
                print(f"ROI: {self.roi['label']} has no contours.")  
        except:
            raise CUHRTStructureSetException(
                message = ("ERROR: Whilst trying to restore contours for "
                f"{self.roi['label']}.")
            )

    def compare_with_roi(self, roi2: str):
        '''
            Return comparison result for two CUHRTROI objects. 
            roi2 must be a ROI label in the current structure set. 
        '''

        if not self.roi['has_contours']:
            self.load_contours()

        try:
            roi2 = ss.RoiGeometries[roi2]
            roi2 = CUHRTROI(
                roi = {
                    'label': roi2.OfRoi.Name,
                    'colour': None,
                    'has_contours': False,
                    'centroid': roi2.GetCenterOfRoi(), 
                    'volume': roi2.GetRoiVolume(), 
                }
            )
        except Exception as err: 
            raise CUHRTStructureSetException(
                error = err, 
                message = (
                    f"ERROR: Whilst trying to initialise {roi2.OfRoi.Name}."
                )
            )

        return CUHRTCompareROI(
            self, roi2
        )
            
class CUHRTCompareROI():
    '''
        Workhorse or compare_two_rois method of CUHRTROI objects. 

        Attributes:
            • volume_match: bool
            • centroid_match: bool
            • 
    '''

    def __init__(self, roi1, roi2):

        self.volume_match = round(roi1.roi['volume'],2) == round(
            roi2.roi['volume'],2)

        deltas = [abs(delta)>0.01 for delta in [
            roi1.roi['centroid']['x'] - roi2.roi['centroid']['x'],
            roi1.roi['centroid']['y'] - roi2.roi['centroid']['y'],
            roi1.roi['centroid']['z'] - roi2.roi['centroid']['z']
        ]]
        self.centroid_match = not any(deltas)
        try:
            self.roi_comparison_results = ss.ComparisonOfRoiGeometries(
                RoiA = roi1.roi['label'],
                RoiB = roi2.roi['label'],
                ComputeDistanceToAgreementMeasures = True
            )
        except Exception as err: 
            self.roi_comparison_results = None
            raise CUHRTStructureSetException(
                error = err, 
                message = ("ERROR: Whilst trying to compare "
                f"{roi1['label']} and {roi2['label']}."
                )
            )

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
            • rois: list 
                list of CUHRTROI objects 

        Methods:
            • json_export
                exports rudimentary structure set data to json 
            • restore_all_contours
                restore all contours in CUHRTStructureSet object


    '''

    def __init__(self, f_path = None, ss_index: int = None):

        if f_path:
            try: 
                with open(path.normpath(f_path), 'r', encoding='utf-8') as f:
                    data = load(f)
                self.locktime = data['locktime']
                self.reviewer = data['reviewer']
                self.f_name = path.split(f_path)[-1]
                self.rois = [
                    CUHRTROI(roi=roi) for roi in data['rois']
                ]
            except Exception as err:
                raise CUHRTStructureSetException(
                    error = err,
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
                        'colour': ", ".join(
                            [str(rgb_val) for rgb_val in[
                            roi.OfRoi.Color.get_A(), roi.OfRoi.Color.get_R(),
                            roi.OfRoi.Color.get_G(), roi.OfRoi.Color.get_B(),
                         ]]),
                        'centroid': roi.GetCenterOfRoi(), 
                        'volume': roi.GetRoiVolume(), 
                        'has_contours': False
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

            Params:
                f_out: path to output json data. 
                include_contours: bool 
        '''

        if include_contours:
            for roi in self.rois:
                roi.load_contours() 

        self.rois = [roi.roi for roi in self.rois]


        try: 
            with open(path.join(f_out, self.f_name), 
            'w',encoding='utf-8') as f:
                dump(self.__dict__, f, indent=4, sort_keys=True) 
        except Exception as err:
            raise CUHRTStructureSetException(
                error = err, 
                message = (
                    "Could not write RT SS to json.\n"
                )
            ) 

    def restore_all_contours(self):
        '''
            Restore all contours in CUHRTStructureSet object.
        '''
        for roi in self.rois:
            if roi.roi['has_contours']: 
                roi.restore_contours() 

  