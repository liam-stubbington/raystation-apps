# CUH Widget Script Objects 
This package contains a collection of script objects that I have used to create scripting GUIs. 

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

### General 
All of these widgets use tkinter's grid method to position widgets on a window. You must therefore provide a row and column position in instance definitions. 

In what follows, default values are specified in parentheses. 

### CUHFrame
Used as a place holder for other widgets. 

Args:
- parent: root widget 
- row
- col

Kwargs:
- columnspan (optional, 1)

### CUHLabelText
Simple display of formatted text. 

Args:
- parent: root widget 
- text: str 
- row: int
- col: int

Kwargs: 
- disp: str (default "info")

The disp kwarg is used to colour code the appearance. Good, Bad, Warn or Info result in Green, Red, Orange and Blue text. 

### CUHTitleText
As above, but with bold size 14 text. 

Args:
- parent: root widget 
- text: str
- row
- col

Kwargs:
- columnspan (optional, 1)

### CUHAppButton
Args:
- parent: root widget 
- text: str 
- func
- row: int
- col: int

Pass any function as a positional argument to bind button selection to function execution. 

### CUHDropDownMenu
Simple drop down menu. 

Args:
- parent: root widget 
- values: list 
- row: int
- col: int
- callbackfunc 

Kwargs:
- columnspan: int (optional, 1)
- rowspan: int (optional, 1)
- current_selection_index: int (optional, 0)
- width: int (optional)

`CUHDropDownMenu.current()` returns the index of the current selection from the list `values`. 

`callbackfunc` is evoked every time the selection is changed by the user. For this to work, your function will need to accept an `event` argument. 

```
drop_down = CUHDropDownMenu(
    parent, ['select','1','from','this','list'], 0, 0)
)

def some_function(event = None):
    current_selection = drop_down.current() 
    print(f"Option selected: {current_selection}.")
```

### CUHCheckBox
Simple binary radio button.

Args: 
- parent: root widget 
- text: str 
- row: int
- col: int

Kwargs: 
- columnspan: int (optional, 1)

The state of any CUHCheckBox instance can be obtained by `self.var.get()` a 1 or 0 is returned. 

### CUHHorizontalRule
Simple horizontal line. 

Args:
- parent: root widget 
- row: int
- col: int

Kwargs:
- columnspan: int (optional, 1)

----