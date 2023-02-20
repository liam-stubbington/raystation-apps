# CUH ROI Classes
This project contains a collection of python modules for interacting with RayStation script objects that fall under the category of Patient Modeling i.e. ROI definition. 

---

## CUHRTStructureSetCompare
This is the workhorse of ROILockTime Script v2+. 

The ROILockTime script exists to provide an auditable history of changes to DR approved Structure Sets. 

If all goes swimmingly, the Dr approved structure set should remain approved throughout the rest of treatment planning. 

Sometimes, the planner needs to unlock the structure set to: 
- Change ROI labels
- Edit ROI colours  
- Move the Localisation point 
- Edit the External 

The CUHRTStructureSetCompare permits the following:
- Export of any sub-structure set with non-zero Review property. 
    - Sub-structure set approval, ROI Centroid, ROI Volume and contours are exported in JSON format
- Import of a structure set back-up from JSON 
- Comparison of Reference and Current ROI geometries 

### Attributes:


### Methods:



---

### RayStation Structure Set handling 

- One structure set per case
- A structure set is a collection or ROIs, POIs 
- Each ROI, POI can have one geometry per Image Set 

RayStation 12A handles structure set approval through the generation of sub-structure sets. This gets confusing. 

- A new sub-structure set is generated upon approval by a new user *(not proven)*
    - May also be linked to the approval ofa plan vs the approval of a structure set. 
- It is possible to lose a sub-structure through multiple approvals by the same user 
- As far as I am aware sub-structure sets do not retain ROI volume and centroid history 
    - OfRoi method 
    - Limited number of test cases 


Note you cannot rely on:
```
ss = case.PatientModel.StructureSets[<exam.Name>].SubStructureSets[<ss_index>]
rois_with_contours = [ roi for roi in ss.RoiStructures if roi.HasContours()]
```
to give you a list of ROIs with contours. Best to check:
```
hasattr(roi.PrimaryShape, "Contours")
```

---

