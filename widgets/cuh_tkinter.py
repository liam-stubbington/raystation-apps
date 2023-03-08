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

WIDTH = 30

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
        super().__init__(
            parent, width = WIDTH, text = text, background=BLACK,
            justify = tk.CENTER, font = ("Calibri 12"), )

        disp = disp.lower()

        if "warn" in disp:
            self["foreground"] = ORANGE
        elif "good" in disp:
            self["foreground"] = GREEN
        elif "bad" in disp:
            self["foreground"] = RED
        else:
            self["foreground"] = BLUE
        

        self.grid(
            row = row, column = col, sticky = "EW", columnspan=columnspan, 
            rowspan=rowspan, padx = PADX, pady = PADY
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
        self["text"] = text 

        self.grid(
            row = 0, column = 0, sticky = "NSEW", columnspan=columnspan,
            padx = PADX, pady = PADY
        )

class CUHAppButton(tk.Button):
    '''
        Simple button super class with formatting 
    '''
    def __init__(self, parent, text: str, func, row: int, col: int):
        super().__init__(
            parent, 
            background = ORANGE,
            activebackground = RED,
            foreground = BLUE,
            font = ("Calibri 12"),
            text = text, 
            command = func,
            width = WIDTH,
        )

        self.grid(
            row = row, 
            column = col, 
            #sticky = "EW",
            padx = PADX,
            pady = PADY
        )

class CUHDropDownMenu(ttk.Combobox):
    '''
        Simple drop-down menu with formatting 
        self.current() returns index of current selection 
    '''
    def __init__(self, parent, values: list, row: int, col: int, 
    callbackfunc, columnspan: int = 1, rowspan: int = 1, 
    current_selection_index: int = 0, width: int = WIDTH*2):
        #self.current_selection = tk.StringVar()
        self.font = ('Calibri', 12)
        super().__init__(
            parent, font = self.font, state = "readonly", values = values,
            justify = tk.CENTER, height = 15, width = width
        )
        #self.config(textvariable = self.current_selection)
        self.current(current_selection_index)
        
        self.bind("<<ComboboxSelected>>", callbackfunc)

        self.grid(
            row = row, column = col, columnspan=columnspan, 
            rowspan=rowspan, padx = PADX, pady = PADY
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
        activebackground = BLACK, foreground = BLUE, width = WIDTH,
        font = ('Calibri', 12), 
        )

        self.grid(
            row = row, column = col, sticky = "EW", columnspan=columnspan,
            padx = PADX, pady = PADY
        )

class CUHFrame(tk.Frame):
    '''
        Simple frame widget for framing other widgets. 

    '''

    def __init__(self, parent, row: int, col: int, columnspan: int  =1):
        super().__init__(parent, background=BLACK, padx = 0, pady = 0,)
        self.grid(
            row = row, column = col, columnspan=columnspan, sticky='NSEW'
        )

class CUHScrollableFrame(tk.Frame):
    ''' 
        Simple canvas with a RHS vertical scroll bar. 

        Args: 
            - parent: root widget
            - row, col: for grid)
            - height [pixels]

        height - default height of the scrollable window.

        Kwargs: 
            - columnspan: int (default 1)

        Attributes: 
            - canvas 
            - frame
            - vsb 

        The frame attribute is a tk.Frame object for placement of widgets. 
        You will need to columnconfigure for grid etc. 

        Methods: 
            - configure_scroll_region 

    '''
    def __init__(self, parent, row: int, col: int, 
    height: int, columnspan: int = 1):
        super().__init__(
            parent, background=BLACK, padx = 0, pady = 0, 
            )

        self.canvas = tk.Canvas(
            self, borderwidth=0, background=BLACK, height = height
        )
        self.frame = tk.Frame(self.canvas, background=BLACK,)
        self.vsb = tk.Scrollbar(self, orient="vertical", 
        command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0,0), window=self.frame, anchor="nw",)

        self.frame.bind("<Configure>", self.configure_scroll_region)

        self.grid(
            row = row, column = col, columnspan=columnspan, sticky='NSEW'
        )

    def configure_scroll_region(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class CUHHorizontalRule(ttk.Separator):
    '''
        Simple horizontal rule 
    '''
    def __init__(self, parent, row: int, col: int, columnspan:int = 1):
        s = ttk.Style()
        s.configure('TSeparator', background = ORANGE)
        super().__init__(
            parent, orient = tk.HORIZONTAL, style = 'TSeparator', 
        )
       

        self.grid(row=row, column=col, columnspan = columnspan, sticky = "EW")