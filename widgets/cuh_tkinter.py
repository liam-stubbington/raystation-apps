'''
Collection of script objects for creating GUIs.

Author: Liam Stubbington
RT Physicist, Cambridge University Hospitals NHS Foundation Trust

'''

import tkinter as tk 
import tkinter.ttk as ttk

BLACK = "#000000"
RED = "#EC4E20"
ORANGE = "#FF9505"
BLUE = "#016FB9"
GREEN = "#48E5C2"

PADX = 5 
PADY = 5

class CUHLabelText(tk.Label):
    '''
        Display strings as formatted text. 
        Initialise with positional arguments:
            - parent (parent widget frame or window)
            - text (string)
            - row, column (control placement in parent)
            - disp ("good", "bad", "warn", "info" -> determines colour)
    '''

    def __init__(
        self, parent, text: str, row: int, col: int, disp: str = "info",
        columnspan: int = 1, rowspan: int = 1):
        super().__init__(parent)

        disp = disp.lower()

        self["text"] = text 
        self["font"] = ("Calibri 12")
        self["justify"] = tk.CENTER
        self["background"] = BLACK
        if "warn" in disp:
            self["foreground"] = ORANGE
        elif "good" in disp:
            self["foreground"] = GREEN
        elif "bad" in disp:
            self["foreground"] = RED
        else:
            self["foreground"] = BLUE
  
        self["pady"] = PADY
        self["padx"] = PADX
        

        self.grid(
            row = row, column = col, sticky = "EW", columnspan=columnspan, 
            rowspan=rowspan,
        )

class CUHTitleText(tk.Label):
    '''
    Similar to CUHLabelText but bold formatting. 
    Expected to occupy the top row of the window. 
    '''
    def __init__(self, parent, text, columnspan: int = 1):
        super().__init__(parent) 

        self["font"] = ("Calibri 14 bold")
        self["foreground"] = ORANGE
        self["background"] = BLACK
        self["padx"] = PADX
        self["pady"] = PADY
        self["text"] = text 

        self.grid(
            row = 0, column = 0, sticky = "NSEW", columnspan=columnspan
        )

class CUHAppButton(tk.Button):
    '''
        Simple button super class with formatting 
    '''
    def __init__(self, parent, text: str, func, row, col):
        super().__init__(
            parent, 
            background = ORANGE,
            activebackground = RED,
            foreground = BLUE,
            pady = PADX,
            padx = PADY, 
            font = "Calibri 12",
            text = text, 
            command = func,
        )

        self.grid(
            row = row, 
            column = col, 
            sticky = "EW"
        )

class CUHDropDownMenu(ttk.Combobox):
    '''
        Simpe drop-down menu with formatting 

    '''
    def __init__(self, parent, values: list, row: int, col: int, 
    columnspan: int = 1, rowspan: int = 1):
        self.font = ('Calibi', 12)
        super().__init__(
            parent, font = self.font, state = "readonly", values = values,
            justify = tk.CENTER, height = 10, width = 10
        )
        

        self.grid(
            row = row, column = col, sticky = "EW", columnspan=columnspan, 
            rowspan=rowspan, 
        )

class CUHCheckBox(tk.Checkbutton): 
    '''
        Boolean Check Box. 
        self.var.get() returns checkbox state, 1, 0
    '''
    def __init__(self, parent, text: str, row: int, col: int, 
    columnspan: int = 1):
        self.var = tk.IntVar(parent, value = 0)
        super().__init__(parent, text = text, variable = self.var, 
        justify=tk.CENTER, background = BLACK,
        activebackground = BLACK, foreground = BLUE, pady = PADX, padx = PADY,
        font = ('Calibi', 12),
        )

        self.grid(
            row = row, column = col, sticky = "EW", columnspan=columnspan
        )
