#!/usr/bin/python3
import os
import csv
import time
import multiprocessing
from pprint import pprint
from influxdb import InfluxDBClient

host = '127.0.0.1'
username = 'admin'
password = 'yourpassword'

client = InfluxDBClient(host=host, port=8086, username=username, password=password)
client.switch_database('stats')

date = os.popen("date +%s").read().split('\n')
time = ((int(date[0])) * 1000000000 - 10000000000)
hn = os.popen("hostname").read().split('\n')
avg = os.popen("cat /proc/loadavg | sed -e \'s/ /,/g\'").readlines()
avg = [i.rstrip('\n') for i in avg]
corecount = os.popen("cat /proc/cpuinfo | grep -E \"core id|processor|cpu cores\" | sort -u | cut -d\':\' -f -1|  uniq -c | awk \'{print $1}\' | paste - - - | sed -e \'s/\t/,/g\'")
pr={}
corecount = [i.rstrip('\n') for i in corecount]
for row in csv.reader(avg):
     pr['cpuinfo'] = {'1min': row[0], '5min': row[1], '15min': row[2]}
for row in csv.reader(corecount):
     pr['cpuinfo'].update({'sockets': row[1], 'cores': row[0], 'processors': row[2]})
for x,y in pr['cpuinfo'].items():
    pr['cpuinfo'][x] = float(y)

influx_data = []
influx_data.append(
		{
			"measurement": "cpusinfo",
			"tags": {
				"hostname" : hn[0],
			},
			"time": time,
			"fields": pr['cpuinfo']
			}
			)
client.write_points(influx_data)
