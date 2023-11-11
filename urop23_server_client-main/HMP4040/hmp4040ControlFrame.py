import sys, os
sys.tracebacklimit = 0
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd()) 
import tkinter as tk
from tkinter import ttk
from HMP4040.hmp4040Class import HMP4040

#################################
# DO NOT FORGET TO UNCOMMENT SELF.HMP, AND ALL THE OTHER REFERENCES TO HMP 
#################################

class InvalidChannel(Exception):
    pass

class InvalidZero(Exception):
    pass

class InvalidPause(Exception):
    pass

class InvalidStep(Exception):
    pass

class InvalidEnd(Exception):
    pass

class InvalidStart(Exception):
    pass

class hmpControlFrame(tk.Frame):
    def __init__(self, master, hmp_com_port, measurement):
        super().__init__(master, bg="white")
        self.hmp = HMP4040(hmp_com_port)
        self.measurement = measurement
        self.channel_voltages = [1] * 4  # Initialize channel voltages to 1
        self.channel_currents = [1] * 4
        self.sweep_start_volt = 0
        self.sweep_end_volt = 0
        self.sweep_step = 0
        self.sweep_pause = 0
        self.sweep_channels_list = []
        self.sweep_zero = 'no'
        self.create_widgets()

    def create_widgets(self):
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10), padding=2)  # Customize the "TButton" style
        style.configure("white.TButton", background="white")  # Define the "white.TButton" style

        output_frame = ttk.LabelFrame(self, text="")
        output_frame.grid(row=0, column=0, padx=10, pady=10)

        label = tk.Label(output_frame, text="Voltage Source", font=("Arial", 15, "bold"), bg="white")
        label.grid(row=1, column=0)

        # Output generation button

        self.on_off_button = tk.Button(output_frame, text="OFF", command=self.toggle_on_off, bg="red")
        self.on_off_button.grid(row=1, column=1)

        # Channel voltages and currents

        channel_labels = ["Channel 1", "Channel 2", "Channel 3", "Channel 4"]
        self.voltage_entries = []
        self.voltage_displays = []
        self.current_entries = []
        self.current_displays = []
        for i, label_text in enumerate(channel_labels):
            label = tk.Label(output_frame, text=label_text, font=("Arial", 10), bg="white")
            voltage_entry = tk.Entry(output_frame, width=5)
            voltage_display = tk.Label(output_frame, text="{} V".format(self.channel_voltages[i]), font=("Arial", 12), bg="white")
            current_entry = tk.Entry(output_frame, width=5)
            current_display = tk.Label(output_frame, text="{} A".format(self.channel_currents[i]), font=("Arial", 12), bg="white")
         
            label.grid(row=i + 2, column=0, pady=10, sticky='w')
            voltage_entry.grid(row=i + 2, column=0, pady=10, padx=(0, 5), sticky='e')
            voltage_display.grid(row=i + 2, column=1, pady=10, sticky='w')
            current_entry.grid(row=i + 2, column=1, pady=10, padx=(0, 5), sticky='e')
            current_display.grid(row=i + 2, column=2, pady=10)

            self.voltage_entries.append(voltage_entry)
            self.voltage_displays.append(voltage_display)
            self.current_entries.append(current_entry)
            self.current_displays.append(current_display)

        update_channel_parameter_button = ttk.Button(output_frame, text="OK", command=self.update_channel_parameters, style=("TButton", "white.TButton"))
        update_channel_parameter_button.grid(row=7, column=1, pady=10)

        # Sweeping

        sweep_frame = ttk.LabelFrame(self, text="")
        sweep_frame.grid(row=1, column=0, padx=10, pady=10)

        sweep_display = tk.Label(sweep_frame, text='Sweep Settings', font=("Arial", 15, 'bold'), bg="white")
        sweep_display.grid(row=8, column=0, pady=10)

        sweep_start = tk.Label(sweep_frame, text='Starting voltage', font=("Arial", 10), bg="white")
        self.sweep_start_entry = tk.Entry(sweep_frame, width=5)
        self.sweep_start_display = tk.Label(sweep_frame, text="{} V".format(self.sweep_start_volt), font=("Arial", 12), bg="white")

        sweep_start.grid(row=9, column=0, pady=10)
        self.sweep_start_entry.grid(row=9, column=1, pady=10)
        self.sweep_start_display.grid(row=9, column=2, pady=10)

        sweep_end = tk.Label(sweep_frame, text='Ending voltage', font=("Arial", 10), bg="white")
        self.sweep_end_entry = tk.Entry(sweep_frame, width=5)
        self.sweep_end_display = tk.Label(sweep_frame, text="{} V".format(self.sweep_end_volt), font=("Arial", 12), bg="white")

        sweep_end.grid(row=10, column=0, pady=10)
        self.sweep_end_entry.grid(row=10, column=1, pady=10)
        self.sweep_end_display.grid(row=10, column=2, pady=10)

        sweep_step = tk.Label(sweep_frame, text='Voltage step', font=("Arial", 10), bg="white")
        self.sweep_step_entry = tk.Entry(sweep_frame, width=5)
        self.sweep_step_display = tk.Label(sweep_frame, text="{} V".format(self.sweep_step), font=("Arial", 12), bg="white")

        sweep_step.grid(row=11, column=0, pady=10)
        self.sweep_step_entry.grid(row=11, column=1, pady=10)
        self.sweep_step_display.grid(row=11, column=2, pady=10)

        sweep_pause = tk.Label(sweep_frame, text='Pause between steps', font=("Arial", 10), bg="white")
        self.sweep_pause_entry = tk.Entry(sweep_frame, width=5)
        self.sweep_pause_display = tk.Label(sweep_frame, text="{} s".format(self.sweep_pause), font=("Arial", 12), bg="white")

        sweep_pause.grid(row=12, column=0, pady=10)
        self.sweep_pause_entry.grid(row=12, column=1, pady=10)
        self.sweep_pause_display.grid(row=12, column=2, pady=10)

        sweep_channels = tk.Label(sweep_frame, text='Channel list to use', font=("Arial", 10), bg="white")
        self.sweep_channels_entry = tk.Entry(sweep_frame, width=10)
        self.sweep_channels_display = tk.Label(sweep_frame, text="{}".format(str(self.sweep_channels_list)), font=("Arial", 12), bg="white")

        sweep_channels.grid(row=13, column=0, pady=10, padx=5)
        self.sweep_channels_entry.grid(row=13, column=1, pady=10)
        self.sweep_channels_display.grid(row=13, column=2, pady=10)

        sweep_zero = tk.Label(sweep_frame, text='Zero between steps?', font=("Arial", 10), bg="white")
        self.sweep_zero_entry = tk.Entry(sweep_frame, width=5)
        self.sweep_zero_display = tk.Label(sweep_frame, text="{}".format(self.sweep_zero), font=("Arial", 12), bg="white")

        sweep_zero.grid(row=14, column=0, pady=10)
        self.sweep_zero_entry.grid(row=14, column=1, pady=10)
        self.sweep_zero_display.grid(row=14, column=2, pady=10)

        self.sweep_start_button = tk.Button(sweep_frame, text="Sweep off", command=self.sweep, bg="red")
        self.sweep_start_button.grid(row=8, column=1, pady=10)

        # update_sweep_parameters_button = ttk.Button(self, text="Update Sweep Parameters", command=self.update_sweep_parameters, style=("TButton", "white.TButton"))
        # update_sweep_parameters_button.grid(row=16, column=1, pady=10)

    # def update_sweep_parameters(self):
    #     pass
    
    def update_channel_parameters(self):
        for i in range(0, 4):
            new_voltage = self.voltage_entries[i].get()
            if new_voltage != self.voltage_displays[i]["text"] and self.is_voltage_valid(new_voltage):
                self.voltage_displays[i].config(text="{} V".format(new_voltage))
                self.channel_voltages[i] = float(new_voltage)
                self.hmp.set_voltage(i+1, new_voltage)
                print('Successfully set voltage for channel ' + str(i+1) + ' to ' + str(new_voltage) + ' V.')

            new_current = self.current_entries[i].get()
            if new_current != self.current_displays[i]["text"] and self.is_current_limit_valid(new_current):
                self.current_displays[i].config(text="{} A".format(new_current))
                self.channel_currents[i] = float(new_current)
                self.hmp.set_current_limit(i+1, new_current)
                print('Successfully set current for channel ' + str(i+1) + ' to ' + str(new_current) + ' A.')

    def sweep(self):
        if self.sweep_start_button["text"] == 'Sweep off':
            start_volt = self.sweep_start_entry.get()
            if (self.is_voltage_valid(start_volt)):
                self.sweep_start_display.config(text="{} V".format(start_volt))
                self.sweep_start_volt = start_volt 
            else:
                print('You have entered an invalid voltage for the sweep start.')
                raise InvalidStart()

            end_volt = self.sweep_end_entry.get()
            if (self.is_voltage_valid(end_volt)):
                self.sweep_end_display.config(text="{} V".format(end_volt))
                self.sweep_end_volt = end_volt 
            else:
                print('You have entered an invalid voltage for the sweep end.')
                raise InvalidEnd()

            step = self.sweep_step_entry.get()
            if (self.is_voltage_valid(step)):
                self.sweep_step_display.config(text="{} V".format(step))
                self.sweep_step = step 
            else:
                print('You have entered an invalid voltage for the sweep step.')
                raise InvalidStep()

            pause = self.sweep_pause_entry.get()
            try:
                float(pause)
                self.sweep_pause_display.config(text="{} s".format(pause))
                self.sweep_pause = pause
            except:
                print('You have entered an invalid duration for the sweep pause.')
                raise InvalidPause()

            new_channels = []
            channels_entry = self.sweep_channels_entry.get().split(',')
            if len(channels_entry) != 0:
                for channel in channels_entry:
                    try:
                        if self.is_valid_channel(channel):
                            new_channels.append(int(channel))
                    except:
                        print('You have entered an invalid channel name: {}'.format(channel))
                        raise InvalidChannel()
                self.sweep_channels_display.config(text="{}".format(str(new_channels)))
                self.sweep_channels_list = new_channels
            else:
                print('You have entered an empty channels list.')
                raise InvalidChannel()
            
            zero = self.sweep_zero_entry.get()
            if zero == 'yes' or zero == 'no':
                self.sweep_zero_display.config(text="{}".format(zero))
                self.sweep_zero = zero
            else:
                print('You have entered an invalid zero; please enter either yes or no.')
                raise InvalidZero()

            print('Congrats, sweep parameters updated and sweep started!')
            self.sweep_start_button.configure(text='Sweeping...', bg='green')
            self.measurement.sweep_and_save(start_volt, end_volt, step, pause, new_channels, zero)
            self.sweep_start_button.configure(text='Sweep off', bg='red')
            print('Sweep successfully completed!')
        else:
            self.sweep_start_button.configure(text='Sweep off', bg='red')
    
    def toggle_on_off(self):
        if self.on_off_button["text"] == "OFF":
            self.on_off_button.configure(text="ON", bg="green")
            self.hmp.enable_output()
        else:
            self.on_off_button.configure(text="OFF", bg="red")
            self.hmp.disable_output()

    def is_voltage_valid(self, voltage):
        try:
            voltage = float(voltage)
            if 0 <= voltage <= 128:
                return True
            else:
                return False
        except:
            print("Error: The entered voltage is invalid.")
            return False
        
    def is_current_limit_valid(self, current):
        try:
            current = float(current)
            return True
        except:
            print("Error: The entered current is invalid.")
            return False
    
    def is_valid_channel(self, channel):
        if channel == '1' or channel == '2' or channel == '3' or channel == '4':
            return True
        else:
            raise

# Example usage
# root = tk.Tk()
# voltage_source_frame = hmpControlFrame(root, 'ENTER ADDRESS HERE')
# voltage_source_frame.pack()
#root.mainloop()
