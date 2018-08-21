import root_pandas as rpd
import glob as glob
import matplotlib.pyplot as plt
import datetime as dt
import os
import csv


def my_plot(time_axis, event_axis, metadata):
    plt.figure()
    trigger_count = 0
    event_count = 0
    print('Plotting now...')
    plt.plot(time_axis, event_axis, 'b.')

    for i in range(len(event_axis)):
        if event_axis[i] == 1:
            trigger_count += 1
            event_count += 1
        else:
            event_count += 1

    plt.title(metadata[0])
    plt.xlabel('Time (h/hhmmss)')
    plt.ylabel(metadata[1])
    plt.ylim(-.05, 1.4)
    plt.figtext(.15, .8, "{} Events:   {}\nTotal Events: {}".format(metadata[1].split(' ')[0],
                                                                    trigger_count, event_count))
    plt.savefig('{}.png'.format(metadata[2]))
    print('Plot Done: {}'.format(metadata[0]))


def create_log_file(log_data):
    log_file_path = os.path.join(os.getcwd(), 'log.csv')

    if not os.path.isfile(log_file_path):
        print('creating new log file...')
        log_file = open(log_file_path, 'w')
        log_writer = csv.writer(log_file)
        header = ['Filename', 'E-Hi Events', 'E-Lo Events', 'ZCal Events', 'Total Events']
        log_writer.writerow(header)
        log_file.close()

    log_file = open(log_file_path, 'a')
    log_writer = csv.writer(log_file)
    log_writer.writerow(log_data)
    log_file.close()


if __name__ == '__main__':

    Date = input("Date (yyyy/mm/dd): ")
    Files = glob.glob("/data/L0/"+Date+"/*.root")
    Files = [file for file in Files if 'hk' not in file and 'bsd' not in file]
    Files = sorted(Files)

    EHi_data = []
    ELo_data = []
    ZCal_data = []
    time_axis = []

    for i in range(len(Files)):
        log_data = []
        E_Hi = 0
        E_Lo = 0
        ZCal = 0
        Total_Events = 0
        try:
            Data = rpd.read_root(Files[i])
            log_data.append(Files[i][20:])
            print('Reading file: {} of {}: passed'.format(i+1, len(Files)))
        except (RuntimeWarning, OSError):
            print('error: file skipped: {} of {}'.format(i+1, len(Files)))
            pass

        for trig_vector in Data['trig']:
            ZCal_data.append(int(trig_vector[6]))
            EHi_data.append(int(trig_vector[7]))
            ELo_data.append(int(trig_vector[8]))

            if int(trig_vector[6]) == 1:
                ZCal += 1
            if int(trig_vector[7]) == 1:
                E_Hi += 1
            if int(trig_vector[8]) == 1:
                E_Lo += 1
            Total_Events += 1

        log_data.append(E_Hi)
        log_data.append(E_Lo)
        log_data.append(ZCal)
        log_data.append(Total_Events)

        for time in Data['time']:
            datetime_object = dt.datetime.strptime(str(time), '[%Y %m %d %H %M %S]')

            Title = '{} Events Plot\n' + "Date: " + str(datetime_object.date())
            Name = '{}-' + str(datetime_object.date())

            if int(datetime_object.hour) < 10:
                hour = str('0' + str(datetime_object.hour))
            else:
                hour = str(datetime_object.hour)

            if int(datetime_object.minute) < 10:
                minute = str('0' + str(datetime_object.minute))
            else:
                minute = str(datetime_object.minute)

            if int(datetime_object.second) < 10:
                second = str('0' + str(datetime_object.second))
            else:
                second = str(datetime_object.second)

            datetime_object = hour + minute + second
            datetime_object = int(datetime_object)
            time_axis.append(datetime_object)

        create_log_file(log_data)

    metadata = [Title.format('E-Hi'), 'E-Hi trigger bit', Name.format('E-Hi')]
    my_plot(time_axis, EHi_data, metadata)

    metadata = [Title.format('E-Lo'), 'E-Lo trigger bit', Name.format('E-Lo')]
    my_plot(time_axis, ELo_data, metadata)

    metadata = [Title.format('ZCal'), 'ZCal trigger bit', Name.format('ZCal')]
    my_plot(time_axis, ZCal_data, metadata)

    print('\nlog file created:')
