#!/usr/bin/env python

import time
import os
import sys
import signal
from multiprocessing import Process, Pipe

sys.path.append(os.getcwd())

from helpers import (DONE, RUN, STOP)


def il(pipe, subdir, with_frame, is_multi):
    from il.sender import main as il_sender_main
    il_sender_main(pipe, subdir, with_frame, is_multi)


def indigo(pipe, subdir, with_frame, is_multi):
    from indigo.dagger.run_sender import main as indigo_sender_main
    indigo_sender_main(pipe, subdir, with_frame, is_multi)


def rl(pipe, subdir, with_frame, is_multi):
    from rl.sender import main as rl_sender_main
    rl_sender_main(pipe, subdir, with_frame, is_multi)


def gcc(pipe, subdir, with_frame, is_multi):
    from gcc.sender import main as gcc_sender_main
    gcc_sender_main(pipe, subdir, with_frame, is_multi)


def remyCC(pipe, subdir, with_frame, is_multi):
    from remy.sender import main as remyCC_sender_main
    remyCC_sender_main(pipe, subdir, with_frame, is_multi)


def pcc_rl(pipe, subdir, with_frame, is_multi):
    from Aurora.sender import main as pcc_rl_sender_main
    pcc_rl_sender_main(pipe, subdir, with_frame, is_multi)


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

    dir = './log/' + subdir
    if not os.path.exists(dir):
        os.mkdir(dir)

    with_frame = False
    is_multi = True

    # create pipe to synchronize
    parent_il, il_pipe = Pipe(True)
    parent_indigo, indigo_pipe = Pipe(True)
    parent_rl, rl_pipe = Pipe(True)
    parent_gcc, gcc_pipe = Pipe(True)
    parent_remyCC, remyCC_pipe = Pipe(True)
    parent_pcc_rl, pcc_rl_pipe = Pipe(True)
    parent_bbr, bbr_pipe = Pipe(True)
    parent_pcc_vivace, pcc_vivace_pipe = Pipe(True)

    # the parent process pipe
    parent_pipes = []
    # parent_pipes.append(parent_il)
    # parent_pipes.append(parent_indigo)
    # parent_pipes.append(parent_rl)
    # parent_pipes.append(parent_gcc)
    # parent_pipes.append(parent_remyCC)
    # parent_pipes.append(parent_pcc_rl)
    # parent_pipes.append(parent_bbr)
    # parent_pipes.append(parent_pcc_vivace)

    process_sets = []

    p1 = Process(target=il, name='il_sender', args=(il_pipe, subdir, with_frame, is_multi))
    p3 = Process(target=indigo, name='indigo_sender', args=(indigo_pipe, subdir, with_frame, is_multi))
    p5 = Process(target=rl, name='rl_sender', args=(rl_pipe, subdir, with_frame, is_multi))
    p7 = Process(target=gcc, name='gcc_sender', args=(gcc_pipe, subdir, with_frame, is_multi))
    p9 = Process(target=remyCC, name='remyCC_sender', args=(remyCC_pipe, subdir, with_frame, is_multi))
    p11 = Process(target=pcc_rl, name='pcc_rl_sender', args=(pcc_rl_pipe, subdir, with_frame, is_multi))
    p13 = Process(target=bbr, name='brr_sender', args=(bbr_pipe, subdir, with_frame, is_multi))
    p15 = Process(target=pcc_vivace, name='pcc_vivace_sender', args=(pcc_vivace_pipe, subdir, with_frame, is_multi))

    # process_sets.append(p1)
    # process_sets.append(p3)
    # process_sets.append(p5)
    # process_sets.append(p7)
    # process_sets.append(p9)
    # process_sets.append(p11)
    # process_sets.append(p13)
    # process_sets.append(p15)

    # algorithm 1
    if algorithm1 == 'il':
        parent_pipes.append(parent_il)
        process_sets.append(p1)

    if algorithm1 == 'indigo':
        parent_pipes.append(parent_indigo)
        process_sets.append(p3)

    if algorithm1 == 'rl':
        parent_pipes.append(parent_rl)
        process_sets.append(p5)

    if algorithm1 == 'gcc':
        parent_pipes.append(parent_gcc)
        process_sets.append(p7)

    if algorithm1 == 'remyCC':
        parent_pipes.append(parent_remyCC)
        process_sets.append(p9)

    if algorithm1 == 'pcc_rl':
        parent_pipes.append(parent_pcc_rl)
        process_sets.append(p11)

    if algorithm1 == 'bbr':
        parent_pipes.append(parent_bbr)
        process_sets.append(p13)

    if algorithm1 == 'pcc_vivace':
        parent_pipes.append(parent_pcc_vivace)
        process_sets.append(p15)

    # algorithm 2
    if algorithm2 == 'il':
        parent_pipes.append(parent_il)
        process_sets.append(p1)

    if algorithm2 == 'indigo':
        parent_pipes.append(parent_indigo)
        process_sets.append(p3)

    if algorithm2 == 'rl':
        parent_pipes.append(parent_rl)
        process_sets.append(p5)

    if algorithm2 == 'gcc':
        parent_pipes.append(parent_gcc)
        process_sets.append(p7)

    if algorithm2 == 'remyCC':
        parent_pipes.append(parent_remyCC)
        process_sets.append(p9)

    if algorithm2 == 'pcc_rl':
        parent_pipes.append(parent_pcc_rl)
        process_sets.append(p11)

    if algorithm2 == 'bbr':
        parent_pipes.append(parent_bbr)
        process_sets.append(p13)

    if algorithm2 == 'pcc_vivace':
        parent_pipes.append(parent_pcc_vivace)
        process_sets.append(p15)

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
