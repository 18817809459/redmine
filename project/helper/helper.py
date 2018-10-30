from project import models
import datetime
import os

def time_now():
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    dayscount = datetime.timedelta(days=now.isoweekday())
    week_start = now - dayscount + datetime.timedelta(days=1)
    week_end = now - dayscount + datetime.timedelta(days=7) + datetime.timedelta(days=1)
    week_list = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return year, month, day, week_start, week_end, week_list, dayscount, now


# 时间前端显示
def time_(created_time):
    year, month, day, week_start, week_end, week_list, dayscount, now = time_now()
    if created_time.year == year:
        if created_time.day == day:
            ele = str(created_time.hour).zfill(2) + ":" + str(created_time.minute).zfill(2)
        else:
            if created_time.day == day - 1:
                ele = "昨天"
            elif created_time >= week_start:
                ele = week_list[created_time.isoweekday()]
            else:
                ele = str(created_time.month).zfill(2) + "-" + str(created_time.day).zfill(2)
    else:
        ele = str(created_time.year).zfill(2) + "-" + str(created_time.month).zfill(2) + "-" + str(
            created_time.day).zfill(2)
    return ele


# 文件删除
def file_del(request):
    files = models.File.objects.filter(created_user=request.user, existent=False)
    for fil in files:
        try:
            os.remove(fil.file.path)
        except:
            pass
        fil.delete()