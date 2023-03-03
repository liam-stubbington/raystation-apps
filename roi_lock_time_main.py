from structure_set_classes import *
from os import path
import tkinter as tk 
from tkinter import filedialog as fd
from widgets.cuh_tkinter import *
from csv import DictWriter


__title__ = "ROI LockTime App"
__version__ = "v0.0.0"

F_ROOT = "//GBCBGPPHFS001.net.addenbrookes.nhs.uk/Planning/ROILockTime"

class ROILockTimeRow(tk.Frame):
    '''
        Each row in the structure set window is an instance of this class. 
        current_roi and reference_roi(s) should be an instance(s) of CUHRTROI.
    '''
    def __init__(
        self, parent, row: int, current_roi, reference_rois: list = None
        ):
        super().__init__(
            parent, background = BLACK, padx = 0, pady = 0 
        )
        self.grid(row=row, column = 0)
        self.columnconfigure((0, 1, 2), weight = 1)
        self.reference_rois = reference_rois 
        self.current_roi = current_roi 

        self.current_roi_label = CUHLabelText(
            self, self.current_roi.roi['label'], 0, 0 
        )

        CUHLabelText(self, 'CF.', 0, 1)

        if self.reference_rois:
            self.selected_roi = CUHDropDownMenu(
                self, [roi.roi['label'] for roi in self.reference_rois], 
                0, 2, self.cf_centroid_and_volume, 
                current_selection_index=self.get_matching_roi_index(),
                width = 30
            )
        else:
            self.selected_roi = CUHDropDownMenu(
                self, [''], 
                0, 2, self.cf_centroid_and_volume, 
                current_selection_index=self.get_matching_roi_index(),
                width = 30
            )


        self.cf_centroid_and_volume()

    def cf_centroid_and_volume(self, event = None):
        '''
            Compare the centroid and volume of the current and reference roi.
        '''
        if not self.reference_rois:
            CUHLabelText(
                self, '', 0, 3, disp="good"
            ) 
        else:
            roi2 = self.reference_rois[
                self.selected_roi.current() 
            ]
            roi1 = self.current_roi
            volume_match = (
                abs(round(roi1.roi['volume'],2) - round(roi2.roi['volume'],2))
                < 1
            )
            deltas = [abs(delta)>0.1 for delta in [
                roi1.roi['centroid']['x'] - roi2.roi['centroid']['x'],
                roi1.roi['centroid']['y'] - roi2.roi['centroid']['y'],
                roi1.roi['centroid']['z'] - roi2.roi['centroid']['z']
            ]]
            centroid_match = not any(deltas)
            if volume_match and centroid_match:
                CUHLabelText(
                    self, 'VOLUME & CENTROID MATCH', 0, 3, disp="good"
                ) 
            elif volume_match and not centroid_match:
                CUHLabelText(
                    self, 'VOLUME MATCH, CENTROID FAIL', 0, 3, disp="WARN"
                ) 
            elif not volume_match and centroid_match:
                CUHLabelText(
                    self, 'VOLUME FAIL, CENTROID MATCH', 0, 3, disp="WARN"
                ) 
            else:
                 CUHLabelText(
                    self, 'FAILURE', 0, 3, disp="bad"
                ) 

    def get_matching_roi_index(self):
        '''
            TO DO
            Find the closest matching roi from list of reference_rois 
            Reference rois must be objects of type CUHRTROI. 
        '''
        if self.reference_rois:
            try: 
                index = [
                    roi.roi['label'] for roi in self.reference_rois
                    ].index(self.current_roi.roi['label'])
            except  ValueError:
                index = 0
        else:
            index = 0
        return index


class ROILockTimeWindow(tk.Tk):
    '''
        Main GUI window of the ROILockTime App. 
    '''
    def __init__(self):

        # -- INITIALISATION -- #
        self.raystation = CUHGetCurrentStructureSetObject() 
        self.structure_sets = [CUHRTStructureSet(sub_structure_set = i)
        for i in self.raystation.ss.SubStructureSets]
        # TO DO
        self.reference_structure_set = None 
        self.sub_structure_set_labels = [
            ss.f_name.split("+")[1:-1] for ss in self.structure_sets
            ]
        self.reference_structure_set_contours_restored = False

        super().__init__() 
        self.title(__title__ + " " + __version__)
        self.configure(background="black")
        self.columnconfigure(0, weight = 1)
        self.iconbitmap(
        "//MOSAIQAPP-20/mosaiq_app/TOOLS/RayStation"
        "/microscope_io/microscope.ico"
        )

        # -- TITLE -- #
        title_row_frame = CUHFrame(self,0,0)
        title_row_frame.columnconfigure(0, weight=1)
        CUHTitleText(title_row_frame, text = __title__ + " " + __version__)
        CUHHorizontalRule(self, 1, 0)

        # -- FIRST ROW -- # 
        first_row_frame = CUHFrame(self, 2, 0)
        first_row_frame.columnconfigure((0,1,2,3), weight=1) 
        CUHLabelText(first_row_frame, "Select Approved SS: ", 0, 0)
        self.ss_dropdown = CUHDropDownMenu(
            first_row_frame, self.sub_structure_set_labels, 0, 1, 
            self.show_current_sub_structure_sets_in_window,
            current_selection_index=len(self.sub_structure_set_labels)-1
        )

        self.current_structure_set = self.structure_sets[
            self.ss_dropdown.current()
            ]

        CUHAppButton(
            first_row_frame, 'Load Reference SS', 
            self.load_reference_structure_set_from_file, 0, 2
            )
        CUHLabelText(
            first_row_frame, 'Check Result', 0, 3
        )
        CUHHorizontalRule(self, 3, 0)

        # -- STRUCTURES -- # 
        self.main_frame = CUHFrame(self, 4, 0)
        self.main_frame.columnconfigure(0, weight =1)
        self.show_current_sub_structure_sets_in_window()

        CUHHorizontalRule(self, 5, 0)

        # -- BOTTOM ROW -- # 
        bottom_row_frame = CUHFrame(self, 6, 0)
        bottom_row_frame.columnconfigure((0,1,2,3), weight=1)
        CUHAppButton(
            bottom_row_frame, 'Export Current SS to json', self.export_to_json,
            0,0
        ) 
        self.include_contours = CUHCheckBox(
            bottom_row_frame, 'Include contours?', 0, 1
        ) 

        CUHAppButton(
            bottom_row_frame, 'Restore reference contours', 
            self.restore_reference_contours,0,2
        ) 

        CUHAppButton(
            bottom_row_frame, 'Compare restored contours', 
            self.export_comparison_of_restored_contours,0,3
        ) 

        self.initial_warning_message()

    def initial_warning_message(self):
        '''
            Shows initial warning about selecting the correct image_set.
            Also centers the window in the displays screen.
        '''
        self.eval('tk::PlaceWindow . center')
        initial_warning = CUHRTWarningMessage(
        message = "In 99.99% of cases you will need to have the RTCT selected\n"
        "to get good results from this script" 
        )
        if not initial_warning.answer:
            exit() 

    def show_current_sub_structure_sets_in_window(self, event = None): 
        self.current_structure_set = self.structure_sets[
            self.ss_dropdown.current()
        ]
        [item.destroy() for item in self.main_frame.winfo_children()]
        for i, roi in enumerate(self.current_structure_set.rois):
            if self.reference_structure_set:
                ROILockTimeRow(
                    self.main_frame, i, roi, 
                    self.reference_structure_set.rois
                )
            else:
                ROILockTimeRow(
                    self.main_frame, i, roi,
                )
    
    def load_reference_structure_set_from_file(self):
        '''
            Load reference structure set into object of class 
            CUHRTStructureSet
        '''
        f_path = fd.askopenfilename(
            filetypes = (('Json File','*.json'),),
            initialdir = F_ROOT,
            title = "Select a json SS to load.",
            
        )

        self.reference_structure_set = CUHRTStructureSet(
            f_path = f_path,
            sub_structure_set=None
        )

        self.show_current_sub_structure_sets_in_window()

        CUHRTWarningMessage(
            title="SUCCESS: ",
            message = (
                "Structure Set data loaded from json: \n"
                f"{path.join(f_path, self.current_structure_set.f_name)}"
            )
        )

    def export_to_json(self):
        '''
            Export selected sub-structure set to JSON. 
        '''
        f_out = F_ROOT
         
        self.current_structure_set.json_export(
            f_out = f_out,
            include_contours=self.include_contours.var.get()
        )

        CUHRTWarningMessage(
            title="SUCCESS: ",
            message = (
                "Structure Set data exported to json: \n"
                f"{path.join(f_out, self.current_structure_set.f_name)}"
            )
        )

    def restore_reference_contours(self):
        '''
            Attempts to restore reference sub-structure set contours 
            into the current exam's structure set. 
        '''
        if self.reference_structure_set is not None:
            self.reference_structure_set.restore_all_contours()
            self.reference_structure_set_contours_restored = True
            CUHRTWarningMessage(
                title = "INFO: ",
                message = ("If contours were found in the reference structure "
                "set, these have been restored into the current exam's "
                "structure set.")
            )
        else:
            CUHRTWarningMessage(
                title = "ERROR: ",
                message = "You must load a reference structure set first."
            )
            self.reference_structure_set_contours_restored = False

    def export_comparison_of_restored_contours(self):
        '''
            If reference contours has been restored into the current structure
            set, it is possible to evaluate Dice and Hausdorff distance for 
            these structures.  
        '''
        list_of_compare_objects = [] 
        roi_geometries = self.raystation.ss.RoiGeometries
        if self.reference_structure_set_contours_restored:
            for roi1 in self.current_structure_set.rois:
                try:
                    index = [
                        roi.OfRoi.Name for roi in roi_geometries
                        ].index(roi1.roi['label']+ " (1)") # TO DO
                    list_of_compare_objects.append(
                        roi1.compare_with_roi(index)
                    )
                except ValueError:
                    continue

            to_csv = [
                compare_object.return_formatted_dict()
                for compare_object in list_of_compare_objects
            ]
            
            headers = to_csv[0].keys()

            csv_file_name = "_".join(
                [self.raystation.patientID, 'ROIComparison.csv']
                ) 

            f_out = path.join(F_ROOT, csv_file_name)

            csv_first_line = (
                f"{self.current_structure_set.f_name} compared with "
                f"{self.reference_structure_set.f_name}.\n\n"
            
            )

            with open(f_out, 'w', encoding='utf-8', newline = '') as f:
                f.write(csv_first_line)
                dw = DictWriter(f, headers)
                dw.writeheader()
                dw.writerows(to_csv)

            CUHRTWarningMessage(
                title = "SUCCESS: ",
                message = (
                    "Structure similarity metrics exported:\n"
                    f"{f_out}."
                )
            )

        else:
            CUHRTWarningMessage(
                title = "ERRROR: ",
                message = ("This method only works through the App if you "
                "have already restored some contours into the current exam's "
                "structure set.")
            )



root = ROILockTimeWindow()
root.mainloop()
