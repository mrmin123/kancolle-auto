# Ensei (expedition) task list.

import datetime


class Ensei:
    def __init__(self, ensei_id, name_pict, area_pict, duration):
        self.id = ensei_id
        self.name_pict = name_pict
        self.area_pict = area_pict
        self.duration = duration

    def __str__(self):
        return 'ensei id = %d, end time = %s' % (self.id, self.ends_time())

    def start(self):
        self.begin_time = datetime.datetime.now()
        self.end_time = self.begin_time + self.duration

    def ends_time(self):
        if hasattr(self, "begin_time"):
            return self.begin_time + self.duration
        else:
            return datetime.datetime.now() + self.duration


def ensei_factory(ensei_id):
    if ensei_id == 1:
        return Ensei(1, 'ensei_name_01.png', 'ensei_area_01.png', datetime.timedelta(minutes=15))
    elif ensei_id == 2:
        return Ensei(2, 'ensei_name_02.png', 'ensei_area_01.png', datetime.timedelta(minutes=30))
    elif ensei_id == 3:
        return Ensei(3, 'ensei_name_03.png', 'ensei_area_01.png', datetime.timedelta(minutes=20))
    elif ensei_id == 4:
        return Ensei(4, 'ensei_name_04.png', 'ensei_area_01.png', datetime.timedelta(minutes=50))
    elif ensei_id == 5:
        return Ensei(5, 'ensei_name_05.png', 'ensei_area_01.png', datetime.timedelta(minutes=90))
    elif ensei_id == 6:
        return Ensei(6, 'ensei_name_06.png', 'ensei_area_01.png', datetime.timedelta(minutes=40))
    elif ensei_id == 7:
        return Ensei(7, 'ensei_name_07.png', 'ensei_area_01.png', datetime.timedelta(hours = 1))
    elif ensei_id == 8:
        return Ensei(8, 'ensei_name_08.png', 'ensei_area_01.png', datetime.timedelta(hours=3))

    elif ensei_id == 9:
        return Ensei(9, 'ensei_name_09.png', 'ensei_area_02.png', datetime.timedelta(hours=4))
    elif ensei_id == 10:
        return Ensei(10, 'ensei_name_10.png', 'ensei_area_02.png', datetime.timedelta(hours=1, minutes=30))
    elif ensei_id == 11:
        return Ensei(11, 'ensei_name_11.png', 'ensei_area_02.png', datetime.timedelta(hours=5))
    elif ensei_id == 12:
        return Ensei(12, 'ensei_name_12.png', 'ensei_area_02.png', datetime.timedelta(hours=8))
    elif ensei_id == 13:
        return Ensei(13, 'ensei_name_13.png', 'ensei_area_02.png', datetime.timedelta(hours=4))
    elif ensei_id == 14:
        return Ensei(14, 'ensei_name_14.png', 'ensei_area_02.png', datetime.timedelta(hours=6))
    elif ensei_id == 15:
        return Ensei(15, 'ensei_name_15.png', 'ensei_area_02.png', datetime.timedelta(hours=12))
    elif ensei_id == 16:
        return Ensei(16, 'ensei_name_16.png', 'ensei_area_02.png', datetime.timedelta(hours=15))

    elif ensei_id == 17:
        return Ensei(17, 'ensei_name_17.png', 'ensei_area_03.png', datetime.timedelta(minutes=45))
    elif ensei_id == 18:
        return Ensei(18, 'ensei_name_18.png', 'ensei_area_03.png', datetime.timedelta(hours=5))
    elif ensei_id == 19:
        return Ensei(19, 'ensei_name_19.png', 'ensei_area_03.png', datetime.timedelta(hours=6))
    elif ensei_id == 20:
        return Ensei(20, 'ensei_name_20.png', 'ensei_area_03.png', datetime.timedelta(hours=2))
    elif ensei_id == 21:
        return Ensei(21, 'ensei_name_21.png', 'ensei_area_03.png', datetime.timedelta(hours=2, minutes=20))
    elif ensei_id == 22:
        return Ensei(22, 'ensei_name_22.png', 'ensei_area_03.png', datetime.timedelta(hours=3))

    elif ensei_id == 25:
        return Ensei(25, 'ensei_name_25.png', 'ensei_area_04.png', datetime.timedelta(hours=40))
    elif ensei_id == 26:
        return Ensei(26, 'ensei_name_26.png', 'ensei_area_04.png', datetime.timedelta(hours=80))
    elif ensei_id == 27:
        return Ensei(27, 'ensei_name_27.png', 'ensei_area_04.png', datetime.timedelta(hours=20))
    elif ensei_id == 28:
        return Ensei(28, 'ensei_name_28.png', 'ensei_area_04.png', datetime.timedelta(hours=25))
    elif ensei_id == 29:
        return Ensei(29, 'ensei_name_29.png', 'ensei_area_04.png', datetime.timedelta(hours=24))
    elif ensei_id == 30:
        return Ensei(30, 'ensei_name_30.png', 'ensei_area_04.png', datetime.timedelta(hours=48))

    elif ensei_id == 35:
        return Ensei(35, 'ensei_name_35.png', 'ensei_area_05.png', datetime.timedelta(hours=7))
    elif ensei_id == 36:
        return Ensei(36, 'ensei_name_36.png', 'ensei_area_05.png', datetime.timedelta(hours=9))
    elif ensei_id == 37:
        return Ensei(37, 'ensei_name_37.png', 'ensei_area_05.png', datetime.timedelta(hours=2, minutes=45))
    elif ensei_id == 38:
        return Ensei(38, 'ensei_name_38.png', 'ensei_area_05.png', datetime.timedelta(hours=2, minutes=55))
    return ensei_factory(2)
