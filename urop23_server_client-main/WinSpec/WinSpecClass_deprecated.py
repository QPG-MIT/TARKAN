import json, subprocess, os, select, urllib, time
from queue import Queue
from threading import Thread

class AcquisitionAborted(Exception):
    pass

class WinSpec:
    def __init__(self, IP = '18.25.30.120', PORT = '36577'):
        self.DEFAULT_IP = IP
        self.DEFAULT_PORT = PORT
        self.HELP = '''Call with json object that is a python dictionary, or matlab struct (caps need to be replaced):
                        Functions without return values will return "OK" upon completion or an error.
                        {"function":"FUNCTION_NAME","args":[ARG1,ARG2,...]}
                        Possible Functions:
                        setup() # Sets up basic file handling procedure (e.g. overwrite, autosave, no background subtraction, TEMP_SPE)
                        acquire() # Begins acquisition
                        abort() # Aborts current acquisition (error if no current acquisition)
                        exposure(time) # Sets exposure time in seconds
                        grating(gratingN,wavelength) # Sets to specified grating (indexed from 1 as highest), then adjusts grating to desired wavelength (nm)
                        [N,pos,exp] = getGratingAndExposure() # Returns grating number, its position and exposure setting
                    '''

    def dispatch(self, connection, function, *args):
        if function == 'start': # start WinSpec.exe
            path = 'C:\Program Files\Princeton Instruments\WinSpec\Winspec.exe'
            run = subprocess.Popen([path])            
            return 'WinSpec.exe has started.'
        elif function == 'close': # close WinSpec.exe
            run = subprocess.Popen(['taskkill', '/IM', 'Winspec.exe', '/F'])
            return 'Winspec.exe is closed.'
        elif function == 'setup': # no inputs
            return self.setup()
        elif function == 'acquire':
            assert len(args) <= 1, 'exposure takes 1 optional input, %i given.'%len(args)
            return self.acquire(connection,*args)
        elif function == 'abort':
            raise Exception('No acquisition in progress')
        elif function == 'exposure':  
            assert len(args) == 1, 'exposure takes 1 input, %i given.'%len(args)
            val = float(args[0]) # Confirm indeed numeric
            self.callScript(function, 3, val)
            return 'OK'
        elif function == 'grating':
            assert len(args) == 2, 'grating takes 2 inputs, %i given.'%len(args)
            N = int(args[0])
            wavelength = float(args[1])
            self.callScript(function, N, wavelength)
            return 'OK'
        elif function == 'getgratingandexposure':
            outRaw = self.callScript(function)
            out = outRaw.split('\n')[3].strip().split(',')
            assert len(out)==3, 'VBS output parsing returned incorrect output:\n%s'%outRaw
            out = [int(out[0]), float(out[1]), float(out[2])]
            return out
        elif function == '_ping':
            out = (self.DEFAULT_IP, self.DEFAULT_PORT)
            return out
        elif function == 'help':
            return self.HELP
        else:
            raise Exception('Incorrect function: %s.\n\n'%function+self.HELP)
        
    def acquire(self, connection, over_exposed_override=False):
        ACQUIRE_Q = Queue()
        DATA_Q = Queue()
        ACQ_THREAD = Thread(target=self.enqueue_output,args=(ACQUIRE_Q,DATA_Q))
        ACQ_THREAD.start()
        acq = subprocess.Popen(['cscript','acquire_blocking'+'.VBS'],stderr=subprocess.PIPE,stdout=subprocess.PIPE)
        DATA_Q.put(acq)
        aborted = False
        try:
            while acq.poll() is None:
                [r,w,x] = select.select([connection],[],[],0)  # Non blocking check if data on connection
                if r:
                    try:
                        cmd = urllib.unquote_plus(self.recv(r[0]))
                    except AssertionError: # Client disconnecting
                        self.callScript('abort')
                        raise AcquisitionAborted()
                    if cmd['function'] == 'abort':
                        self.callScript('abort')
                        raise AcquisitionAborted()
                time.sleep(0.1)
            dat = ACQUIRE_Q.get(timeout=5) # Blocking wait
            err = ACQUIRE_Q.get(timeout=5)
            if err: raise Exception(err)
        except AcquisitionAborted:
            aborted = True
        finally:
            ACQ_THREAD.join()
        if aborted: return
        dat = dat.strip().split(os.linesep*2)[-1] # Strip off header
        out_dat = json.loads(dat)
        # Data should be uint16 (interpreted in VBS as signed)
        out_dat['y'] = [[i%2**16 for i in frame] for frame in out_dat['y']]
        if not over_exposed_override:
            if max([max(i) for i in out_dat['y']])==2**16-1:
                raise Exception('Over exposed')
        return out_dat

    def setup(self):
        out = subprocess.check_output(['cscript', 'setup.VBS'], stderr=subprocess.STDOUT, shell=False)
        out = out.strip().split(os.linesep)[-1] # Grab last line
        out = json.loads(out)
        return out
    
    def callScript(self, script, *args):
        args = [str(a) for a in args] # Convert all to strings
        out = subprocess.check_output(['cscript', script+'.VBS']+args, stderr=subprocess.STDOUT, shell=False)
        return out
    
    def enqueue_output(queue, ps_queue):
        ps = ps_queue.get() # Get subprocess or kill command (blocking)
        [stdout, stderr] = ps.communicate() # Blocks this thread
        queue.put(stdout)
        queue.put(stderr)

    def recv(connection,delim='\n',recv_buffer=4096):
        buffer = ''
        while True:
            data = connection.recv(recv_buffer)
            print('This is data: ', data)
            assert data, 'Client disconnected while receiving.'
            buffer += data
            if data[-1] == '\n':
                return buffer[0:-len(delim)]  # Remove delim