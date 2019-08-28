import matplotlib.pyplot as plt


class LogPlot(object):
    def __init__(self, labels=None, log_file_path=None, throughput_file_path=None):
        self.seq_num = []
        self.frame_id = []
        self.send_ts = []
        self.frame_start = []
        self.frame_end = []
        self.recv_time = []
        self.delay = []

        self.throughput = []

        self.labels = labels

        self.log_file_path = log_file_path
        self.throughput_file_path = throughput_file_path

        self.fig = plt.figure()

    def read_log(self, file):
        f = open(file, mode='r')
        for line in f:
            data = line.strip("\n").split(" ")
            self.seq_num.append(int(data[0].split(":")[1]))
            self.frame_id.append(int(data[1].split(":")[1]))
            self.send_ts.append(data[2].split(":")[1])
            self.frame_start.append(int(data[3].split(":")[1]))
            self.frame_end.append(int(data[4].split(":")[1]))
            self.recv_time.append(data[5].split(":")[1])
            self.delay.append(float(data[6].split(":")[1]))
        f.close()

    def read_throughput(self, file):
        f = open(file, mode='r')
        throughput = []
        for line in f:
            data = line.strip("\n").split(" ")
            throughput.append(float(data[1]))
        f.close()
        return throughput

    def plot_throughput(self):
        total_throughput = []
        for file in self.throughput_file_path:
            total_throughput.append(self.read_throughput(file))

        ax = self.fig.add_subplot(3, 1, 1)
        ax.set_title(label='multi flows throughput')
        ax.set_xlabel(xlabel='time/s')
        ax.set_ylabel(ylabel='throughput/mbps')
        ax.locator_params('x', tight=True, nbins=20)
        ax.locator_params('y', tight=True, nbins=10)
        plt.tight_layout()

        for index in range(len(total_throughput)):
            data = total_throughput[index]
            x = [i for i in range(len(data))]
            clr = "C" + str(index + 1)
            ax.plot(x, data, color=clr, label=self.labels[index], linewidth=3)
        ax.legend()

    def plot_delay(self):

        ax = self.fig.add_subplot(3, 1, 2)
        ax.set_title(label='multi flows delay')
        ax.set_xlabel(xlabel='time/s')
        ax.set_ylabel(ylabel='delay/ms')
        ax.locator_params('x', tight=True, nbins=20)
        ax.locator_params('y', tight=True, nbins=10)
        plt.tight_layout()

        for ii in range(len(self.log_file_path)):
            path = self.log_file_path[ii]

            self.seq_num = []
            self.frame_id = []
            self.send_ts = []
            self.frame_start = []
            self.frame_end = []
            self.recv_time = []
            self.delay = []

            self.read_log(path)

            tmp_recv_time = self.recv_time
            begin = tmp_recv_time[0]
            for i in range(len(tmp_recv_time)):
                tmp_recv_time[i] = float(tmp_recv_time[i]) - float(begin)

            ax.plot(tmp_recv_time, self.delay, color="C" + str(ii + 1), label=self.labels[ii], linewidth=2)
        ax.legend()

    def compute_packet_loss_and_throughput(self):
        packet_queue = self.seq_num
        tmp_recv_time = self.recv_time

        loss = []
        recv_time = []
        throughputs = []

        for i in range(1, len(packet_queue)):
            tmp_throughput = 0
            if i < 49:
                lo = 1 - (i + 1) / (int(packet_queue[i]) - int(packet_queue[0]) + 1)
                tmp_throughput = 0
            else:
                lo = 1 - 50.0 / (int(packet_queue[i]) - int(packet_queue[i - 49]) + 1)
                tmp_throughput = 50 * 1500.0 * 8 / (float(tmp_recv_time[i]) - float(tmp_recv_time[i - 49])) / 1000000.0
            loss.append(lo)
            throughputs.append(tmp_throughput)
            recv_time.append(tmp_recv_time[i])

        return recv_time, loss, throughputs

    def plot_packet_loss_and_throughput(self):

        ax0 = self.fig.add_subplot(3, 1, 1)
        ax0.set_title(label='multi flows throughput')
        ax0.set_xlabel(xlabel='time/s')
        ax0.set_ylabel(ylabel='throughput/mbps')
        ax0.locator_params('x', tight=True, nbins=20)
        ax0.locator_params('y', tight=True, nbins=10)
        plt.tight_layout()

        ax = self.fig.add_subplot(3, 1, 3)
        ax.set_title(label='multi flows packet loss')
        ax.set_xlabel(xlabel='time/s')
        ax.set_ylabel(ylabel='loss')
        ax.locator_params('x', tight=True, nbins=20)
        ax.locator_params('y', tight=True, nbins=10)
        plt.tight_layout()

        for ii in range(len(self.log_file_path)):
            path = self.log_file_path[ii]

            self.seq_num = []
            self.frame_id = []
            self.send_ts = []
            self.frame_start = []
            self.frame_end = []
            self.recv_time = []
            self.delay = []

            self.read_log(path)

            recv_time, loss, throughputs = self.compute_packet_loss_and_throughput()

            tmp_recv_time = recv_time
            begin = tmp_recv_time[0]
            for i in range(len(tmp_recv_time)):
                tmp_recv_time[i] = float(tmp_recv_time[i]) - float(begin)
            ax0.plot(tmp_recv_time, throughputs, color="C" + str(ii + 1), label=self.labels[ii], linewidth=2)
            ax.plot(tmp_recv_time, loss, color="C" + str(ii + 1), label=self.labels[ii], linewidth=2)
        ax0.legend()
        ax.legend()


def main():
    subdir = '07092154'

    labels = ['IL', 'RL', 'GCC', 'indigo', 'remyCC']

    throughput_file_path = ["../log/" + subdir + "/IL_recv_throughput.log",
                            "../log/" + subdir + "/RL_recv_throughput.log",
                            "../log/" + subdir + "/GCC_recv_throughput.log",
                            "../log/" + subdir + "/indigo_recv_throughput.log",
                            ]

    log_file_path = ["../log/" + subdir + "/IL_recv.log",
                     "../log/" + subdir + "/RL_recv.log",
                     "../log/" + subdir + "/GCC_recv.log",
                     "../log/" + subdir + "/indigo_recv.log",
                     "../log/" + subdir + "/RemyCC_recv.log", ]

    logPlot = LogPlot(labels=labels, log_file_path=log_file_path, throughput_file_path=None)

    # logPlot.plot_throughput()
    logPlot.plot_delay()
    logPlot.plot_packet_loss_and_throughput()
    plt.show()


if __name__ == '__main__':
    main()
