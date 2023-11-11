import tkinter as tk
from tkinter import ttk
from m30xy.m30xyClass import StageXY

class StageControlFrame(tk.Frame):
    def __init__(self, master, serial_number, status, measurement, optimization, root, *args, **kwargs):
        super().__init__(master, *args, **kwargs, bg="white")
        self.optimization = optimization
        self.keyboard_status = status
        self.rowconfigure((0, 1, 2), weight=1)
        self.stage = StageXY(serial_number, measurement, optimization)
        self.stage.build_device()

        self.create_widgets()
        root.bind("<Key>", self.on_key_press)
                         
    def create_widgets(self):
        # Create labels and style of the widgets
        label = tk.Label(self, text="Stage M30XY", font=("Arial", 10, "bold"), bg="white")
        label.grid(row=0, column=1, pady=10)    

        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10), padding=2)  # Customize the "TButton" style
        style.configure("white.TButton", background="white")  # Define the "white.TButton" style

        # Move in specified direction with arrows and specified steps
        displacement_frame = ttk.LabelFrame(self, text="Move with Steps")
        displacement_frame.grid(row=1, column=0, pady=10)
        displacement_frame.columnconfigure((0, 1, 2), weight=1)

        button_left = ttk.Button(displacement_frame, text="⬅", command=lambda: self.stage.move_l(), style=("TButton", "white.TButton"))
        button_left.grid(row=2, column=0, padx=10)
        button_right = ttk.Button(displacement_frame, text="➡", command=lambda: self.stage.move_r(), style=("TButton", "white.TButton"))
        button_right.grid(row=2, column=2, padx=10)
        button_up = ttk.Button(displacement_frame, text="⬆", command=lambda: self.stage.move_t(), style=("TButton", "white.TButton"))
        button_up.grid(row=1, column=1, pady=10)
        button_down = ttk.Button(displacement_frame, text="⬇", command=lambda: self.stage.move_b(), style=("TButton", "white.TButton"))
        button_down.grid(row=3, column=1)

        # Entry for custom step size
        step_entry = tk.Entry(displacement_frame, width=6)
        step_entry.grid(row=4, column=1, padx=10, pady=10)

        self.step_button = tk.Button(displacement_frame, text="Update step size", command=lambda: self.update_step(int(step_entry.get())), 
                              bg='white')
        self.step_button.grid(row=4, column=0, pady=10, sticky='e')

        # Pre-defined steps - as buttons for convenience
        self.button_1 = tk.Button(displacement_frame, text="2.5 um", command=lambda: self.update_step(25), bg='white')
        self.button_1.grid(row=4, column=2, pady=10)
        self.button_2 = tk.Button(displacement_frame, text="210 um", command=lambda: self.update_step(2100), bg='white')
        self.button_2.grid(row=5, column=0, pady=10)
        self.button_3 = tk.Button(displacement_frame, text="800 um", command=lambda: self.update_step(8000), bg='white')
        self.button_3.grid(row=5, column=1, pady=10)
        self.button_4 = tk.Button(displacement_frame, text="5 mm", command=lambda: self.update_step(50000), bg='white')
        self.button_4.grid(row=5, column=2, pady=10)

        # Change status for keyboard arrow displacement
        keyboard_status_box = tk.Checkbutton(displacement_frame, text='Use keyboard arrows?', command=self.change_keyboard_status, font=("Arial", 10), bg="white")
        keyboard_status_box.grid(row=0,column=1)
        
        # Move to absolute position with respect to the initialization point
        abs_displacement_frame = ttk.LabelFrame(self, text="Move to Location")
        abs_displacement_frame.grid(row=1, column=1, pady=10)

        x_label = tk.Label(abs_displacement_frame, text="X:", font=("Arial", 10), bg="white")
        x_label.grid(row=0, column=0, padx=10, pady=10)
        x_entry = tk.Entry(abs_displacement_frame, width=6)
        x_entry.grid(row=0, column=1, pady=10)

        y_label = tk.Label(abs_displacement_frame, text="Y:", font=("Arial", 10), bg="white")
        y_label.grid(row=1, column=0, padx=10, pady=10)
        y_entry = tk.Entry(abs_displacement_frame, width=6)
        y_entry.grid(row=1, column=1, pady=10)

        move_to_loc_button = ttk.Button(abs_displacement_frame, text="Go", command=lambda: 
                                        self.stage.set_position(int(x_entry.get()), int(y_entry.get())), style=("TButton", "white.TButton"))
        move_to_loc_button.grid(row=2, column=1, pady=10)
        
        # Manual sequence
        manual_sequence_frame = ttk.LabelFrame(self, text="Manual Sequence")
        manual_sequence_frame.grid(row=2, column=1, pady=10)

        manual_sequence_label = tk.Label(manual_sequence_frame, text="Manual sequence", font=("Arial", 10), bg="white")
        manual_sequence_label.grid(row=0,column=0, padx=10, pady=10)
        manual_sequence_entry = tk.Entry(manual_sequence_frame, textvariable=self.optimization.manual_sequence)
        manual_sequence_entry.grid(row=0,column=1)

        is_manual_coordinate_relative_label = tk.Label(manual_sequence_frame, text='Relative coords?', font=("Arial", 10), bg="white")
        is_manual_coordinate_relative_label.grid(row=1, column=0)
        is_manual_coordinate_relative_box = tk.Checkbutton(manual_sequence_frame, variable=self.optimization.manual_rel_coord,
                                                font=("Arial", 10), bg="white")
        is_manual_coordinate_relative_box.grid(row=1, column=1)

        manual_sequence_button = ttk.Button(manual_sequence_frame, text="Optimize man. seq.", command=lambda: 
                                            self.stage.move_sequence(self.optimization.manual_sequence, 
                                            relative=self.optimization.manual_rel_coord.get()), 
                                            style=("TButton","white.TButton"))
        manual_sequence_button.grid(row=2,column=1)
        
        # Optimization 
        optimization_frame = ttk.LabelFrame(self, text="Optimize single device")
        optimization_frame.grid(row=1, column=2, pady=10, sticky='w')

        center_wavelength = tk.Label(optimization_frame, text='Center Wavelength', font=("Arial", 10), bg="white")
        center_wavelength.grid(row=0, column=0, padx=5, pady=5)
        self.center_wavelength_entry = tk.Entry(optimization_frame, textvariable=self.optimization.center_wavelength, width=5)
        self.center_wavelength_entry.grid(row=0, column=1, padx=5, pady=5)
        
        width = tk.Label(optimization_frame, text='Width', font=("Arial", 10), bg="white")
        width.grid(row=1, column=0, padx=5, pady=5)
        width_entry = tk.Entry(optimization_frame, textvariable=self.optimization.width, width=5)
        width_entry.grid(row=1, column=1, padx=5, pady=5)
        
        x_range = tk.Label(optimization_frame, text='x range', font=("Arial", 10), bg="white")
        x_range.grid(row=2, column=0, padx=5, pady=5)
        x_range_entry = tk.Entry(optimization_frame, textvariable=self.optimization.xrange, width=8)
        x_range_entry.grid(row=2, column=1, padx=5, pady=5)
        
        y_range = tk.Label(optimization_frame, text='y range', font=("Arial", 10), bg="white")
        y_range.grid(row=3, column=0, padx=5, pady=5)
        y_range_entry = tk.Entry(optimization_frame, textvariable=self.optimization.yrange, width=8)
        y_range_entry.grid(row=3, column=1, padx=5, pady=5)
    
        optimization_button = ttk.Button(optimization_frame, text='Optimize', width=15, 
                                        command=self.optimization.optimize_single_device, 
                                        style=("TButton","white.TButton"))
        optimization_button.grid(row=4,column=1)

        # Generate device sequence & take measurements
        sequence_frame = ttk.LabelFrame(self, text="Generate Sequence & Take Measurements")
        sequence_frame.grid(row=2, column=0, padx=10, pady=10)
        
        start_label = tk.Label(sequence_frame, text='Start label', font=("Arial", 10), bg="white")
        start_label.grid(row=0, column=0, padx=5, pady=5)
        start_label_entry = tk.Entry(sequence_frame, textvariable=self.optimization.start_label, width=10)
        start_label_entry.grid(row=0, column=1, padx=5, pady=5)
        
        start_x = tk.Label(sequence_frame, text='Start x', font=("Arial", 10), bg="white")
        start_x.grid(row=1, column=0, padx=5, pady=5)
        start_x_entry = tk.Entry(sequence_frame, textvariable=self.optimization.start_x, width=3)
        start_x_entry.grid(row=1, column=1, padx=5, pady=5)
        
        start_y = tk.Label(sequence_frame, text='Start y', font=("Arial", 10), bg="white")
        start_y.grid(row=2, column=0, padx=5, pady=5)
        start_y_entry = tk.Entry(sequence_frame, textvariable=self.optimization.start_y, width=3)
        start_y_entry.grid(row=2, column=1, padx=5, pady=5)
        
        num_devices_per_col = tk.Label(sequence_frame, text='Devices per column', font=("Arial", 10), bg="white")
        num_devices_per_col.grid(row=0, column=2, padx=5, pady=5)
        num_devices_per_col_entry = tk.Entry(sequence_frame, textvariable=self.optimization.num_devices_per_col, width=10)
        num_devices_per_col_entry.grid(row=0, column=3, padx=5, pady=5)
        
        x_increment = tk.Label(sequence_frame, text='x increment', font=("Arial", 10), bg="white")
        x_increment.grid(row=1, column=2, padx=5, pady=5)
        x_increment_entry = tk.Entry(sequence_frame, textvariable=self.optimization.x_increment, width=5)
        x_increment_entry.grid(row=1, column=3, padx=5, pady=5)
        
        y_increment = tk.Label(sequence_frame, text='y increment', font=("Arial", 10), bg="white")
        y_increment.grid(row=2, column=2, padx=5, pady=5)
        y_increment_entry = tk.Entry(sequence_frame, textvariable=self.optimization.y_increment, width=5)
        y_increment_entry.grid(row=2, column=3, padx=5, pady=5)

        # Relative coordinate tickbox
        is_coordinate_relative_label = tk.Label(sequence_frame, text='Relative coords?', font=("Arial", 10), bg="white")
        is_coordinate_relative_label.grid(row=3, column=0)
        is_coordinate_relative_box = tk.Checkbutton(sequence_frame, variable=self.optimization.rel_coord,
                                                font=("Arial", 10), bg="white")
        is_coordinate_relative_box.grid(row=3, column=1)
        
        gen_sequence_button = ttk.Button(sequence_frame, text='Generate seq & measure', 
                                         command=self.stage.gen_mes_seq, 
                                         style=("TButton","white.TButton"))
        gen_sequence_button.grid(row=3,column=2)
        
    # Update the status of the keyboard interaction
    def change_keyboard_status(self):
        if self.keyboard_status == "off":
            self.keyboard_status = 'on'
            print("Keyboard active")
        elif self.keyboard_status == "on":
            self.keyboard_status = 'off'
            print("Keyboard inactive")
    
    def on_key_press(self, event):
        if self.keyboard_status == 'on':
            if event.keysym == "Up":  # Replace "Up" with the key you want to trigger the function"
                self.stage.move_t()
                print('Going up...')
            elif event.keysym == "Down":
                self.stage.move_b()
                print('Going down...')
            elif event.keysym == "Left":
                self.stage.move_l()
                print('Going left...')
            elif event.keysym == "Right":
                self.stage.move_r()
                print('Going right...')

    def update_step(self, size):
        self.update_step_buttons(size)
        self.stage.update_step(size)

    def update_step_buttons(self, size):
        self.button_1.configure(bg='white')
        self.button_2.configure(bg='white')
        self.button_3.configure(bg='white')
        self.button_4.configure(bg='white')
        self.step_button.configure(bg='white')
        if size == 25: 
            self.button_1.configure(bg='green')
        elif size == 2100:
            self.button_2.configure(bg='green')
        elif size == 8000:
            self.button_3.configure(bg='green')
        elif size == 50000:
            self.button_4.configure(bg='green')
        else:
            self.step_button.configure(bg='green')
  
# TO DO : turn off the device when the window is closed