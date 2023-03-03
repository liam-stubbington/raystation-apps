# CUH Widget Script Objects 
This package contains a collection of script objects that can be used to create scripting GUIs. 

It is all based on the tkinter module which comes packaged as part of the python standard library.  

Requirements: 
- Python 3.6 or greater

---
## Quick start guide 
Best illustrated with some example code. 

```
__title__ = "My App Title"
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
1, 2, lambda x: print('Drop Down Menu Option changed'))

a_radio_button = CUHCheckBox(root, 'Selection',2,0, columnspan=3 )


root.mainloop()
```

This produces the following:

![Example GUI](/widgets/example_gui.PNG "A simple GUI using CUH widgets.")

---
## Reference guide 

## Revision History
