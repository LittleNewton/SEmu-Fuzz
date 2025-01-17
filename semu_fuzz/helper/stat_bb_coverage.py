'''
Description: stat bb coverage from afl output.
Usage: semu-fuzz-helper stat <base_configs.yml> [-t <time>]
'''

import argparse
import os
import subprocess
from time import perf_counter, sleep
from .stat_draw_bb_img import draw

DEBUG = True # Recommend setting True to get most info in stat.

def _find_file(folder_path):
    # find all the files in folder_path
    return [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]

def _get_file_sorted(folder_path):
    # get create time
    files = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            create_time = os.path.getctime(file_path)
            files.append((file_name, create_time))
    # sort
    return [os.path.join(folder_path, file_name) for file_name,_ in sorted(files, key=lambda x: x[1])]

def stat(base_configs, duration):
    # dump all the file
    for firmware_elfpath, base_config in base_configs.items():
        try:
            firmware_dir = os.path.dirname(firmware_elfpath)
            firmware_elfname = os.path.basename(firmware_elfpath)
            stat_path = os.path.join(firmware_dir, 'stat_output')
            possible_fuzz_queue_dir = [
                os.path.join(firmware_dir, "output/queue"), # AFL
                os.path.join(firmware_dir, "output/default/queue")  # AFLplusplus
            ]
            fuzz_queue_dir = possible_fuzz_queue_dir[0]
            config_path = os.path.join(firmware_dir, 'semu_config.yml')

            # check all path to know whether fuzz or not
            for qd in possible_fuzz_queue_dir:
                if os.path.exists(qd):
                    fuzz_queue_dir = qd
                    break
            else:
                print("[+] No Fuzz output of %s" % firmware_elfpath)
                continue

            print('[*] Stat Block Coverage of %s...' % firmware_elfpath)

            # rm the old stat
            os.system("rm -r " + stat_path)

            # start stat
            commands = []
            # find all the file in fuzz_queue_dir
            for fuzz_input in _get_file_sorted(fuzz_queue_dir):
                command_line = "semu-fuzz %s %s -s " % (fuzz_input, config_path)
                commands.append(command_line)
            # execute commands in order
            for command in commands:
                if DEBUG:
                    print("[*] Start Command: %s" % command)
                proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # wait for proc stop
                start_time = perf_counter()
                while True:
                    if proc.poll() is not None:
                        break
                    # timeout: 10s
                    if perf_counter() - start_time > 10:
                        if DEBUG:
                            print("[-] Process timed out. Killing process...")
                            # exit(-1)
                        proc.kill()
                    sleep(0.1) # check proc status every 0.1s
            # draw picture with 'new_blocks.txt'
            draw(firmware_dir, duration * 3600)
        except Exception as e:
            print("[-] Failed! {}".format(e))