import os
import numpy as np
import re
import csv
import math

NETWORK_KINDS = ['3g', '4g', 'wifi']
ALGORITHMS = ['gcc', 'bbr', 'pcc_vivace', 'indigo', 'remyCC', 'aurora', 'il', 'rl']


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

    # the first packet received time as the beginning
    def compose_recv(self):
        tmp_recv_time = self.recv_time
        recv_begin = tmp_recv_time[0]
        for i in range(len(tmp_recv_time)):
            tmp_recv_time[i] -= recv_begin
        return tmp_recv_time  # ms

    def compute_frame_delay_codec_bitratre(self):
        """
        the last packet receive time - the first packet send time
        :return: ms
        """
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
        """
        compute the stalling times
        :return: list
        """
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
        return stalling

    def compute_rate_seconds(self):
        tmp_recv_time = self.compose_recv()
        start = tmp_recv_time[0]

        rate_ans = []

        codec_rate_seconds = []
        for index in range(len(tmp_recv_time)):
            if tmp_recv_time[index] - start <= 1000:
                codec_rate_seconds.append(self.codec_bitrate[index])
            else:
                rate_ans.append(round(np.mean(np.asarray(codec_rate_seconds)) / 1000000.0, 2))

                start += 1000
                codec_rate_seconds.append(self.codec_bitrate[index])
        if len(codec_rate_seconds) > 0:
            rate_ans.append(round(np.mean(np.asarray(codec_rate_seconds)) / 1000000.0, 2))

        # print(rate_ans)
        return rate_ans

    def compute_seconds_metric(self):
        receive_time = self.compose_recv()
        start = receive_time[0]
        packets_num = 0  # to compute the throughput in one second
        packets_seq = []  # to compute the packet loss in one second
        packets_delay = []  # to compute the delay in one second

        throughput_each_second = []
        packet_loss_each_second = []
        packet_average_delay_each_second = []

        for index in range(len(receive_time)):
            if receive_time[index] - start <= 1000:
                packets_num += 1
                packets_seq.append(self.seq[index])
                packets_delay.append(self.delay[index])
            else:
                throughput = packets_num * 1500 * 8.0 / 1000000.0
                if packets_seq is None or len(packets_seq) == 0:
                    pass
                else:
                    packet_loss = 1 - len(packets_seq) * 1.0 / (max(packets_seq) - min(packets_seq) + 1)  # [0,1]
                    packet_average_delay = np.mean(np.asarray(packets_delay))

                    throughput_each_second.append(throughput)
                    packet_loss_each_second.append(packet_loss)
                    packet_average_delay_each_second.append(packet_average_delay)

                # reset the start time
                start += 1000
                # print start
                # print len(packets_seq)
                index -= 1
                packets_num = 0
                packets_seq = []
                packets_delay = []

        if packets_num != 0:
            throughput = packets_num * 1500 * 8.0 / 1000000.0
            packet_loss = 1 - len(packets_seq) * 1.0 / (max(packets_seq) - min(packets_seq) + 1)  # [0,1]
            packet_average_delay = np.mean(np.asarray(packets_delay))

            throughput_each_second.append(throughput)
            packet_loss_each_second.append(packet_loss)
            packet_average_delay_each_second.append(packet_average_delay)

        # print(throughput_each_second)
        # print(packet_loss_each_second)
        # print(packet_average_delay_each_second)
        return throughput_each_second, packet_average_delay_each_second

    # the average throughput seconds level
    def compute_avg_throughput(self):
        throughput_each_second, packet_average_delay_each_second = self.compute_seconds_metric()
        return round(np.mean(np.asarray(throughput_each_second)), 2)


def get_file_path(path):
    dir = '../' + path
    subdirs = os.listdir(dir)

    total_file_path = []
    for dd in subdirs:
        subdir_path = dir + '/' + dd
        if os.path.isfile(subdir_path):
            continue
        else:
            files = os.listdir(subdir_path)
            for file in files:
                if file.find('recv_single') != -1:
                    file_path = subdir_path + '/' + file
                    # print(file_path)
                    total_file_path.append(file_path)
    # print(total_file_path)
    return total_file_path


def extract_stalling_time(path):
    # get all the log file path
    total_file_path = get_file_path(path=path)
    ext = Extract()

    for al in ALGORITHMS:
        stalling_res_file = '../' + path + '/stalling_' + al + '.csv'
        print(stalling_res_file)
        f = open(stalling_res_file, mode='w')
        csv_file = csv.writer(f, dialect='excel')
        line = []
        for file in total_file_path:
            if re.search(al, file, re.IGNORECASE):
                # print(file)
                ext.read_recv_file(file)
                stalling = ext.compute_stalling()
                line.append(np.sum(np.asarray(stalling)))
        csv_file.writerow(line)
        f.close()


def extract_frame_delay_codec_rate(path):
    # get all the log file path
    total_file_path = get_file_path(path=path)
    ext = Extract()

    x1 = -6.39
    y1 = 6.22 * 10
    z1 = 3.3

    x2 = -1.92
    y2 = 1.01 * 10
    z2 = 2.67

    for al in ALGORITHMS:

        print(al)
        frame_delay_res_file = '../' + path + '/frame_delay_' + al + '.csv'
        codec_rate_res_file = '../' + path + '/codec_rate_' + al + '.csv'
        QoE_1_res_file = '../' + path + '/QoE_p_' + al + '.csv'
        QoE_2_res_file = '../' + path + '/QoE_d_' + al + '.csv'

        f = open(frame_delay_res_file, mode='w')
        f1 = open(codec_rate_res_file, mode='w')
        f2 = open(QoE_1_res_file, mode='w')
        f3 = open(QoE_2_res_file, mode='w')
        #
        csv_file_frame_delay = csv.writer(f, dialect='excel')
        csv_file_codec_rate = csv.writer(f1, dialect='excel')
        #
        csv_file_QoE_1 = csv.writer(f2, dialect='excel')
        csv_file_QoE_2 = csv.writer(f3, dialect='excel')

        line_frame_delay = []
        line_codec_rate = []

        line_QoE_1 = []
        line_QoE_2 = []

        for file in total_file_path:
            if re.search(al, file, re.IGNORECASE):
                ext.read_recv_file(file)
                frame_delay, codec_rate = ext.compute_frame_delay_codec_bitratre()

                avg_frame_delay = round(np.mean(np.asarray(frame_delay)) / 1000.0, 2)
                avg_codec_rate = round(np.mean(np.asarray(codec_rate)) / 1000000.0, 2)

                line_frame_delay.append(avg_frame_delay)
                line_codec_rate.append(avg_codec_rate)

                QoE_1 = round(x1 * avg_frame_delay + y1 * avg_codec_rate + z1, 2)
                QoE_2 = round(x2 * avg_frame_delay + y2 * avg_codec_rate + z2, 2)

                line_QoE_1.append(QoE_1)
                line_QoE_2.append(QoE_2)

        # print(np.mean(line_QoE_1))
        # print(np.mean(line_QoE_2))

        csv_file_frame_delay.writerow(line_frame_delay)
        csv_file_codec_rate.writerow(line_codec_rate)
        csv_file_QoE_1.writerow(line_QoE_1)
        csv_file_QoE_2.writerow(line_QoE_2)

        f.close()
        f1.close()
        f2.close()
        f3.close()


def extract_compete_data():
    dir = '../compete'
    dd = os.listdir(dir)
    # print(dd)

    algorithms = ['rl', 'gcc', 'bbr', 'pcc_vivace', 'indigo', 'remyCC', 'pcc_rl', 'il']

    ext = Extract()

    # f = open("compete.txt", mode='w')

    for ii in range(len(algorithms)):
        for jj in range(ii + 1, len(algorithms)):
            name = algorithms[ii] + "_VS_" + algorithms[jj]
            # f.write(name)
            # f.write('\n')
            algorithm_ii_PQ = []
            algorithm_jj_PQ = []
            if algorithms[ii] == 'bbr' and algorithms[jj] == 'pcc_vivace':
                pass
            else:
                print(name)
                for item in dd:
                    if item.find("ms_" + name) != -1:
                        subdir = dir + '/' + item
                        for file in os.listdir(subdir):
                            # print(file)
                            file_name = subdir + '/' + file
                            # print(file_name)

                            # algorithm ii
                            if algorithms[ii] == 'rl':
                                if re.search('RL_recv', file, re.IGNORECASE):
                                    # print(file_name)
                                    ext.read_recv_file(file_name)
                                    frame_delay, codec_rate = ext.compute_frame_delay_codec_bitratre()
                                    avg_codec_rate = round(np.mean(np.asarray(codec_rate)) / 1000000.0, 2)
                                    algorithm_ii_PQ.append(avg_codec_rate)

                            elif algorithms[ii] == 'pcc_rl':
                                if re.search('aurora_recv', file, re.IGNORECASE):
                                    # print(file_name)
                                    ext.read_recv_file(file_name)
                                    frame_delay, codec_rate = ext.compute_frame_delay_codec_bitratre()
                                    avg_codec_rate = round(np.mean(np.asarray(codec_rate)) / 1000000.0, 2)
                                    algorithm_ii_PQ.append(avg_codec_rate)

                            else:
                                if re.search(algorithms[ii] + '_recv', file, re.IGNORECASE):
                                    # print(file_name)
                                    ext.read_recv_file(file_name)
                                    frame_delay, codec_rate = ext.compute_frame_delay_codec_bitratre()
                                    avg_codec_rate = round(np.mean(np.asarray(codec_rate)) / 1000000.0, 2)
                                    algorithm_ii_PQ.append(avg_codec_rate)
                            # algorithm jj
                            if algorithms[jj] == 'pcc_rl':
                                if re.search('aurora_recv', file, re.IGNORECASE):
                                    # print(file_name)
                                    ext.read_recv_file(file_name)
                                    frame_delay, codec_rate = ext.compute_frame_delay_codec_bitratre()
                                    avg_codec_rate = round(np.mean(np.asarray(codec_rate)) / 1000000.0, 2)
                                    algorithm_jj_PQ.append(avg_codec_rate)
                            else:
                                if re.search(algorithms[jj] + '_recv', file, re.IGNORECASE):
                                    # print(file_name)
                                    ext.read_recv_file(file_name)
                                    frame_delay, codec_rate = ext.compute_frame_delay_codec_bitratre()
                                    avg_codec_rate = round(np.mean(np.asarray(codec_rate)) / 1000000.0, 2)
                                    algorithm_jj_PQ.append(avg_codec_rate)
            if len(algorithm_jj_PQ) != 0:
                # f.write(str(algorithm_ii_PQ))
                # f.write('\n')
                # f.write(str(algorithm_jj_PQ))
                # f.write('\n')
                print(algorithm_ii_PQ)
                print(algorithm_jj_PQ)
                ans = 0.0
                for index in range(len(algorithm_ii_PQ)):
                    F = algorithm_ii_PQ[index] / algorithm_jj_PQ[index]
                    # F = (algorithm_ii_PQ[index] + algorithm_jj_PQ[index]) ** 2 / 2 / (
                    #         math.pow(algorithm_ii_PQ[index], 2) + math.pow(algorithm_jj_PQ[index], 2))
                    ans += F

                ans /= len(algorithm_ii_PQ)
                # f.write(str(round(ans, 4)))
                # f.write('\n')
                # f.write('###################')
                # f.write('\n')
                print(round(ans, 2))
                print(round(1 / ans, 2))
                print('###################')

                # P_numerator = pow(np.sum(np.asarray(algorithm_ii_PQ)), 2)
                # P_denominator = len(algorithm_ii_PQ) * pow(np.linalg.norm(np.asarray(algorithm_ii_PQ), ord=2), 2)
                # P = P_numerator / P_denominator
                #
                # Q_numerator = pow(np.sum(np.asarray(algorithm_jj_PQ)), 2)
                # Q_denominator = len(algorithm_ii_PQ) * pow(np.linalg.norm(np.asarray(algorithm_jj_PQ), ord=2), 2)
                # Q = Q_numerator / Q_denominator
                #
                # H = -math.log(P / Q)

                # print(algorithm_ii_PQ)
                # print(algorithm_jj_PQ)
                # print(P)
                # print(Q)
                # print(H)
            # print('\n')

    # f.close()


def extract_all_flows_competing():
    path = '../7flows'
    subdirs = os.listdir(path)

    ext = Extract()

    ans = []
    for sub in subdirs:
        sub_path = path + '/' + sub
        files = os.listdir(sub_path)
        ALGOR = []
        vec_rate = []

        f_sencods_name = '7flows_seconds_' + sub + '.csv'
        f_sencods = open(f_sencods_name, mode='w')
        csv_seconds = csv.writer(f_sencods, dialect='excel')

        for file in files:
            file_path = sub_path + '/' + file
            if file_path.find('recv') != -1:
                ALGOR.append(file.split('recv')[0][:-1])
                ext.read_recv_file(file_path)
                frame_delay, codec_rate = ext.compute_frame_delay_codec_bitratre()
                rate_seconds = ext.compute_rate_seconds()

                csv_seconds.writerow([file.split('recv')[0][:-1]])
                csv_seconds.writerow(rate_seconds)
                print(rate_seconds)
                # print(np.mean(frame_delay))
                # print(np.mean(codec_rate))
                print()

                avg_codec_rate = round(np.mean(np.asarray(codec_rate)) / 1000000.0, 2)
                vec_rate.append(avg_codec_rate)
        f_sencods.close()
        # compute the fairness from the vector
        numerator = pow(np.sum(np.asarray(vec_rate)), 2)
        denominator = len(vec_rate) * pow(np.linalg.norm(np.asarray(vec_rate), ord=2), 2)
        g = round(numerator / denominator, 4)
        ans.append(g)
        # print(ALGOR)
        # print(vec_rate)
        # print(g)
        print("########################")
    # print("avg:", np.mean(np.asarray(ans)))


def extract_pantheon_data():
    path = '../pantheon'
    subdir = os.listdir(path)

    ext = Extract()

    f = open('pantheon_points.csv', mode='w')
    csv_file = csv.writer(f, dialect='excel')

    for sub in subdir:
        sub_path = path + '/' + sub
        files = os.listdir(sub_path)
        link_name = sub_path.split('/')[-1]
        print(link_name)
        ALGOR = []
        RATE = []
        DELAY = []
        csv_line = []
        for file in files:
            file_path = sub_path + '/' + file
            if file_path.find('recv') != -1:
                ext.read_recv_file(file_path)
                frame_delay, codec_rate = ext.compute_frame_delay_codec_bitratre()
                algorithm_name = file.split('recv')[0][:-1]
                avg_codec_rate = round(np.mean(np.asarray(codec_rate)) / 1000000.0, 2)
                avg_frame_delay = round(np.mean(np.asarray(frame_delay)) / 1000.0, 2)
                ALGOR.append(algorithm_name)
                RATE.append(avg_codec_rate)
                DELAY.append(avg_frame_delay)
        for index in range(len(ALGOR)):
            csv_line.append(ALGOR[index])
            csv_line.append(RATE[index])
            csv_line.append(DELAY[index])
        # print(ALGOR)
        # print(RATE)
        # print(DELAY)
        csv_file.writerow([link_name])
        csv_file.writerow(csv_line)
        print(csv_line)
    f.close()


def extract_file_single():
    path = '../single_file'
    subdir = os.listdir(path)

    ext = Extract()

    all_throughput = []
    all_delay = []

    f = open('single_file.csv', mode='w')
    csv_file = csv.writer(f, dialect='excel')

    for sub in subdir:
        sub_path = path + '/' + sub
        files = os.listdir(sub_path)
        link_name = sub_path.split('/')[-1]
        print(link_name)
        ALGOR = []
        throughput = []
        delay = []

        # f_name = sub + '.csv'
        # f = open(f_name, mode='w')
        # csv_file = csv.writer(f, dialect='excel')
        csv_file.writerow([link_name])
        line = []

        for file in files:
            file_path = sub_path + '/' + file
            if file_path.find('recv') != -1:
                algorithm_name = file.split('recv')[0][:-1]
                ext.read_recv_file(file_path)
                throughput_seconds, delay_seconds = ext.compute_seconds_metric()

                avg_throughput_seconds = round(np.mean(np.asarray(throughput_seconds)), 2)
                avg_delay_seconds = round(np.mean(np.asarray(delay_seconds)), 2)
                ALGOR.append(algorithm_name)
                throughput.append(avg_throughput_seconds)
                delay.append(avg_delay_seconds)

                line.append(algorithm_name)
                line.append(avg_throughput_seconds)
                line.append(avg_delay_seconds)

        # all_throughput.append(throughput)
        # all_delay.append(delay)
        csv_file.writerow(line)
    f.close()
    # print(ALGOR)
    # # print(throughput)
    # # print(delay)
    # print(all_throughput)
    # print(all_delay)
    # line = []
    # for ii in range(len(ALGOR)):
    #     th = []
    #     de = []
    #     line.append(ALGOR[ii])
    #     for index in range(len(subdir)):
    #         th.append(all_throughput[index][ii])
    #         de.append(all_delay[index][ii])
    #     line.append(round(np.mean(np.asarray(th)), 2))
    #     line.append(round(np.mean(np.asarray(de)), 2))
    #     print(th)
    #     print(de)
    # print(line)
    # csv_file.writerow(line)


def extract_file_compete():
    dir = '../compete_file'
    dd = os.listdir(dir)
    # print(dd)

    algorithms = ['gcc', 'remyCC', 'indigo', 'pcc_rl', 'bbr', 'pcc_vivace', 'il', 'rl']

    ext = Extract()

    # f = open("compete_file.txt", mode='w')

    for ii in range(len(algorithms)):
        for jj in range(ii + 1, len(algorithms)):
            name = algorithms[ii] + "_VS_" + algorithms[jj]
            # f.write(name)
            # f.write('\n')
            algorithm_ii_PQ = []
            algorithm_jj_PQ = []
            if algorithms[ii] == 'bbr' and algorithms[jj] == 'pcc_vivace':
                pass
            else:
                print(name)
                for item in dd:
                    if item.find("compete_" + name) != -1:
                        # print(item)
                        subdir = dir + '/' + item
                        for file in os.listdir(subdir):
                            # print(file)
                            file_name = subdir + '/' + file
                            # print(file_name)

                            # algorithm ii
                            if algorithms[ii] == 'rl':
                                if re.search('RL_recv', file, re.IGNORECASE):
                                    # print(file_name)
                                    ext.read_recv_file(file_name)
                                    avg_throughput = ext.compute_avg_throughput()
                                    algorithm_ii_PQ.append(avg_throughput)

                            elif algorithms[ii] == 'pcc_rl':
                                if re.search('aurora_recv', file, re.IGNORECASE):
                                    # print(file_name)
                                    ext.read_recv_file(file_name)
                                    avg_throughput = ext.compute_avg_throughput()
                                    algorithm_ii_PQ.append(avg_throughput)

                            else:
                                if re.search(algorithms[ii] + '_recv', file, re.IGNORECASE):
                                    # print(file_name)
                                    ext.read_recv_file(file_name)
                                    avg_throughput = ext.compute_avg_throughput()
                                    algorithm_ii_PQ.append(avg_throughput)
                            # algorithm jj
                            if algorithms[jj] == 'pcc_rl':
                                if re.search('aurora_recv', file, re.IGNORECASE):
                                    # print(file_name)
                                    ext.read_recv_file(file_name)
                                    avg_throughput = ext.compute_avg_throughput()
                                    algorithm_jj_PQ.append(avg_throughput)
                            else:
                                if re.search(algorithms[jj] + '_recv', file, re.IGNORECASE):
                                    # print(file_name)
                                    ext.read_recv_file(file_name)
                                    avg_throughput = ext.compute_avg_throughput()
                                    algorithm_jj_PQ.append(avg_throughput)
            if len(algorithm_jj_PQ) != 0:
                # f.write(str(algorithm_ii_PQ))
                # f.write('\n')
                # f.write(str(algorithm_jj_PQ))
                # f.write('\n')
                print(algorithm_ii_PQ)
                print(algorithm_jj_PQ)
                ans = 0.0
                for index in range(len(algorithm_ii_PQ)):
                    # F = (algorithm_ii_PQ[index] + algorithm_jj_PQ[index]) ** 2 / 2 / (
                    #         math.pow(algorithm_ii_PQ[index], 2) + math.pow(algorithm_jj_PQ[index], 2))
                    F = algorithm_ii_PQ[index] / algorithm_jj_PQ[index]
                    ans += F

                ans /= len(algorithm_ii_PQ)
                # f.write(str(round(ans, 4)))
                # f.write('\n')
                # f.write('###################')
                # f.write('\n')
                print(round(ans, 2))
                print(round(1 / ans, 2))
                print('###################')
    # f.close()
    pass


def extract_cases():
    path = '../compete'
    VS_names = ['ms_rl_VS_il', 'ms_pcc_vivace_VS_indigo']

    dd = os.listdir(path)
    ext = Extract()

    for vs_name in VS_names:
        for subdir in dd:
            if subdir.find(vs_name) != -1:
                sub_path = path + '/' + subdir
                files = os.listdir(sub_path)

                f_name = subdir + '.csv'
                f = open(f_name, mode='w')

                csv_file = csv.writer(f, dialect='excel')
                print(subdir)
                # print(files)
                for file in files:
                    if file.find('recv') != -1:
                        file_path = sub_path + '/' + file
                        # print(file_path)
                        ext.read_recv_file(file_path)
                        rates = ext.compute_rate_seconds()

                        if file.find('RL') != -1:
                            csv_file.writerow(['RL'])
                            csv_file.writerow(rates)
                            print(rates)
                        if file.find('IL') != -1:
                            csv_file.writerow(['IL'])
                            csv_file.writerow(rates)
                            print(rates)
                        if file.find('indigo') != -1:
                            csv_file.writerow(['indigo'])
                            csv_file.writerow(rates)
                            print(rates)
                        if file.find('vivace') != -1:
                            csv_file.writerow(['pcc_vivace'])
                            csv_file.writerow(rates)
                            print(rates)
                f.close()


def extract_single_cases():
    paths = ['../drop150/3g/3g_1798660_17ms', '../drop150/4g/4g_2027280_30ms', '../drop150/wifi/wifi_3535080_8ms']
    ext = Extract()

    f = open('single_cases.csv', mode='w')
    csv_file = csv.writer(f, dialect='excel')

    for path in paths:

        link_name = path.split('/')[-1]
        csv_file.writerow([link_name])
        line = []

        files = os.listdir(path)
        for file in files:
            file_path = path + '/' + file
            if file.find('recv') != -1:
                ext.read_recv_file(file_path)
                frame_delay, codec_bitrate = ext.compute_frame_delay_codec_bitratre()
                algor_name = file.split('recv')[0][:-1]
                avg_codec_bitrate = round(np.mean(np.asarray(codec_bitrate)) / 1000000.0, 2)
                avg_frame_delay = round(np.mean(np.asarray(frame_delay)), 2)
                line.append(algor_name)
                line.append(avg_codec_bitrate)
                line.append(avg_frame_delay)
        csv_file.writerow(line)
        print(line)
    f.close()


def extract_compete_self():
    path = '../self_compete/file'
    dd = os.listdir(path)
    algorithms = ['gcc', 'indigo', 'remyCC', 'pcc_rl', 'il']

    ext = Extract()

    for algor in algorithms:
        name = algor + '_VS_' + algor

        ans = 0.0
        for item in dd:
            # print(item)
            if item.find(name) != -1:
                th = []
                subdir = path + '/' + item
                for file in os.listdir(subdir):
                    if file.find('recv') != -1:
                        file_path = subdir + '/' + file
                        ext.read_recv_file(file_path)

                        throughput = ext.compute_avg_throughput()

                        frame_delay, codec_bitrate = ext.compute_frame_delay_codec_bitratre()
                        avg_codec_bitrate = round(np.mean(np.asarray(codec_bitrate)) / 1000000.0, 2)

                        th.append(throughput)
                        # th.append(avg_codec_bitrate)
                numerator = pow(np.sum(np.asarray(th)), 2)
                denominator = len(th) * pow(np.linalg.norm(np.asarray(th), ord=2), 2)
                # ans += numerator / denominator
                ans += th[0] / th[1]
        ans /= 6
        print(algor)
        print(ans)
        print(1 / ans)


def extract_5g():
    path = '../5g'
    files = os.listdir(path)
    als = ['Aurora', 'BBR', 'GCC', 'IL', 'indigo', 'pcc_vivace', 'RemyCC', 'RL']

    ext = Extract()

    for al in als:
        print(al)
        for file in files:
            if file.find(al) != -1 and file.find('recv') != -1:
                file_path = path + '/' + file
                ext.read_recv_file(file_path)
                frame_delay, codec_rate = ext.compute_frame_delay_codec_bitratre()
                print(round(np.mean(frame_delay), 2))
                print(round(np.mean(codec_rate) / 1000000.0))


if __name__ == '__main__':
    path = 'drop150/3g'
    # extract_stalling_time(path)
    # extract_frame_delay_codec_rate(path)
    # extract_compete_data()
    # extract_all_flows_competing()
    # extract_pantheon_data()
    # extract_file_single()
    # extract_cases()
    # extract_file_compete()
    # extract_single_cases()
    # extract_compete_self()
    extract_5g()

    # ext = Extract()
    # ext.read_recv_file('../7flows/mm_3g_2416940/BBR_recv_multi.log')
    # ext.compute_rate_seconds()
