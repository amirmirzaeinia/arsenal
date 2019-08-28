import numpy as np
import os
import csv


class Extract(object):
    def __init__(self):
        self.seq = []
        self.frame_id = []
        self.send_ts = []
        self.frame_start = []
        self.frame_end = []
        self.recv_time = []
        self.delay = []
        self.codec_bitrate = []

    def read_recv_file(self, filename):
        f = open(filename, mode='r')
        self.seq = []
        self.frame_id = []
        self.send_ts = []
        self.frame_start = []
        self.frame_end = []
        self.recv_time = []
        self.delay = []
        self.codec_bitrate = []
        for line in f:
            data = line.strip("\n").split(" ")
            self.seq.append(int(data[0].split(":")[1]))
            self.frame_id.append(int(data[1].split(":")[1]))
            self.send_ts.append(int(data[2].split(":")[1]))
            self.frame_start.append(int(data[3].split(":")[1]))
            self.frame_end.append(int(data[4].split(":")[1]))
            self.recv_time.append(int(data[5].split(":")[1]))
            self.delay.append(float(data[6].split(":")[1]))
            self.codec_bitrate.append(int(data[-1].split(":")[1]))
        f.close()
