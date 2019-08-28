import os
import time


def run():
    f = open('./trace/mm-link-scripts-compete.txt', mode='r')
    traces = []
    for line in f:
        traces.append(line.split('\n')[0])
    f.close()
    subdirs = []
    for tt in traces:
        trace_name = tt.split(' ')[1].split('/')[2].split('.')[0]
        subdir = trace_name.split('_')[0] + "_" + trace_name.split('_')[3] + "_" + trace_name.split('_')[
            5] + '_file'
        subdirs.append(subdir)

    # rl_algorithm = ['rl']
    # algorithms = ['gcc', 'remyCC', 'indigo', 'pcc_rl', 'bbr', 'pcc_vivace', 'il', 'rl']

    algorI = ['indigo', 'gcc', 'remyCC', 'pcc_rl', 'il']
    # algorII = ['indigo']
    portI = 13140
    portII = 13141
    print subdirs

    for kk in range(len(subdirs)):
        for ii in range(len(algorI)):
            begin = time.time()
            cc_vs_cmd = './multi_oneself_server.py ' + subdirs[kk] + "_" + algorI[ii] + "_VS_" + algorI[ii]
            server_cmd = cc_vs_cmd + " " + algorI[ii] + " " + algorI[ii] + " " + str(portI) + " " + str(portII)
            print server_cmd
            os.system(server_cmd)
            while True:
                if time.time() - begin > 120:
                    break
            print (algorI[ii], algorI[ii], 'done')
            portI += 2
            portII += 2
        time.sleep(1)


if __name__ == '__main__':
    run()
