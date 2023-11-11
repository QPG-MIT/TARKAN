import numpy as np
import tkinter as tk

class Optimization():
    def __init__(self, laser, spect, stage):
        self.laser = laser
        self.spect = spect
        self.stage = stage

        self.center_wavelength = tk.StringVar(value='648.8')
        self.width = tk.StringVar(value='0.5')
        self.xrange = tk.StringVar(value='-75, 75')
        self.yrange = tk.StringVar(value='-75, 75')

        self.start_label = tk.StringVar(value=' ')
        self.start_x = tk.StringVar(value='0')
        self.start_y = tk.StringVar(value='0')
        self.num_devices_per_col = tk.StringVar(value=' ')
        self.x_increment = tk.StringVar(value='800')
        self.y_increment = tk.StringVar(value='210')
        self.rel_coord = tk.BooleanVar(value=False)

        self.manual_sequence = tk.StringVar(value='n/a')
        self.manual_rel_coord = tk.BooleanVar(value=False)


    def optimize_single_device(self):
        '''
        Function for optimizing the signal from a single device. Optimization starts somewhere in the center of the grating coupler.
            'center_wavelength' is the central wavelength around which we would like to maximize the signal,
            'width' is the width around the central wavelength to be used as boundaries for optimization,
            'x_range' and 'y_range' are the scan range tuples, given as relative distances from the center of the grating.
        Returns the optimal (x, y) coordinates, and moves the stage to these coordinates before returning so.
        '''
        initial_position = self.stage.get_position()
        center_wavelength = float(self.center_wavelength.get())
        width = float(self.width.get())
        x_range = self.xrange.get()
        y_range = self.yrange.get()
        
        print('Scanning the x axis...')
        optimal_x = self.__do_scan(x_range, 'x', center_wavelength, width)
        self.stage.set_position(optimal_x, initial_position[1])

        print('Scan on x axis completed. Optimal x coordinate is {}. Now scanning the y axis...'.format(optimal_x))
        optimal_y = self.__do_scan(y_range, 'y', center_wavelength, width)
        self.stage.set_position(optimal_x, optimal_y)

        print('Optimization completed, please proceed to sweeping.')
        print('The optimal location is: (', optimal_x, ' ', optimal_y, ')')
        return True

    def __do_scan(self, coord_range, direction, center_wavelength, width):
        min_coord, max_coord = self.__get_coords_and_set_init_pos(coord_range, direction)
        self.stage.update_step(self.stage.MIN_STEP_SIZE) # set the step size to be the smallest 

        optimal_coord = 0
        area = 0
        coord = min_coord
        while coord < max_coord:
            raw_data = self.spect.acquire_and_plot_data(self.spect.fig)
            #all_params = self.__get_all_params()
            #data_to_save =  all_params | {'data': data} # merge parameter and data dictionaries 
            new_area = self.__integrate_area(center_wavelength, width, raw_data)
            if new_area > area:
                area = new_area
                optimal_coord = coord
            if direction == 'x':
                self.stage.move_r()
            else:
                self.stage.move_t()
            coord += self.stage.MIN_STEP_SIZE
        return optimal_coord

    def __integrate_area(self, center_wavelength, width, raw_data):
        intensity_arr = raw_data['y'][0]
        min_wavelength, max_wavelength = float(raw_data['CAL_CALIBVAL'][0]), float(raw_data['CAL_CALIBVAL'][2])
        wavelength_np = np.linspace(min_wavelength, max_wavelength, len(intensity_arr))
        step = wavelength_np[1]-wavelength_np[0] # the distance in the x axis between two subsequent data points 

        area = 0
        for (index, wavelength) in enumerate(wavelength_np):
            if ((center_wavelength-width/2) <= wavelength <= (center_wavelength+width/2)):
                area += intensity_arr[index]*step
        return area
    
    def __get_coords_and_set_init_pos(self, coord_range, direction):
        separated = coord_range.split(',')
        min_rel_dist = int(separated[0])
        max_rel_dist = int(separated[1])
        position = self.stage.get_position()
        
        if direction == 'x':
            min_coord = position[0]+min_rel_dist
            max_coord = position[0]+max_rel_dist
            self.stage.set_position(min_coord, position[1])
        else:
            min_coord = position[1]+min_rel_dist
            max_coord = position[1]+max_rel_dist
            self.stage.set_position(position[0], min_coord)
        return min_coord, max_coord

    # def __get_all_params(self):
    #     laser_params = {'laser_wavelength': self.laser.getwavelength(), 'laser_bandwidth': self.laser.getbandwidth(),
    #                     'laser_power': self.laser.getpower()}
        
    #     spect_params_query = self.spect.get_parameters()
    #     spect_params = {'spect_grating': spect_params_query[0], 'spect_wavelength': spect_params_query[1], 
    #                     'spect_exposure': spect_params_query[2]}
        
    #     stage_params = {'stage_location': self.stage.get_position()}
        
    #     params = {'laser_params': laser_params, 'spect_params': spect_params, 'stage_params': stage_params}
    #     return params

