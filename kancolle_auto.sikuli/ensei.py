# Ensei (expedition) task list.

import datetime

class Ensei:
    def __init__(self, ensei_id, name_pict, area_pict, duration):
        self.id = ensei_id
        self.name_pict = name_pict
        self.area_pict = area_pict
        self.duration = duration

    def start(self):
        self.begin_time = datetime.datetime.now()

    def end_time(self):
        if hasattr(self, "begin_time"):
            return self.begin_time + self.duration
        return datetime.datetime.max

    def is_end(self):
        if hasattr(self, "begin_time"):
            return self.end_time() < datetime.datetime.now()
        return False

    def __str__(self):
        return 'ensei id = ' + str(self.id) + ', end time = ' + str(self.end_time())

    def __nonzero__(self):
        return self.is_end()

def ensei_factory(ensei_id):
    if ensei_id == 1: return Ensei(1, 'ensei_name_01.png', 'ensei_area_01.png', datetime.timedelta(minutes = 15)) 
    if ensei_id == 2: return Ensei(2, 'ensei_name_02.png', 'ensei_area_01.png', datetime.timedelta(minutes = 30))
    if ensei_id == 3: return Ensei(3, 'ensei_name_03.png', 'ensei_area_01.png', datetime.timedelta(minutes = 20))
    if ensei_id == 4: return Ensei(4, 'ensei_name_04.png', 'ensei_area_01.png', datetime.timedelta(minutes = 50))
    if ensei_id == 5: return Ensei(5, 'ensei_name_05.png', 'ensei_area_01.png', datetime.timedelta(minutes = 90))
    if ensei_id == 6: return Ensei(6, 'ensei_name_06.png', 'ensei_area_01.png', datetime.timedelta(minutes = 40))

    return ensei_factory(2)
              
