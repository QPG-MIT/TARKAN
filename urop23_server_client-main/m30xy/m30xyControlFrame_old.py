import tkinter as tk
from tkinter import ttk
from m30xy.m30xyClass_old import m30XY

class StageControlFrame(tk.Frame):
    def __init__(self, master, serial_number, status, *args, **kwargs):
        super().__init__(master, *args, **kwargs,bg="white")
        self.stage = m30XY(serial_number, status)
        self.stage.build_device()
        self.create_widgets()
        self.master.bind("<KeyPress>", self.key_press)
                         
    def create_widgets(self):

        # Create labels and style of the widgets
        label = tk.Label(self, text="Stage M30XY", font=("Arial", 10, "bold"), bg="white")
        label.grid(row=0, column=1, pady=10)

        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10), padding=2)  # Customize the "TButton" style
        style.configure("white.TButton", background="white")  # Define the "white.TButton" style

        # Arrows for displacements in all directions
        button_left = ttk.Button(self, text="⬅", command=lambda: self.stage.move_l(), style=("TButton", "white.TButton"))
        button_left.grid(row=2, column=0, padx=10)
        button_right = ttk.Button(self, text="➡", command=lambda: self.stage.move_r(), style=("TButton", "white.TButton"))
        button_right.grid(row=2, column=2, padx=10)
        button_up = ttk.Button(self, text="⬆", command=lambda: self.stage.move_t(), style=("TButton", "white.TButton"))
        button_up.grid(row=1, column=1, pady=10)
        button_down = ttk.Button(self, text="⬇", command=lambda: self.stage.move_b(), style=("TButton", "white.TButton"))
        button_down.grid(row=3, column=1)

        # Entry for the steps
        step_entry = tk.Entry(self)
        step_entry.grid(row=4, column=0, columnspan=2, pady=10)

        button_ok = ttk.Button(self, text="OK", command=self.stage.update_step(step_entry.get()), style=("TButton", "white.TButton"))
        button_ok.grid(row=4, column=2, columnspan=1, pady=10)
        
        # Defined steps - as buttons for easiness -
        button_1 = ttk.Button(self, text="2.5 um", command=lambda: self.stage.update_step(25), style=("TButton", "white.TButton"))
        button_1.grid(row=5, column=0, pady=10)
        button_2 = ttk.Button(self, text="210 um", command=lambda: self.stage.update_step(2100), style=("TButton", "white.TButton"))
        button_2.grid(row=5, column=1, pady=10)
        button_3 = ttk.Button(self, text="800 um", command=lambda: self.stage.update_step(8000), style=("TButton", "white.TButton"))
        button_3.grid(row=5, column=2, pady=10)
        button_4 = ttk.Button(self, text="5 mm", command=lambda: self.stage.update_step(50000), style=("TButton", "white.TButton"))
        button_4.grid(row=5, column=3, pady=10)

        # Define the position w.r.t. the reference
        label_x = tk.Label(self, text="X:", font=("Arial", 10), bg="white")
        label_x.grid(row=6, column=0, pady=10)
        entry_x = tk.Entry(self)
        entry_x.grid(row=6, column=1, pady=10)

        label_y = tk.Label(self, text="Y:", font=("Arial", 10), bg="white")
        label_y.grid(row=7, column=0, pady=10)
        entry_y = tk.Entry(self)
        entry_y.grid(row=7, column=1, pady=10)

        button_go = ttk.Button(self, text="Go", command=lambda: self.stage.set_position(entry_x, entry_y), style=("TButton", "white.TButton"))
        button_go.grid(row=6, column=3, rowspan=2, pady=10)
        
        # Change status for keyboard arrow displacement
        status_button = ttk.Button(self, text="Arrows", width=15, command=self.change_status, style=("TButton","white.TButton"))
        status_button.grid(row=1,column=3)

    
    # Update the status of the keyboard interaction
    def change_status(self):
        current_status = self.stage.get_status()
        if current_status == "off":
            self.stage.set_status("on")
            print("Keyboard active")
        elif current_status == "on":
            self.stage.set_status("off")
            print("Keyboard inactive")
            
    # Event sensing with keyboard -Doesn't work-
    def key_press(self, event):
        if self.stage.get_status() == "on":
            if event.keysym == "Up":
                self.stage.move_t()
                print("Up Key")
            elif event.keysym == "Down":
                self.stage.move_b()
            elif event.keysym == "Right":
                self.stage.move_r()
            elif event.keysym == "Left":
                self.stage.move_l()

    # Turn off the device
    def __del__(self):
        self.stage.close_device()


# TO DO : turn off the device when the window is closed