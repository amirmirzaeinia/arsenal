#!/usr/bin/env python
import sys
import time
import os
import signal

sys.path.append('.')

from multiprocessing import Process


def il_server(subdir, is_multi, port):
    from il.receiver import main as il_server_main
    il_server_main(subdir, is_multi, port)


# add port
def indigo_server(subdir, is_multi, port):
    from indigo.env.run_receiver import main as indigo_server_main
    indigo_server_main(subdir, is_multi, port)


def rl_server(subdir, is_multi, port):
    from rl.receiver import main as rl_server_main
    rl_server_main(subdir, is_multi, port)


def gcc_server(subdir, is_multi, port):
    from gcc.receiver import main as gcc_server_main
    gcc_server_main(subdir, is_multi, port)


def remy_server(subdir, is_multi, port):
    from remy.receiver import main as remy_server_main
    remy_server_main(subdir, is_multi, port)


def pcc_rl_server(subdir, is_multi, port):
    from Aurora.receiver import main as pcc_rl_server_main
    pcc_rl_server_main(subdir, is_multi, port)


def bbr_server(subdir, is_multi):
    from bbr.receiver import main as bbr_server_main
    bbr_server_main(subdir, is_multi)


def pcc_vivace_server(subdir, is_multi):
    from pcc_vivace.receiver import main as pcc_vivace_server_main
    pcc_vivace_server_main(subdir, is_multi)


def main():
    running_time = 100 + 15
    subdir = sys.argv[1]
    algorithm1 = sys.argv[2]
    algorithm2 = sys.argv[3]

    portI = int(sys.argv[4])
    portII = int(sys.argv[5])

    print(portI)
    print(portII)

    dir = './log/' + subdir
    if not os.path.exists(dir):
        os.mkdir(dir)

    is_multi = True

    process_sets = []

    # algorithm 1
    if algorithm1 == 'indigo':
        process = Process(target=indigo_server, name='Indigo Server 1', args=(subdir, is_multi, portI))
        process_sets.append(process)

    if algorithm1 == 'gcc':
        process = Process(target=gcc_server, name='gcc Server 1', args=(subdir, is_multi, portI))
        process_sets.append(process)

    if algorithm1 == 'remyCC':
        process = Process(target=remy_server, name='remy Server 1', args=(subdir, is_multi, portI))
        process_sets.append(process)

    if algorithm1 == 'pcc_rl':
        process = Process(target=pcc_rl_server, name=' pcc_rl Server 1', args=(subdir, is_multi, portI))
        process_sets.append(process)

    if algorithm1 == 'il':
        process = Process(target=il_server, name='il Server 1', args=(subdir, is_multi, portI))
        process_sets.append(process)

    if algorithm1 == 'rl':
        process = Process(target=rl_server, name='rl Server 1', args=(subdir, is_multi, portI))
        process_sets.append(process)

    # algorithm 2
    if algorithm2 == 'indigo':
        process = Process(target=indigo_server, name='Indigo Server 2', args=(subdir, is_multi, portII))
        process_sets.append(process)

    if algorithm1 == 'gcc':
        process = Process(target=gcc_server, name='gcc Server 2', args=(subdir, is_multi, portII))
        process_sets.append(process)

    if algorithm1 == 'remyCC':
        process = Process(target=remy_server, name='remy Server 2', args=(subdir, is_multi, portII))
        process_sets.append(process)

    if algorithm1 == 'pcc_rl':
        process = Process(target=pcc_rl_server, name='pcc_rl Server 2', args=(subdir, is_multi, portII))
        process_sets.append(process)

    if algorithm1 == 'il':
        process = Process(target=il_server, name='il Server 2', args=(subdir, is_multi, portII))
        process_sets.append(process)

    if algorithm1 == 'rl':
        process = Process(target=rl_server, name='rl Server 2', args=(subdir, is_multi, portII))
        process_sets.append(process)

    # print process_sets
    for p in process_sets:
        p.start()

    time.sleep(running_time)

    for p in process_sets:
        try:
            os.kill(p.pid, signal.SIGTERM)
        except Exception:
            pass


if __name__ == '__main__':
    main()
