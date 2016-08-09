import time
import pymongo

client = pymongo.MongoClient("localhost", 27017)
db = client.minio


def video_sel(buk='CON812A930BA4D', start=1470386226, end=1470386826):
    result = db.s3objects.find({"modtime": {"$gte": start, "$lte": end}, "bucket": buk})  # lt:<   gt:>  ne:!=  lte:<=
    video = []
    for i in result:
        video.append(i)

    return video


if __name__ == "__main__":
    starttime = "2016-08-08:08:08:08"
    temp = starttime.split("-")
    temp[2:] = temp[2].split(":")
    temp.extend(['0', '0', '0'])
    temp = int(time.mktime(tuple([int(i) for i in temp])))
    endtime = "2016-08-08:09:08:08"
    tmp = endtime.split("-")
    tmp[2:] = tmp[2].split(":")
    tmp.extend(['0', '0', '0'])
    tmp = int(time.mktime(tuple([int(i) for i in tmp])))
    print video_sel(start=temp, end=tmp)

