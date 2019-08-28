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
        # print self.codec_bitrate

    # the first packet received time as the beginning
    def compose_recv(self):
        tmp_recv_time = self.recv_time
        recv_begin = tmp_recv_time[0]
        for i in range(len(tmp_recv_time)):
            tmp_recv_time[i] -= recv_begin
        return tmp_recv_time  # ms

    # the receive rate (mbps)
    def compute_average_throughput(self):
        tmp_recv_time = self.compose_recv()
        recv_rate = []
        for i in range(len(tmp_recv_time)):
            packets_num = 0
            for j in range(i, 0, -1):
                if tmp_recv_time[i] - tmp_recv_time[j] < 1000:
                    packets_num += 1
                else:
                    break
            recv_rate.append(packets_num * 1500 * 8.0 / 1000000)
        print len(recv_rate)
        print recv_rate
        return np.mean(np.asarray(recv_rate))

    def compute_frame_delay_codec_bitratre(self):
        '''
        the last packet receive time - the first packet send time
        :return: ms
        '''
        current_frame_id = self.frame_id[0]
        current_frame_start = self.send_ts[0]
        current_frame_end = self.recv_time[0]
        rate = self.codec_bitrate[0]
        frame_delay = []
        codec_bitrate = []

        for index in range(len(self.frame_id)):
            if self.frame_id[index] == current_frame_id:
                current_frame_end = self.recv_time[index]
                rate = self.codec_bitrate[index]
            else:
                current_frame_delay = current_frame_end - current_frame_start
                frame_delay.append(current_frame_delay)
                codec_bitrate.append(rate)

                current_frame_start = self.send_ts[index]
                current_frame_end = self.recv_time[index]
                current_frame_id = self.frame_id[index]
                rate = self.codec_bitrate[index]

        # the last frame
        current_frame_delay = current_frame_end - current_frame_start
        frame_delay.append(current_frame_delay)
        codec_bitrate.append(rate)
        return frame_delay, codec_bitrate

    def compute_stalling(self):
        current_frame_id = self.frame_id[0]
        current_frame_end = self.recv_time[0]
        last_frame_end = self.recv_time[0]
        stalling = []
        flag = 0
        for index in range(len(self.frame_id)):
            if self.frame_id[index] == current_frame_id:
                current_frame_end = self.recv_time[index]

            else:
                if flag == 0:
                    flag += 1
                    last_frame_end = current_frame_end
                    current_frame_end = self.recv_time[index]
                    current_frame_id = self.frame_id[index]
                else:
                    # 50 + 33
                    if current_frame_end - last_frame_end > 83:
                        stalling.append(1)
                    else:
                        stalling.append(0)
                    last_frame_end = current_frame_end
                    current_frame_end = self.recv_time[index]
                    current_frame_id = self.frame_id[index]

        if current_frame_end - last_frame_end > 83:
            stalling.append(1)
        else:
            stalling.append(0)
        print stalling
        print np.sum(np.asarray(stalling))
        return stalling

    def compute_avrage_delay(self):
        print len(self.delay)
        print self.delay
        return np.mean(np.asarray(self.delay))

    # the total progress
    def compute_packet_loss(self):
        return 1 - len(self.seq) / (max(self.seq) - min(self.seq) + 1)

    def compute_frame_loss(self):
        frame_packet_start = self.frame_start[0]
        frame_packet_end = self.frame_end[0]
        packets_per_frame = 0
        total_frame = max(self.frame_id) + 1
        lost_frame = 0
        for index in range(len(self.frame_start)):
            if self.frame_start[index] == frame_packet_start:
                packets_per_frame += 1
            else:
                if packets_per_frame * 1.0 / (frame_packet_end - frame_packet_start + 1) < 0.5:
                    lost_frame += 1
                # reset
                frame_packet_start = self.frame_start[index]
                frame_packet_end = self.frame_end[index]
                packets_per_frame = 0
                index -= 1
        return lost_frame * 1.0 / total_frame

    """
    def compute_second_level_metrics(self):
        receive_time = self.compose_recv()
        start = receive_time[0]
        packets_num = 0  # to compute the throughput in one second
        packets_seq = []  # to compute the packet loss in one second
        packets_delay = []  # to compute the delay in one second

        throughput_each_second = []
        packet_loss_each_second = []
        packet_average_delay_each_second = []

        for index in range(len(receive_time)):
            if receive_time[index] - start <= 5000:
                packets_num += 1
                packets_seq.append(self.seq[index])
                packets_delay.append(self.delay[index])
            else:
                throughput = packets_num * 1500 * 8.0 / 1000000.0 / 5
                if packets_seq == None or len(packets_seq) == 0:
                    pass
                else:
                    packet_loss = 1 - len(packets_seq) * 1.0 / (max(packets_seq) - min(packets_seq) + 1)  # [0,1]
                    packet_average_delay = np.mean(np.asarray(packets_delay))

                    throughput_each_second.append(throughput)
                    packet_loss_each_second.append(packet_loss)
                    packet_average_delay_each_second.append(packet_average_delay)

                # reset the start time
                start += 5000
                # print start
                # print len(packets_seq)
                index -= 1
                packets_num = 0
                packets_seq = []
                packets_delay = []

        if packets_num != 0:
            throughput = packets_num * 1500 * 8.0 / 1000000.0 / 5
            packet_loss = 1 - len(packets_seq) * 1.0 / (max(packets_seq) - min(packets_seq) + 1)  # [0,1]
            packet_average_delay = np.mean(np.asarray(packets_delay))

            throughput_each_second.append(throughput)
            packet_loss_each_second.append(packet_loss)
            packet_average_delay_each_second.append(packet_average_delay)

        print throughput_each_second
        print packet_loss_each_second
        print packet_average_delay_each_second

        return throughput_each_second, packet_loss_each_second, packet_average_delay_each_second
"""


def get_file_path(path=''):
    # ext = Extract()
    subdir = path
    dir = '../log/' + subdir
    files = os.listdir(dir)
    total_file_path = []

    for file in files:
        if file.find('recv_single') != -1:
            file_path = dir + '/' + file
            total_file_path.append(file_path)
    return total_file_path


def extract_frame_delay(path='', r1=1, r2=1, r3=0):
    # print path
    total_file_path = get_file_path(path)
    ext = Extract()

    frame_delay_dir = '../log/' + path + '/frame_delay'
    codec_bitrate_dir = '../log/' + path + '/codec_bitrate'
    QoE_dir = '../log/' + path + '/QoE'

    if not os.path.exists(frame_delay_dir):
        os.mkdir(frame_delay_dir)

    if not os.path.exists(codec_bitrate_dir):
        os.mkdir(codec_bitrate_dir)

    if not os.path.exists(QoE_dir):
        os.mkdir(QoE_dir)

    # points
    f_avg = open('../log/' + path + '/avg_res.csv', 'w')
    csv_file_avg = csv.writer(f_avg, dialect='excel')

    for file in total_file_path:
        # print file
        file_name1 = frame_delay_dir + '/frame_delay_' + file.split('/')[-1].split('.')[0] + '.csv'
        file_name2 = codec_bitrate_dir + '/codec_bitrate_' + file.split('/')[-1].split('.')[0] + '.csv'
        file_name3 = QoE_dir + '/QoE_' + file.split('/')[-1].split('.')[0] + '.csv'

        f1 = open(file_name1, 'w')
        f2 = open(file_name2, 'w')
        f3 = open(file_name3, 'w')

        csv_file1 = csv.writer(f1, dialect='excel')
        csv_file2 = csv.writer(f2, dialect='excel')
        csv_file3 = csv.writer(f3, dialect='excel')

        ext.read_recv_file(file)
        frame_delay, codec_bitrate = ext.compute_frame_delay_codec_bitratre()  # list

        avg_frame_delay = np.mean(np.asarray(frame_delay))
        avg_codec_bitrate = np.mean(np.asarray(codec_bitrate))

        # print [file.split('/')[-1].split('_')[0], avg_frame_delay, avg_codec_bitrate]
        csv_file_avg.writerow([file.split('/')[-1].split('_')[0], avg_frame_delay, avg_codec_bitrate])

        # print len(frame_delay)

        # frame delay
        line = []
        for delay in frame_delay:
            line.append(delay)
        csv_file1.writerow(line)

        # codec bitrate
        line = []
        for rate in codec_bitrate:
            line.append(rate / 1000000.0)
        csv_file2.writerow(line)

        # QoE
        QoE_line = []
        for ii in range(len(frame_delay)):
            QoE_line.append(r1 * frame_delay[ii] + r2 * codec_bitrate[ii] + r3)
        csv_file3.writerow(QoE_line)

        f1.close()
        f2.close()
        f3.close()
    f_avg.close()


def extract_stalling(path=''):
    total_file_path = get_file_path(path)
    ext = Extract()
    stalling_dir = '../log/' + path + '/stalling'
    if not os.path.exists(stalling_dir):
        os.mkdir(stalling_dir)

    for file in total_file_path:
        stalling_file_name = stalling_dir + '/stalling_' + file.split('/')[-1].split('.')[0] + '.csv'

        f = open(stalling_file_name, mode='w')
        csv_file = csv.writer(f, dialect='excel')

        ext.read_recv_file(file)
        stalling_list = ext.compute_stalling()

        csv_file.writerow(stalling_list)
        csv_file.writerow([np.sum(np.asarray(stalling_list))])  # total stalling time

        f.close()


"""
def extract_one_second_metrics(path=''):
    total_file_path = get_file_path(path)
    ext = Extract()

    throughput_dir = '../log/' + path + '/throughput_seconds'
    packet_loss_dir = '../log/' + path + '/packet_loss_seconds'
    packet_average_delay_dir = '../log/' + path + '/packet_delay_seconds'

    if not os.path.exists(throughput_dir):
        os.mkdir(throughput_dir)

    if not os.path.exists(packet_loss_dir):
        os.mkdir(packet_loss_dir)

    if not os.path.exists(packet_average_delay_dir):
        os.mkdir(packet_average_delay_dir)

    f = open('../log/' + path + '/avg_res.csv', 'w')
    csv_file = csv.writer(f, dialect='excel')

    for file in total_file_path:
        print file
        ext.read_recv_file(file)
        throughput_each_second, packet_loss_each_second, packet_average_delay_each_second = ext.compute_second_level_metrics()

        throughput_file_name = throughput_dir + '/throughput_seconds_' + file.split('/')[-1].split('.')[0] + '.csv'
        packet_loss_file_name = packet_loss_dir + '/packet_loss_seconds_' + file.split('/')[-1].split('.')[0] + '.csv'
        packet_delay_file_name = packet_average_delay_dir + '/packet_delay_seconds' + file.split('/')[-1].split('.')[
            0] + '.csv'

        avg_throughput = np.mean(np.asarray(throughput_each_second))
        avg_delay = np.mean(np.asarray(packet_average_delay_each_second))
        # print file
        line = [file.split('/')[-1].split('_')[0], avg_throughput, avg_delay]
        csv_file.writerow(line)

        f1 = open(throughput_file_name, 'w')
        f2 = open(packet_loss_file_name, 'w')
        f3 = open(packet_delay_file_name, 'w')
        csv_file1 = csv.writer(f1, dialect='excel')
        csv_file2 = csv.writer(f2, dialect='excel')
        csv_file3 = csv.writer(f3, dialect='excel')
        for throughput in throughput_each_second:
            line = [throughput]
            csv_file1.writerow(line)

        for loss in packet_loss_each_second:
            line = [loss]
            csv_file2.writerow(line)

        for delay in packet_average_delay_each_second:
            line = [delay]
            csv_file3.writerow(line)

        f1.close()
        f2.close()
        f3.close()

    f.close()


def extract_throughput_delay(path=''):
    ext = Extract()
    subdir = path
    dir = '../log/' + subdir
    files = os.listdir(dir)

    des_path = dir + '/res_' + path + '.csv'
    res = open(des_path, mode='w')
    csv_write = csv.writer(res, dialect='excel')

    for file in files:
        if file.find('recv_single') != -1:
            file_path = dir + '/' + file

            print file_path

            ext.read_recv_file(file_path)
            avg_throughput = ext.compute_average_throughput()
            avg_delay = ext.compute_avrage_delay()
            # line = [file.split('_')[0], avg_throughput, avg_delay]
            # csv_write.writerow(line)

            print avg_throughput
            print avg_delay
"""

if __name__ == '__main__':
    path = '3g_1464880_59ms'

    # extract_frame_delay(path)
    extract_stalling(path)
    # extract_one_second_metrics(path)
