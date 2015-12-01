import subprocess
import os

from time import sleep
from ConfigParser import ConfigParser

PCAP_DIRECTORY = '/sdcard/Research/output.pcap'
RESULT_DIRECTORY = '../result/'

DEVICE_ID = 'id'
IP = 'ip'
ADB_PORT = 'adb_port'
CHROME_INSTANCE = 'com.android.chrome'
WEB_SOCKET_DEBUGGER_URL = 'webSocketDebuggerUrl'

def start_chrome(device_configuration):
    '''
    Setup and run chrome on Android.
    '''
    # Run chrome
    cmd_base = 'adb -s {0} shell "am start -a android.intent.action.VIEW -n {1}"'
    cmd = cmd_base.format(device_configuration[DEVICE_ID], device_configuration[CHROME_INSTANCE])
    p = subprocess.Popen(cmd, shell=True)

    sleep(15) # So we have enough time to forward the port.

    # Setup port-forwarding for RDP
    cmd_base = 'adb -s {0} forward tcp:{1} localabstract:chrome_devtools_remote'
    cmd = cmd_base.format(device_configuration[DEVICE_ID], device_configuration[ADB_PORT])
    p = subprocess.Popen(cmd, shell=True)

    return p

def stop_chrome(device_configuration):
    '''
    Kill the chrome process that is running.
    '''
    cmd_base = 'adb -s {0} shell am force-stop com.android.chrome'
    cmd = cmd_base.format(device_configuration[DEVICE_ID])
    os.system(cmd)

def start_tcpdump(device_configuration, snaplen=0):
    '''
    Starts tcpdump on the phone.
    '''
    cmd_base = 'adb -s {0} shell \'su -c "/tcpdump -i wlan0 -n -s {1} -w {2}"\''
    cmd = cmd_base.format(device_configuration[DEVICE_ID], snaplen, PCAP_DIRECTORY)
    return subprocess.Popen(cmd, shell=True)

def stop_tcpdump(device_configuration, sleep_before_kill=True):
    '''
    Stops tcpdump on the phone.
    '''
    if sleep_before_kill:
        print 'Sleeping before killing tcpdump.'
        sleep(10) # Give sometime for tcpdump to be finished.
    cmd_base = 'adb -s {0} shell ps | grep tcpdump | awk \'{{ print $2 }}\' | xargs adb -s {0} shell "su -c kill -9"'
    cmd = cmd_base.format(device_configuration[DEVICE_ID])
    print cmd
    return subprocess.Popen(cmd, shell=True)

def fetch_pcap(device_configuration, pcap_directory=PCAP_DIRECTORY, destination_directory=RESULT_DIRECTORY):
    '''
    Fetches the pcap file from the phone.
    '''
    cmd_base = 'adb -s {0} pull {1} {2}'
    cmd = cmd_base.format(device_configuration[DEVICE_ID], pcap_directory, destination_directory)
    os.system(cmd)
    cmd_base = 'adb -s {0} shell rm {1}'
    cmd = cmd_base.format(device_configuration[DEVICE_ID], pcap_directory)
    os.system(cmd)

def get_device_configuration(config_reader, device):
    '''
    Constructs a device configuration map.
    '''
    device_config = dict()
    device_config[DEVICE_ID] = config_reader.get(device, DEVICE_ID)
    device_config[IP] = config_reader.get(device, IP)
    device_config[CHROME_INSTANCE] = 'com.android.chrome/com.google.android.apps.chrome.Main'
    device_config[ADB_PORT] = int(config_reader.get(device, ADB_PORT))
    print 'device_config: ' + str(device_config)
    return device_config
