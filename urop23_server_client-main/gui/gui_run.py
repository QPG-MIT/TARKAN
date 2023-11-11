import os
import sys
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd()) 
from ctypes import *  # This is generally bad practice, but done here for brevity
import tkinter as tk
from m30xy.m30xyControlFrame import StageControlFrame
from SuperK.SuperKControlFrame import SuperKControlFrame
from WinSpec.WinSpecControlFrame import WinSpecControlFrame
from HMP4040.hmp4040ControlFrame import hmpControlFrame
from measurement import Measurement
from optimization import Optimization
# Yakalarsam kis kis
class App:
    def __init__(self, master):
        self.master = master
        self.master.title("TARKAN")
        self.master.geometry("950x450")  # Taille initiale de la fenêtre
        self.selected_options = []
        self.option_frames = {}

        # Put a canvas in the master frame, along with scroll bars
        self.canvas = tk.Canvas(self.master)
        self.horizontal_scrollbar = tk.Scrollbar(
            self.master, orient="horizontal", command=self.canvas.xview)
        self.vertical_scrollbar = tk.Scrollbar(
            self.master, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(
            yscrollcommand=self.vertical_scrollbar.set,
            xscrollcommand=self.horizontal_scrollbar.set)
       
        self.inner_frame = tk.Frame(self.canvas, width=1400, height=1000)
        self.inner_frame.pack()
        
        # Pack the scroll bars and the canvas
        self.horizontal_scrollbar.pack(side="bottom", fill="x")
        self.vertical_scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0,0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", self.on_frame_configure)
        
        # provide clean-up code to be executed after pressing 'X' to close the Tarkan app
        self.master.protocol("WM_DELETE_WINDOW", self.on_close) 

        self.measurement = Measurement(None, None, None)
        self.optimization = Optimization(None, None, None)
        self.laser = None
        self.hmp = None
        self.stage = None
        self.create_menu()

    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


    def create_menu(self):
        menubar = tk.Menu(self.master)
        options_menu = tk.Menu(menubar, tearoff=0)
        options_menu.add_checkbutton(label="Laser", command=lambda: self.option_clicked("laser"))
        options_menu.add_checkbutton(label="Hmp4040", command=lambda: self.option_clicked("hmp"))
        options_menu.add_checkbutton(label="Spectrometer", command=lambda: self.option_clicked("spectrometer"))
        options_menu.add_checkbutton(label="Stage", command=lambda: self.option_clicked("stage"))
        menubar.add_cascade(label="Options", menu=options_menu)
        self.master.config(menu=menubar)

    def option_clicked(self, option):
        if option not in self.selected_options:
            self.selected_options.append(option)
            self.create_option_frame(option)
        else:
            self.selected_options.remove(option)
            self.destroy_option_frame(option)

    def create_option_frame(self, option):
        if option == "laser":
            frame = SuperKControlFrame(self.inner_frame,'10C4:EA60')
            self.laser = frame.superk
            self.measurement.laser = frame.superk
            self.optimization.laser = frame.superk
            frame.place(x = 1050, y = 0)
        elif option == "hmp":
            frame = hmpControlFrame(self.inner_frame, 'ASRL7::INSTR', self.measurement)
            self.hmp = frame.hmp
            self.measurement.hmp = frame.hmp
            frame.place(x = 1050, y = 300)
        elif option == "spectrometer":
            frame = WinSpecControlFrame(self.inner_frame, '18.25.30.120', 36577, True, self.measurement)
            self.measurement.spect = frame.spect
            self.optimization.spect = frame.spect
            frame.place(x = 0, y = 500)
        elif option == 'stage':
            frame = StageControlFrame(self.inner_frame, serial_number=b"101362194", status="off", measurement=self.measurement,
                                      optimization=self.optimization, root=self.master)
            self.stage = frame.stage
            self.optimization.stage = frame.stage
            frame.place(x = 0, y = 0)
            
        else:
            frame = None
            
        frame.configure(borderwidth=2, relief="solid")
        self.option_frames[option] = frame
        
    def destroy_option_frame(self, option):
        frame = self.option_frames[option]
        frame.destroy()
        if option == 'laser':
            self.laser._Close()
        del self.option_frames[option]

    def on_close(self):
        '''
        Run clean-up code after hitting 'X' to close the main window
        '''
        self.display_warning() # display the warning message for lifting the probes 
        try:
            self.laser.off() # turn off the laser
            self.laser._Close() # close the serial connection to the laser
        except:
            pass    
        try:
            self.hmp.disable_output() # disable hmp output
        except:
            pass
        try:
            self.stage.close_device() # disconnect the motors
        except:
            pass
        self.master.destroy()
        print('Tarkan is closed.')
        
    def display_warning(self):
        '''
        Displays a warning box before Tarkan is closed, reminding the user to make sure the probes are lifted from the chip.
        '''
        warning = tk.Toplevel(self.master)
        warning.title('Warning')
        warning.geometry("450x100")
        label = tk.Label(warning, text='Please ensure that you have lifted the probes from the chip before clicking OK!')
        label.pack(padx=20, pady=10)
        
        ok_button = tk.Button(warning, text='OK', command=warning.destroy)
        ok_button.pack(pady=5)
        warning.wait_window()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
