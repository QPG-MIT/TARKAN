import os, sys, socket, json, urllib, logging, time, traceback, ctypes, select
import errno # To catch specific socket errors
import subprocess
from subprocess import Popen, PIPE
from threading import Thread
from Queue import Queue
from get_mapped_drives import get_drives
from WinSpecClass import WinSpec

if not getattr(__builtins__, "WindowsError", None):
    class WindowsError(OSError): pass

# client computer must be tracked on diamondbase. Authenticated via IP
# Will use plink via GIT_SSH env variable for communication to SERVER
# Note: will likely require a connection attempt manually to save server's key

# \n signfies EOM.  Communication is urlencoded (plus) and jsonencoded
#
# Creates daemon.pid with pid as only content
# Logs to stdout only
# See HELP for calling instructions

BASE_DIR = unicode(os.path.dirname(os.path.abspath(__file__)))

####################################################
############### Priviledge Elevation ###############
####################################################
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
 
if not is_admin():
    # Re-run the program with admin rights
    thisfile = unicode(os.path.abspath(__file__))
    outcome = ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), thisfile, None, 1)
    exit()
####################################################
####################################################
####################################################

# Server stuff
DEFAULT_IP = '0.0.0.0'
DEFAULT_PORT = 36577
PID_FILE = os.path.join(BASE_DIR,'daemon.pid')

HELP = '''Call with json object that is a python dictionary, or matlab struct (caps need to be replaced):
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

# Auth Server
SERVER = "diamondbase.mit.edu"
USER = "dbssh"
PORT = 22
PROXY = "proxy.py"

# Setup logging
logFile = os.path.join(BASE_DIR,'server.log')
log_formatter = logging.Formatter('[%(asctime)s] %(levelname)-7.7s %(message)s')
# Log to stream
str_handler = logging.StreamHandler(sys.stdout)
str_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
#if not logger.hasHandlers():    
logger.addHandler(str_handler)
        
VALID_CLIENTS = []  # Get from diamondbase

# Set to have higher priority
try:
    import win32api, win32process, win32con
    pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS,True,pid)
    win32process.SetPriorityClass(handle, win32process.ABOVE_NORMAL_PRIORITY_CLASS)
except:
    logger.warning('Could not elevate process priority.')

class AcquisitionAborted(Exception):
    pass

def checkWinSpec():
    pname = 'Winspec.exe'
    tlcall = ['TASKLIST', '/FI', 'imagename eq %s'%pname]
    tlout = subprocess.check_output(tlcall,shell=False).strip().split('\r\n')
    if len(tlout) > 1 and pname in tlout[-1]:
        return True
    return False

def callScript(script,*args):
    args = [str(a) for a in args] # Convert all to strings
    out = subprocess.check_output(['cscript',script+'.VBS']+args,stderr=subprocess.STDOUT,shell=False)
    return out

def enqueue_output(queue,ps_queue):
    logger.debug('enqueue_output started')
    ps = ps_queue.get() # Get subprocess or kill command (blocking)
    logger.debug('Received: %s'%ps)
    [stdout,stderr] = ps.communicate() # Blocks this thread
    logger.debug('stdout: %s'%stdout)
    logger.debug('stderr: %s'%stderr)
    queue.put(stdout)
    queue.put(stderr)

def acquire(connection,over_exposed_override=False):
    ACQUIRE_Q = Queue()
    DATA_Q = Queue()
    ACQ_THREAD = Thread(target=enqueue_output,args=(ACQUIRE_Q,DATA_Q))
    ACQ_THREAD.start()
    acq = subprocess.Popen(['cscript','acquire_blocking'+'.VBS'],stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    DATA_Q.put(acq)
    aborted = False
    try:
        while acq.poll() is None:
            [r,w,x] = select.select([connection],[],[],0)  # Non blocking check if data on connection
            if r:
                try:
                    cmd = urllib.unquote_plus(recv(r[0]))
                except AssertionError: # Client disconnecting
                    callScript('abort')
                    raise AcquisitionAborted()
                logger.info('During acquire, client issued: %s'%cmd)
                if cmd['function'] == 'abort':
                    callScript('abort')
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

def setup():
    out = subprocess.check_output(['cscript','setup.VBS'],stderr=subprocess.STDOUT,shell=False)
    out = out.strip().split(os.linesep)[-1] # Grab last line
    logger.debug('setup returned: %s'%out)
    out = json.loads(out)
    return out
    
def refresh_clients():
    msg = "python proxy.py custom_query 'out=json.dumps(list(Computer.objects.all().values(\"ip\")))'"
    ssh = Popen([r'%GIT_SSH%','-P',str(PORT),'%s@%s'%(USER,SERVER),msg],stdout=PIPE,stderr=PIPE,shell=True)
    try:
        out = ssh.communicate()
    except:
        raise Exception('IP not validated; Failed to update client list from diamondbase.')
    print(out)
    ips = [str(a['ip']) for a in json.loads(out[0].strip())]
    print(ips)
    return ips

def authenticate(address):
    global VALID_CLIENTS
    ip,port = address
    if ip in VALID_CLIENTS:
        return True
    else: # Refresh list once and try again
        VALID_CLIENTS = refresh_clients()
        if ip in VALID_CLIENTS:
            return True
    return True#False

def recv(connection,delim='\n',recv_buffer=4096):
    buffer = ''
    while True:
        data = connection.recv(recv_buffer)
        print('this is data', data)
        assert data, 'Client disconnected while receiving.'
        buffer += data
        if data[-1] == '\n':
            return buffer[0:-len(delim)]  # Remove delim

def main():
    logger.info('Starting acq thread')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    server_address=(DEFAULT_IP,DEFAULT_PORT)
    sock.bind(server_address)
    logger.info('listening on %s port %s'%server_address)
    sock.listen(5)
    already_connected = False
    try:
        while True:
            logger.info('waiting for connection...')
            if not already_connected:
                while True:
                    print('waiting for new connection')
                    try:
                        connection, client_address = sock.accept()
                        print('we have a new client yey')
                        logger.info('New Client: %s'%(client_address[0]))
                        connection.setblocking(1)
                        already_connected = True
                        break
                    except KeyboardInterrupt:
                        raise
                    except socket.timeout:
                        pass
            tstart = time.time()
            output = {'response': ''}
            try:
                print('trying to receive from client')
                #if authenticate(client_address):
                logger.debug('Took %0.2f to auth'%(time.time()-tstart))
                logger.debug('Client authenticated')
                cmd = urllib.unquote_plus(recv(connection))
                logger.debug('Took %0.2f to recv'%(time.time()-tstart))
                logger.debug('%s: %s'%(client_address[0],cmd))
                if cmd.strip() == 'Simulate_Server_Failure;':
                    # Not a perfect simulation of fatal error but should do the trick
                    continue # Note, this will go straight to the finally block
                try:  # Dispatch block
                    output = WinSpec.dispatch(connection,cmd,client_address[0])
                    logger.debug('Took %0.2f to dispatch'%(time.time()-tstart))
                    if output is str:
                        output = output.replace('\r\n','\n').strip()
                    output = {'success':True,'response':output}
                except Exception as err:
                    print('we have encountered an error during dispatch')
                    output = {'success':False,'response':err.message}
                    logger.error(traceback.format_exc())
            #else: # Failed auth
                #output = {'success':False,'resp':'Authentication Failed.'}
                logger.debug('    Sent: '+json.dumps(output))
                connection.sendall(urllib.quote_plus(json.dumps(output))+'\n')
            except socket.error as err:
                # Client may have gotten diconnected
                if err.errno == errno.ECONNRESET:
                    logger.debug('    Client Disconnected')
                    already_connected = False   
                else:
                    raise
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                logger.error(traceback.format_exc())
            finally:
                #print('we are in the finally block')
                #print('and this is the output so far:', output)
                if (output['response'] != 'ack'):
                    print('connection closed')
                    already_connected = False
                    connection.close()
            logger.debug('Took %0.2f s'%(time.time()-tstart))
    except SystemExit:
        raise
    except KeyboardInterrupt:
        logger.info('Aborted')
    except:
        logger.error(traceback.format_exc())
    finally:
        sock.close()
        logger.info('server shutting down')


if __name__=="__main__":
    os.system("title "+"WinSpec Server")
    if checkWinSpec():
        print('Found WinSpec')
        logger.info('Found WinSpec')
    else:
        logger.info('Starting WinSpec')
        subprocess.call(['start','', u'C:\Program Files\Princeton Instruments\WinSpec\Winspec.exe'],shell=True)
    VALID_CLIENTS = refresh_clients()
    main()
