# CUH ROI Classes
This project contains a collection of python modules for interacting with RayStation Patient Modelling script objects.

---

## End User Guide 
Volume match is within ± 1cc, centroid match is within 1mm.

## CUHRTException 
Custom exception. 
Presents a tkinter messagebox with a customizable error message and the TraceBack. 

### Attributes: 
- message: str
    - Custom error message. 
- err: str
    - TraceBack error message (optional).

### Example usage 
```
    try:
        some_object.do_something() 
    except Exception as err:
        raise CUHRTStructureSetException(
            message = (
                "ERROR!: Some helpful debug info here."
            ),
            error = err,
        )
```
---

## CUHRTROI
Helper class that forms the objects in the CUHRTStructureSet class. By default, no contour information is stored to improve performance. 

### Attributes:
- roi: dict
    - label, volume, centroid, colour, contours, has_contours 

### Methods:
- load_contours 
    - attempts to load the contours into memory from the current structure set 
- restore contours 
    - attempts to add the contours stored in memory back in to the current structure set. 
    - steps:
        - create a new ROI 
        - create a cylinder geometry 
        - change the geometry to match the contours in memory 
    - **accuracy is not guaranteed.**
- compare_with_roi
    - params:
        - roi2: *shallow* CUHRTROI object - no contours or colour.
    - returns: object of class CUHRTCompareROI 

### Example usage 
It is best to start with a RayStation SubStructureSet object `ss = case.PatientModel.StructureSets[<exam.Name>].SubStructureSets[<sub_structure_set_index>]`. 
```
    roi = ss.RoiStructures[<index>]
    my_roi = CUHRTROI(
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
        }
    )

```
Then run the methods. 
```
    my_roi.load_contours() 
    my_roi.restore_contours() 
```
See notes on CUHRTCompareROI for use of the `my_roi.compare_with_roi()` method. 

---

## CUHRTCompareROI
Object template for comparing two CUHRTROI objects. Interacts with the current structure set in RayStation. RayStation does all the hard work by providing a method for calculating similarity metrics like. This is a powerful way of numerically auditing changes to structures. 

### Attributes: 
- volume_match: bool
    - return true if the two CUHRTROI objects have volumes within 0.5cm<sup>3<sup>  
- centroid_match: bool
    - return true if the two CUHRTROI objects have IEC DICOM Patient X, Y Z within ±0.1mm  
- roi_comparison_results: dict
    - RayStation ComparisonOfRoiGeometries() kwargs:
        - DiceSimilarityCoefficient
        - Precision
        - Sensitivity
        - Specificity
        - MeanDistanceToAgreement
        - MaxDistanceToAgreement

### Example usage 
Assuming you have access to two CUHRTROI objects in the namespace as `roi1` and `roi2`. The following will compare roi1 and roi2. 

```
    compare_roi_object = roi1.compare_with_roi(roi2.roi['label'])

    print(f"ROI 1: {roi1.roi['label']}")
    print(f"ROI 2: {roi2.roi['label']}")

    print(f"Centroid match: {compare_roi_object.centroid_match}.")
    print(f"Volume match: {compare_roi_object.volume_match}.")
    for k,v in compare_roi_object.roi_comparison_results.items():
        print(f"{k}: {v}")
```

---

## CUHRTStructureSet
This is the workhorse of the ROILockTime script. It is best instantiated from a RayStation SubStructureSet object - this is necessary because the SubStrutureSet object holds the structure set approval. 

### Initialisation 
The object can be committed to disc in .json format. You have two options for initialisation either:

1. `my_ss_obj = CUHRTStructureSet(ss_index=1)` in which case the object comes from the current SubStructureSet identified by `ss_index`.
2. `my_ss_obj = CUHRTStructureSet(f_path = "./some_json_file.json")` if you want to read back in from disc.  

### Attributes:
- locktime: str 
- reviewer: str
- f_name: str 
- rois: list 
    - list of CUHRTROI objects 

### Methods:
- json_export
    - params:
        - exports object data to json
        - f_out: str 
        - include_contours: bool = False 
- restore_all_contours
    - restore all contours in CUHRTStructureSet object

### Example usage:

```
    my_ss_obj = CUHRTStructureSet(ss_index=1)

    print(my_ss_obj.locktime)
    print(my_ss_obj.reviewer) 
    print([roi.roi['label'] for roi in my_ss_obj.rois])

    my_ss_obj.json_export(
        f_out = "./some_root_folder",
        include_contours=True
    )

    my_ss_obj.restore_all_contours()

```
---
Liam Stubbington <br> RT Physicist
<br>Cambridge University Hospitals NHS Foundation Trust

liam.stubbington@NHS.net