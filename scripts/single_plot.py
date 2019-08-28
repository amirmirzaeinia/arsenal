import matplotlib.pyplot as plt


class SinglePlot(object):
    def __init__(self, labels=None):
        self.seq = []
        self.frame_id = []
        self.send_ts = []
        self.frame_start = []
        self.frame_end = []
        self.recv_time = []
        self.delay = []

        self.send_time = []
        self.send_rate = []

        self.labels = labels
        self.fig = plt.figure()

        self.trace = []

    def read_log(self, file):
        f = open(file, mode='r')
        for line in f:
            data = line.strip("\n").split(" ")
            self.seq.append(int(data[0].split(":")[1]))
            self.frame_id.append(int(data[1].split(":")[1]))
            self.send_ts.append(int(data[2].split(":")[1]))
            self.frame_start.append(int(data[3].split(":")[1]))
            self.frame_end.append(int(data[4].split(":")[1]))
            self.recv_time.append(int(data[5].split(":")[1]))
            self.delay.append(float(data[6].split(":")[1]))
        f.close()

    def read_send_log(self, file):
        f = open(file, 'r')
        for line in f:
            data = line.strip("\n").split(" ")
            self.send_time.append(int(data[1]))
            self.send_rate.append(float(data[3]))
        f.close()

    def read_trace(self, file):
        f = open(file, 'r')
        for line in f:
            data = line.strip("\n")
            self.trace.append(int(data))
        f.close()

    def compose_recv(self):
        tmp_recv_time = self.recv_time
        recv_begin = tmp_recv_time[0]
        for i in range(len(tmp_recv_time)):
            tmp_recv_time[i] -= recv_begin
        return tmp_recv_time  # ms

    def plot_send_rate(self):
        ax = self.fig.add_subplot(1, 1, 1)
        ax.set_title("throughput")
        ax.set_xlabel(xlabel='time(ms)')
        ax.set_ylabel(ylabel='throughput(mbps)')
        ax.locator_params('x', tight=True, nbins=20)
        ax.locator_params('y', tight=True, nbins=10)

        ax.plot(self.send_time, self.send_rate, color="C1", label="GCC send")

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

        ax.plot(tmp_recv_time, recv_rate, color="C2", label="GCC receive")

        traces = []
        for i in range((len(self.trace))):
            packets_num = 0
            for j in range(i, 0, -1):
                if self.trace[i] - self.trace[j] < 1000:
                    packets_num += 1
                else:
                    break
            traces.append(packets_num * 1500 * 8.0 / 1000000)
        ax.plot(self.trace, traces, color="C3", label="trace")

        ax.legend()


def main():
    singlePlot = SinglePlot()
    subdir = '071714'
    file = '../log/' + subdir + '/GCC_send_single.log'
    recv_file = '../log/' + subdir + '/GCC_recv_single.log'
    trace_file = '../3.04mbps-poisson.trace'
    singlePlot.read_send_log(file)
    singlePlot.read_log(recv_file)
    singlePlot.read_trace(trace_file)

    singlePlot.compose_recv()
    singlePlot.plot_send_rate()

    plt.show()


if __name__ == '__main__':
    main()
