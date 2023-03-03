from connect import get_current 
from os import path
from sys import exit
from json import load, dump, dumps
from datetime import datetime as dt
from tkinter import Tk
from tkinter import messagebox as mb
from tkinter.messagebox import WARNING

class CUHGetCurrentStructureSetObject():
    '''
        Script object used to get the current structure set properties in 
        RayStation. 

        Subsequent script objects inherit from this. 
    '''
    def __init__(self):

        self.exam = get_current("Examination")
        self.patientID = get_current("Patient").PatientID
        self.case = get_current("Case")

        self.ss = self.case.PatientModel.StructureSets[
            self.exam.Name]
  

class CUHRTWarningMessage(): 
    ''' 
        Warns the user about selecting the RTCT image set. 
        Returns True or False. 
    '''
    def __init__(self, title: str = "WARNING: ", message: str = None):
        
        root = Tk()
        root.iconbitmap(
            "//MOSAIQAPP-20/mosaiq_app/TOOLS/RayStation"
            "/microscope_io/microscope.ico"
            )
        root.withdraw() 
        self.answer = mb.askokcancel(
            title = title,
            message = message,
            icon = WARNING
        )
        root.destroy() 


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
            "//MOSAIQAPP-20/mosaiq_app/TOOLS/RayStation"
            "/microscope_io/microscope.ico"
            )
        root.withdraw() 
        mb.showerror(
            title = "ERROR: CUHRTStructureSetException",
            message = self.message
        ) 
        super().__init__(self.message)
        exit()

class CUHRTROI(CUHGetCurrentStructureSetObject):
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
            • unload_contours
                opposite of above 
            • restore_contours
                adds structures back in to current structure set from file
            
    '''

    def __init__(self, roi: dict, ):
        super().__init__()
        self.roi = roi 
            
    def load_contours(self):
        '''
            Attempts to load contours into memory from RayStation get_current
            Patient Model object. 
        '''
        roi = self.ss.RoiGeometries[self.roi['label']]

        try:
            if hasattr(roi.PrimaryShape, "Contours"):
                self.roi['contours'] = [
                    contour for contour in roi.PrimaryShape.Contours
                ]
                self.roi['has_contours'] = True
            else:
                print(f"No contours for roi: {self.roi['label']}.")
                self.roi['has_contours'] = False
        except:
            raise CUHRTStructureSetException(
                message = (
                    "ERROR: Could not load contours for "
                    f"{self.roi['label']}."
                )
            )

    def unload_contours(self):
        '''
            Attempts to remove contours from the current CUHRTROI 
            if loaded into memory 
        '''
        if 'contours' in self.roi.keys():
            self.roi.pop('contours') 
            self.roi['has_contours'] = False


    def restore_contours(self):
        '''
            Attempts to add contours from the CUHRTROI object 
            onto the current examination. 
        '''        
        print(f"Attempting to recreate ROI: {self.roi['label']}")

        new_roi_name = self.case.PatientModel.GetUniqueRoiName(
            DesiredName = self.roi["label"]
            )

        self.case.PatientModel.CreateRoi(
            Name = new_roi_name,Type = "Undefined",
            Color = self.roi['colour'],
        )

        new_roi = self.case.PatientModel.RegionsOfInterest[new_roi_name]

        new_roi.CreateBoxGeometry(
            Size={"x":2,"y":2,"z":2},Examination = self.exam,
            Center = {"x":0,"y":0,"z":0},Representation = 'Voxels',
            VoxelSize = None
        )

        new_roi_geometry = self.ss.RoiGeometries[new_roi_name]
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
            roi2 must be a ROI label, or index, in the current structure set. 
        '''

        if not self.roi['has_contours']:
            self.load_contours()

        try:
            roi2 = self.ss.RoiGeometries[roi2]
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
            
class CUHRTCompareROI(CUHGetCurrentStructureSetObject):
    '''
        Workhorse or compare_two_rois method of CUHRTROI objects. 

        Attributes:
            • reference_roi_label 
            • compare_roi_label
            • reference_volume: float 
            • compare_volume: float 
            • volume_match: bool
            • reference_centroid: dict
            • compare_centroid: dict
            • centroid_match: bool
            • roi_comparison_results
                - RayStation method of extracting Dice and Hausdorff distance
        
        Methods:
            • return_formatted_dict
    '''

    def __init__(self, roi1, roi2):
        super().__init__()
        self.reference_roi_label = roi1.roi['label']
        self.reference_roi_volume = roi1.roi['volume']
        self.reference_roi_centroid = roi1.roi['centroid']
        self.compare_roi_label = roi2.roi['label']
        self.compare_roi_volume = roi2.roi['volume']
        self.compare_roi_centroid = roi2.roi['centroid']
        self.volume_match = round(roi1.roi['volume'],2) == round(
            roi2.roi['volume'],2)

        deltas = [abs(delta)>0.01 for delta in [
            roi1.roi['centroid']['x'] - roi2.roi['centroid']['x'],
            roi1.roi['centroid']['y'] - roi2.roi['centroid']['y'],
            roi1.roi['centroid']['z'] - roi2.roi['centroid']['z']
        ]]
        self.centroid_match = not any(deltas)
        try:
            self.roi_comparison_results = self.ss.ComparisonOfRoiGeometries(
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
    
    def return_formatted_dict(self) -> dict: 
        '''
            Returns a nicely formatted dict of CUHRTCompareROI object 
        '''
        return {
            'Reference ROI Label': self.reference_roi_label,
            'Reference ROI Volume [cc]': self.reference_roi_volume,
            'Reference ROI Centroid [cm]': self.reference_roi_centroid,
            'Compare ROI Label': self.compare_roi_label,
            'Compare ROI Volume [cc]': self.compare_roi_volume,
            'Compare ROI Centroid [cm]': self.compare_roi_centroid,
            'DICE': self.roi_comparison_results['DiceSimilarityCoefficient'],
            'Precision': self.roi_comparison_results['Precision'],
            'Sensitivity': self.roi_comparison_results['Sensitivity'],
            'Specificity': self.roi_comparison_results['Specificity'],
            'MeanDistanceToAgreement': self.roi_comparison_results[
                'MeanDistanceToAgreement'
            ],
            'MaxDistanceToAgreement': self.roi_comparison_results[
                'MaxDistanceToAgreement'
            ],
        }

class CUHRTStructureSet(CUHGetCurrentStructureSetObject):
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

    def __init__(self, sub_structure_set = None, f_path = None, ):
        super().__init__()

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
                     
        elif sub_structure_set is not None:

            try:
                rev = sub_structure_set.Review.ReviewTime
                self.locktime = dt(
                    year = rev.Year, month = rev.Month, day = rev.Day, 
                    hour = rev.Hour, minute = rev.Minute, 
                    second = rev.Second).strftime("%m_%d_%Y_%H_%M_%S")
                self.reviewer = sub_structure_set.Review.ReviewerFullName.replace("^"," ")
                self.f_name = "+".join(
                    [
                        self.patientID,
                        self.reviewer.replace(" ","_"),
                        self.locktime,
                        ".json"
                    ]
                )
            except:
                self.locktime = None 
                self.reviewer = None 
                self.f_name = "+".join(
                    [
                        self.patientID,
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
                ) for roi in sub_structure_set.RoiStructures
                if roi.HasContours()
            ]

        else:
            raise CUHRTStructureSetException(
                    message = (
                        "No Sub-StructureSet index selected. \n"
                        "Or json file path provided."
                ))


    def json_export(self, f_out: str, include_contours: bool = False):
        '''
            Write contents of CUHRTStructureSet to 
            JSON.

            Params:
                f_out: path to output json data. 
                include_contours: bool 
             
        '''

        if include_contours:
            for roi in self.rois:
                roi.load_contours() 
        else: 
            for roi in self.rois:
                roi.unload_contours()
 
        json_data_out = {
            "f_name" : self.f_name,
            "locktime" : self.locktime,
            "reviewer" : self.reviewer,
            "rois": [roi.roi for roi in self.rois]
        }

        try: 
            with open(path.normpath(path.join(f_out, self.f_name)), 
            'w',encoding='utf-8') as f:
                dump(json_data_out, f, indent=4, sort_keys=True) 
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
