""" utility scripts """

import pprint
import copy
import sys

def test1(self, filename):
    from models import S4Record

    print "-- reading:", filename
    f = open(filename)
    
    data = S4Record.process_csv(f)
    for datum in data:
        del datum['raw']
        pprint.pprint(datum)
    
    print "#", len(data)
    print "-30-"

def test2A(self):
    from models import TrackerGroup
    
    g = TrackerGroup(code='9999', name='Test Group')
    g.save()
    
    print g
    
def test2B(self, filename):
    from models import S4Record, TrackerGroup

    print "-- reading:", filename
    f = open(filename, 'U')

    data = S4Record.process_csv(f)
    print "#", len(data)
        
    for datum in data:
        tmp = copy.deepcopy(datum)
        del tmp['raw']
        pprint.pprint(tmp)
        
        try:
            g = TrackerGroup.objects.get(code=datum['group_code'])
        except:
            print "--", datum['group_code'], "DOES NOT EXIST"
            continue
            
        record = S4Record.process_datum(datum)
        record.group = g
        print record
        record.save()
        
    print "-30-"

def test2C(self, id):
    from models import S4Record, TrackerGroup
    
    try:
        record = S4Record.objects.get(id=id)
    except:
        print "-- could not find", id
        sys.exit()
        
    print record.where_observed
    
def test3(self, sequence):
    import modify_user_class
    from models import TrackerGroup
    from django.contrib.auth.models import User
    
    user = User.objects.get(id=3)
    print user.organization
    
    TrackerGroup.assign(user, sequence, 5)
    