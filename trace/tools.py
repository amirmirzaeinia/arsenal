import os

dir = ['4g_200ms', '2_4g_200ms', '2_3g_200ms', '3g_200ms', 'wifi_200ms', '2_wifi_200ms']


def remove_space():
    for i in dir:
        path = './' + i
        file_list = os.listdir(path)
        for file in file_list:
            old_name = file
            new_name = file.replace(' ', '_')
            # print old_name
            os.rename('./' + i + '/' + old_name, './' + i + '/' + new_name)


def generate_mm_link():
    f = open('mm-link-scripts-4g-rl.txt', 'w')
    for i in dir:
        path = './' + i
        file_list = os.listdir(path)
        for file in file_list:
            delay = file.split('_')[5][:-2]
            # print delay
            loss = file.split('_')[-1].split('.')[0]
            # print loss
            mm_cmd = "mm-link trace/" + i + "/" + file + " trace/" + i + "/" + file
            if loss == '0':
                pass
            else:
                loss = int(loss) * 1.0 / 100
                mm_cmd += " mm-loss uplink " + str(loss)
            mm_cmd += " mm-delay " + delay + "\n"
            print mm_cmd
            f.write(mm_cmd)
    f.close()


def generate_mm_link_drop_tail():
    f = open('mm-link-scripts-with-drop-tail.txt', 'w')
    for i in dir:
        path = './' + i
        file_list = os.listdir(path)
        for file in file_list:
            print file
            delay = file.split('_')[5][:-2]
            # print delay
            loss = file.split('_')[-1].split('.')[0]
            # print loss
            # bandwidth = int(file.split('_')[3])
            # # print bandwidth
            # if bandwidth <= 1000000:
            #     buffer_packet_num = 60
            # elif bandwidth <= 2000000:
            #     buffer_packet_num = 100
            # else:
            #     buffer_packet_num = 130
            mm_cmd = "mm-link trace/" + i + "/" + file + " trace/" + i + "/" + file + ' --uplink-queue=droptail --uplink-queue-args=packets=150'

            if loss == '0':
                pass
            else:
                loss = int(loss) * 1.0 / 100
                mm_cmd += " mm-loss uplink " + str(loss)
            mm_cmd += " mm-delay " + delay + "\n"
            print mm_cmd
            f.write(mm_cmd)
    f.close()


if __name__ == '__main__':
    # remove_space()
    # generate_mm_link()
    generate_mm_link_drop_tail()
    pass
