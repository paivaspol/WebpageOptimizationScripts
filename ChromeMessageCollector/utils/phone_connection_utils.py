import subprocess
import os

from time import sleep
from ConfigParser import ConfigParser

PCAP_DIRECTORY = '/sdcard/Research/output.pcap'
RESULT_DIRECTORY = '../result/'

DEVICE_ID = 'id'
IP = 'ip'
ADB_PORT = 'adb_port'
CHROME_MAC_DEBUG_PORT = 'chrome_mac_debugging_port'
DEVICE_TYPE = 'type'
CHROME_INSTANCE = 'chrome_instance'
WEB_SOCKET_DEBUGGER_URL = 'webSocketDebuggerUrl'
USE_CHROMIUM = 'use_chromium'

DEVICE_PHONE = 'phone'
DEVICE_MAC = 'mac'

ANDROID_CHROME_INSTANCE = 'com.android.chrome/com.google.android.apps.chrome.Main'
ANDROID_CHROMIUM_INSTANCE = 'org.chromium.chrome/com.google.android.apps.chrome.Main'
MAC_CHROME_INSTANCE = '"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"'

def start_chrome(device_configuration):
    '''
    Setup and run chrome on Android.
    '''
    if device_configuration[DEVICE_TYPE] == DEVICE_PHONE:
        print device_configuration.keys()
        # Setup port-forwarding for RDP
        cmd_base = 'adb -s {0} forward tcp:{1} localabstract:chrome_devtools_remote'
        cmd = cmd_base.format(device_configuration[DEVICE_ID], device_configuration[ADB_PORT])
        p = subprocess.Popen(cmd, shell=True)

        # Run chrome
        cmd_base = 'adb -s {0} shell "am start -a android.intent.action.VIEW -n {1}"'
        cmd = cmd_base.format(device_configuration[DEVICE_ID], device_configuration[CHROME_INSTANCE])
        p = subprocess.Popen(cmd, shell=True)

        sleep(3) # So we have enough time to forward the port.

        return p
    elif device_configuration[DEVICE_TYPE] == DEVICE_MAC:
        print 'device config: ' + str(device_configuration)
        # Run Chrome.
        cmd = device_configuration[CHROME_INSTANCE] + ' --incognito --disable-extensions --remote-debugging-port={0} --disable-logging > /dev/null 2>&1 &'.format(device_configuration[CHROME_MAC_DEBUG_PORT])
        p = subprocess.call(cmd, shell=True)
        return p
        

def stop_chrome(device_configuration):
    '''
    Kill the chrome process that is running.
    '''
    if device_configuration[DEVICE_TYPE] == DEVICE_PHONE:
        cmd_base = 'adb -s {0} shell am force-stop com.android.chrome'
        cmd = cmd_base.format(device_configuration[DEVICE_ID])
        os.system(cmd)
    elif device_configuration[DEVICE_TYPE] == DEVICE_MAC:
        os.system('pkill -9 Chrome')

def start_tcpdump(device_configuration):
    '''
    Starts tcpdump on the phone.
    '''
    tcpdump_started = False
    while not tcpdump_started:
        cmd_base = 'adb -s {0} shell \'su -c \'/tcpdump -i wlan0 -n -s 0 -w {1}\'\''
        cmd = cmd_base.format(device_configuration[DEVICE_ID], PCAP_DIRECTORY)
        retval = subprocess.Popen(cmd, shell=True)
        get_tcp_dump_process = 'adb -s {0} shell \'su -c \'ps | grep tcpdump\'\''.format(device_configuration[DEVICE_ID])
        result = subprocess.check_call(get_tcp_dump_process, shell=True)
        print result
        tcpdump_started = True
    return retval

def stop_tcpdump(device_configuration, sleep_before_kill=True):
    '''
    Stops tcpdump on the phone.
    '''
    if sleep_before_kill:
        print 'Sleeping before killing tcpdump.'
        sleep(45) # Give sometime for tcpdump to be finished.
    cmd_base = 'adb -s {0} shell ps | grep tcpdump | awk \'{{ print $2 }}\' | xargs adb -s {0} shell "su -c kill -9"'
    cmd = cmd_base.format(device_configuration[DEVICE_ID])
    print cmd
    return subprocess.Popen(cmd, shell=True)

def fetch_pcap(device_configuration, pcap_directory=PCAP_DIRECTORY, destination_directory=RESULT_DIRECTORY):
    '''
    Fetches the pcap file from the phone.
    '''
    fetch_file(device_configuration, pcap_directory, destination_directory, remove_file=True)

def fetch_cpu_measurement_file(device_configuration, measurement_dir, destination_directory):
    print 'Fetching CPU Measurement file...'
    fetch_file(device_configuration, measurement_dir, destination_directory, remove_file=True)

def fetch_file(device_configuration, file_location_on_phone, destination_directory, remove_file=False):
    print 'destination directory: ' + destination_directory
    cmd_base = 'adb -s {0} pull {1} {2}'
    cmd = cmd_base.format(device_configuration[DEVICE_ID], file_location_on_phone, destination_directory)
    os.system(cmd)
    if remove_file:
        cmd_base = 'adb -s {0} shell rm {1}'
        cmd = cmd_base.format(device_configuration[DEVICE_ID], file_location_on_phone)
        os.system(cmd)

def kill_cpu_measurement(device_configuration):
    command = 'adb -s {0} shell am force-stop edu.michigan.pageloadcpumeasurement'
    cmd = command.format(device_configuration[DEVICE_ID])
    subprocess.Popen(cmd, shell=True)

def start_cpu_measurement(device_configuration):
    command = 'adb -s {0} shell am start -n edu.michigan.pageloadcpumeasurement/.MainActivity'
    cmd = command.format(device_configuration[DEVICE_ID])
    subprocess.Popen(cmd, shell=True)

def bring_cpu_measurement_to_foreground(device_configuration):
    command = 'adb -s {0} shell am broadcast -a "android.intent.action.PROCESS_TEXT"'
    cmd = command.format(device_configuration[DEVICE_ID])
    subprocess.Popen(cmd, shell=True).wait()

def get_device_configuration(config_reader, device):
    '''
    Constructs a device configuration map.
    '''
    device_config = dict()
    device_config[IP] = config_reader.get(device, IP)
    device_type = config_reader.get(device, DEVICE_TYPE)
    device_config[DEVICE_TYPE] = device_type
    if device_type == DEVICE_PHONE:
        device_config[ADB_PORT] = int(config_reader.get(device, ADB_PORT))
        device_config[CHROME_INSTANCE] = ANDROID_CHROME_INSTANCE if not bool(config_reader.get(device, USE_CHROMIUM)) else ANDROID_CHROMIUM_INSTANCE
        device_config[DEVICE_ID] = config_reader.get(device, DEVICE_ID)
    elif device_type == DEVICE_MAC:
        device_config[CHROME_MAC_DEBUG_PORT] = int(config_reader.get(device, CHROME_MAC_DEBUG_PORT))
        device_config[CHROME_INSTANCE] = MAC_CHROME_INSTANCE
    return device_config

def get_cpu_running_chrome(device_config):
    command = 'adb -s {0} shell \'ps -c | grep chrome\''.format(device_config[DEVICE_ID])
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, _ = process.communicate()
    return output.split()[5]

def wake_phone_up(device_config):
    command = 'adb shell input keyevent KEYCODE_WAKEUP'
    subprocess.call(command, shell=True)
    print 'Waking up the phone'
