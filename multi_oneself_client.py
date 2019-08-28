#!/usr/bin/env python

import time
import os
import sys
import signal
from multiprocessing import Process, Pipe

sys.path.append(os.getcwd())

from helpers import (DONE, RUN, STOP)


def il(pipe, subdir, with_frame, is_multi, port):
    from il.sender import main as il_sender_main
    il_sender_main(pipe, subdir, with_frame, is_multi, port)


# add port
def indigo(pipe, subdir, with_frame, is_multi, port):
    from indigo.dagger.run_sender import main as indigo_sender_main
    indigo_sender_main(pipe, subdir, with_frame, is_multi, port)


def rl(pipe, subdir, with_frame, is_multi, port):
    from rl.sender import main as rl_sender_main
    rl_sender_main(pipe, subdir, with_frame, is_multi, port)


def gcc(pipe, subdir, with_frame, is_multi, port):
    from gcc.sender import main as gcc_sender_main
    gcc_sender_main(pipe, subdir, with_frame, is_multi, port)


def remyCC(pipe, subdir, with_frame, is_multi, port):
    from remy.sender import main as remyCC_sender_main
    remyCC_sender_main(pipe, subdir, with_frame, is_multi, port)


def pcc_rl(pipe, subdir, with_frame, is_multi, port):
    from Aurora.sender import main as pcc_rl_sender_main
    pcc_rl_sender_main(pipe, subdir, with_frame, is_multi, port)


def bbr(pipe, subdir, with_frame, is_multi):
    from bbr.sender import main as bbr_sender_main
    bbr_sender_main(pipe, subdir, with_frame, is_multi)


def pcc_vivace(pipe, subdir, with_frame, is_multi):
    from pcc_vivace.sender import main as pcc_vivace_sender_main
    pcc_vivace_sender_main(pipe, subdir, with_frame, is_multi)


def main():
    # seconds
    running_time = 100

    subdir = sys.argv[1]
    algorithm1 = sys.argv[2]
    algorithm2 = sys.argv[3]

    portI = int(sys.argv[4])
    portII = int(sys.argv[5])

    dir = './log/' + subdir
    if not os.path.exists(dir):
        os.mkdir(dir)

    with_frame = False
    is_multi = True

    # the parent process pipe
    parent_pipes = []
    process_sets = []

    # algorithm 1
    if algorithm1 == 'indigo':
        parent_1, pipe_1 = Pipe(True)
        p = Process(target=indigo, name='indigo_sender_1', args=(pipe_1, subdir, with_frame, is_multi, portI))
        parent_pipes.append(parent_1)
        process_sets.append(p)

    if algorithm1 == 'gcc':
        parent_1, pipe_1 = Pipe(True)
        p = Process(target=gcc, name='gcc_sender_1', args=(pipe_1, subdir, with_frame, is_multi, portI))
        parent_pipes.append(parent_1)
        process_sets.append(p)

    if algorithm1 == 'remyCC':
        parent_1, pipe_1 = Pipe(True)
        p = Process(target=remyCC, name='remyCC_sender_1', args=(pipe_1, subdir, with_frame, is_multi, portI))
        parent_pipes.append(parent_1)
        process_sets.append(p)

    if algorithm1 == 'pcc_rl':
        parent_1, pipe_1 = Pipe(True)
        p = Process(target=pcc_rl, name='pcc_rl_sender_1', args=(pipe_1, subdir, with_frame, is_multi, portI))
        parent_pipes.append(parent_1)
        process_sets.append(p)

    if algorithm1 == 'il':
        parent_1, pipe_1 = Pipe(True)
        p = Process(target=il, name='il_sender_1', args=(pipe_1, subdir, with_frame, is_multi, portI))
        parent_pipes.append(parent_1)
        process_sets.append(p)

    if algorithm1 == 'rl':
        parent_1, pipe_1 = Pipe(True)
        p = Process(target=rl, name='rl_sender_1', args=(pipe_1, subdir, with_frame, is_multi, portI))
        parent_pipes.append(parent_1)
        process_sets.append(p)

    # algorithm 2
    if algorithm2 == 'indigo':
        parent_2, pipe_2 = Pipe(True)
        p = Process(target=indigo, name='indigo_sender_2', args=(pipe_2, subdir, with_frame, is_multi, portII))
        parent_pipes.append(parent_2)
        process_sets.append(p)

    if algorithm2 == 'gcc':
        parent_2, pipe_2 = Pipe(True)
        p = Process(target=gcc, name='gcc_sender_2', args=(pipe_2, subdir, with_frame, is_multi, portII))
        parent_pipes.append(parent_2)
        process_sets.append(p)

    if algorithm2 == 'remyCC':
        parent_2, pipe_2 = Pipe(True)
        p = Process(target=remyCC, name='remyCC_sender_2', args=(pipe_2, subdir, with_frame, is_multi, portII))
        parent_pipes.append(parent_2)
        process_sets.append(p)

    if algorithm2 == 'pcc_rl':
        parent_2, pipe_2 = Pipe(True)
        p = Process(target=pcc_rl, name='pcc_rl_sender_2', args=(pipe_2, subdir, with_frame, is_multi, portII))
        parent_pipes.append(parent_2)
        process_sets.append(p)

    if algorithm2 == 'il':
        parent_2, pipe_2 = Pipe(True)
        p = Process(target=il, name='il_sender_2', args=(pipe_2, subdir, with_frame, is_multi, portII))
        parent_pipes.append(parent_2)
        process_sets.append(p)

    if algorithm2 == 'rl':
        parent_2, pipe_2 = Pipe(True)
        p = Process(target=rl, name='rl_sender_2', args=(pipe_2, subdir, with_frame, is_multi, portII))
        parent_pipes.append(parent_2)
        process_sets.append(p)

    for p in process_sets:
        p.start()

    # do handshake
    # n processes mapping n flags
    flags = ["" for i in range(len(process_sets))]

    while True:
        try:
            cc = 0
            for i in range(len(flags)):
                if flags[i] == "":
                    flags[i] = parent_pipes[i].recv()
                if flags[i] == DONE:
                    cc += 1

            # all handshake done
            if cc == len(flags):
                for pp in parent_pipes:
                    pp.send(RUN)
                break

        except BaseException as e:
            print "multi exception\n"
            sys.stderr.write(str(e.args))
            sys.stderr.flush()

    # start to run
    print("Process Beginning!")
    time.sleep(running_time)
    print("Process Ended!")

    # send stop signal
    for pp in parent_pipes:
        pp.send(STOP)

    # kill the process
    for pp in process_sets:
        try:
            # os.killpg(pp.pid, signal.SIGTERM)
            os.kill(pp.pid, signal.SIGTERM)
        except BaseException as e:
            print e.args


if __name__ == '__main__':
    main()
