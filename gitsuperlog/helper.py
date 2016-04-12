import csv
import os
from datetime import datetime, timedelta
from dateutil import tz
import bisect

tzUtc = tz.gettz('Etc/UTC')
tzBerlin = tz.gettz('Europe/Berlin')
unixTime = datetime(1970,1,1).replace(tzinfo=tzUtc)


def timestampFromDatetime(dt):
    # timestamp = (dt - unixTime) / timedelta(seconds=1)
    timestamp = round((dt - unixTime).total_seconds())
    return timestamp

def datetimeFromTimestamp(timestamp):
    dt = datetime.utcfromtimestamp(timestamp)
    dt = dt.replace(tzinfo=tzUtc)
    return dt

def transpose(lst):
    result = [[] for i in lst[0]]
    for i in lst:
        row = []
        for n,j in enumerate(i):
            result[n].append(j)
    return result

def getSetsFromCsv(path):
    rows = []
    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter=" ")
        for row in reader:
            rows.append(row)
    columns = transpose(rows)
    return columns

def merge(x1,y1,x2,y2):
    x1,y1 = zip(*sorted(zip(x1, y1)))
    x2,y2 = zip(*sorted(zip(x2, y2)))

    mergedX = sorted(set(x1 + x2))

    y1new = interpolate_new_x(x1,y1,mergedX)
    y2new = interpolate_new_x(x2,y2,mergedX)

    mergedY = []
    for i,j in zip(y1new,y2new):
        mergedY.append(i+j)

    return mergedX,mergedY
    # return mergedX,y1new

def interpolate_new_x(x1,y1,new_x1):
    yDict = {}
    new_y = []
    new_x1 = sorted(new_x1)
    for i,j in zip(x1,y1):
        yDict[i] = j


    idx = 0

    for i in new_x1:
        if i in x1:
            y = yDict[i]
        elif i < min(x1):
            # y = yDict[min(x1)]
            y = 0
        elif i > max(x1):
            y = yDict[max(x1)]
        else:
            pos = bisect.bisect(x1,i)
            bottom = x1[pos-1]
            top = x1[pos]

            bottomY = yDict[bottom]
            topY = yDict[top]
            y = float(bottomY) + (float(topY)-float(bottomY))/(float(top)-float(bottom)) * float((i-bottom))

        new_y.append(y)
    return new_y



def strListToInt(l):
    result = []
    for i in l:
        result.append(int(i))
    return result
