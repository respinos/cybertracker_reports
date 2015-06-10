# -*- coding: utf-8 -*-

from django.db import models
# from jsonfield import JSONField
from nosj.fields import JSONField
from linesfield import LinesField

from django.contrib.auth.models import User
import datetime
import dateutil.parser

import sys
from django.db.models import signals
from django.dispatch import dispatcher

from django.db import connection

import csv
import pprint

# SORTED_MAP = {
#   'Annelids' : 1,
#   'Mollusks' : 2,
#   'Insects' : 3,
#   'Arachnids' : 4,
#   'Myriapods': 5,
#   'Crustaceans' : 6,
#   'Bird' : 7,
#   'Mammal' : 8,
#   'Amphibian' : 9,
#   'Reptile' : 10,
#   'Fish' : 11,
#   'Unknown' : 999
# }

SORTED_MAP = {
    'Bird' : 1,
    'Mammal' : 2,
    'Reptile' : 3,
    'Amphibian' : 4,
    'Fish' : 5,
    'Annelids' : 6,
    'Mollusks' : 7,
    'Insects' : 8,
    'Arachnids' : 9,
    'Myriapods': 10,
    'Crustaceans' : 11,
    'Unknown' : 999
}


ICON_MAP = {
  'Mollusks' : '/images/0legs.gif',
  'Annelids' : '/images/0legsEarthworm.gif',
  'Insects' : '/images/6legs.gif',
  'Arachnids' : '/images/8legs.gif',
  'Myriapods' : '/images/10legs.gif',
  'Crustaceans' : '/images/10legsPillbug.gif',
  'Bird' : '/images/birds.gif',
  'Mammal' : '/images/mammals.gif',
  'Amphibian' : '/images/amphibs.gif',
  'Reptile' : '/images/reptiles.gif',
  'Fish' : '/images/fish.gif',
  'Unknown' : '/images/blank.gif'
}

SEQUENCE_CHOICES = (
    ('S456', 'Sequence 4/5/6'),
    ('S4', 'Sequence 4'),
    ('S5', 'Sequence 5'),
    ('S6', 'Sequence 6'),
)

class TrackerGroup(models.Model):
    code = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=255)
    sequence = models.CharField(max_length=32, choices=SEQUENCE_CHOICES)
    
    users = models.ManyToManyField(User, related_name='tracker_groups', blank=True, null=True)
    
    class Admin:
        ordering = ('code', 'name')
    
    class Meta:
        ordering = ['code', 'name']
    
    def __unicode__(self):
        return "%s: %s" % ( self.code, self.name )
        
    @classmethod
    def assign(self, user, sequence, number_classes):
        """ assign codes to the user based on the sequence """

        # given a sequence, assign number_classes
        # this is only going to be for increasing/adding
        
        name = "%s (%s)" % (user.organization, user.last_name)
        groups = []
        
        if sequence == 'S5':
            base_code = '5'
        elif sequence == 'S4':
            base_code = '4'
        elif sequence == 'S456':
            base_code = '2'
        elif sequence == 'S6':
            base_code = '6'
            
        check = user.tracker_groups.filter(sequence=sequence)
        start = 1
        if len(check) and len(check) < number_classes:
            # adding classes
            number_needed = number_classes - len(check)
            base_code = check[len(check) - 1].code[0:3]
            start = len(check) + 1
        else:
            number_needed = number_classes
            cursor = connection.cursor()
            cursor.execute('''SELECT MAX(code) FROM %s WHERE sequence = %%s AND substr(code, 1, 1) = %%s ''' % self._meta.db_table, [sequence, base_code])
            result = cursor.fetchone()
            if result[0]:
                base_code = result[0][0:3]
            else:
                base_code = base_code + '00'
            # and now add 10
            base_code = str(int(base_code) + 1)
        print >>sys.stderr, "BASE CODE", base_code, "/", start
        
        for idx in range(start, number_needed + start):
            print >>sys.stderr, base_code, "/", idx
            group = self(code="%s%d" % (base_code, idx), name=name, sequence=sequence)
            group.save()
            group.users.add(user)
            user.message_set.create(message=unicode(group) + " set up")
            
    
class S5Record(models.Model):
    location = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)
    date = models.CharField(max_length=255, blank=True, null=True)
    uploaded_on = models.DateTimeField(blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    animal_group = models.CharField(max_length=255, blank=True, null=True)
    weight = models.IntegerField(default=0)
    animal = models.CharField(max_length=255, blank=True, null=True)
    how_many = models.IntegerField(default=0)
    how_exact = models.CharField(max_length=255, blank=True, null=True)
    how_observed = LinesField(blank=True, null=True)
    what_observed = LinesField(blank=True, null=True)
    where_observed = LinesField(blank=True, null=True)
    behavior_observed = LinesField(blank=True, null=True)
    raw = JSONField(blank=True, null=True)
    
    group = models.ForeignKey(TrackerGroup, db_column='group_code')
    
    def __unicode__(self):
        return "<S5: %s> %s" % ( self.name, self.time )
    
    def save(self):
        self.weight = SORTED_MAP.get(self.animal_group, 999)
        super(S5Record, self).save()
        
    def group_icon(self):
        return ICON_MAP.get(self.animal_group, ICON_MAP['Unknown'])
        
    def timestamp(self):
        return dateutil.parser.parse(self.date + " " + self.time)
        
    # put the processing code here in the model
    @classmethod
    def process_csv(self, input_file):
        sequence = self.sequence_key()
        data = []
        
        keys = None
        reader = csv.reader(input_file)
        keys = reader.next()
        
        for row in reader:
            sequence_index = 0
            raw = []
            datum = {'what_observed':[], 'where_observed':[], 'how_observed':[], 'behavior_observed':[], 'identification':{}, 'sequence':'S456'}
            
            # use enumerate on the row?
            for index, value in enumerate(row):
                raw.append(value)
                if not keys[index:]:
                    continue
                
                try:
                    seq = sequence[sequence_index]
                except:
                    seq = None
                sequence_index += 1
                
                if seq is None or not seq[1:]:
                    print >>sys.stderr, "SKIPPING:", keys[index].strip(), "/", sequence_index
                    continue
                    
                key = seq[1]
                
                if not value.strip():
                    if key == 'location':
                        datum['location'] = 'Zone ?'
                    continue
                
                if not datum.has_key(key):
                    datum[key] = value.strip()
                    
                elif isinstance(datum[key], list):
                    datum[key].append(keys[index].strip())
                    
                elif isinstance(datum[key], dict):
                    datum[key][seq[0]] = value.strip()
                else:
                    datum[key] = value.strip()
                    
            if len(datum['group_code']) == 3:
                datum['group_code'] = '0' + datum['group_code']
            
            datum['raw'] = raw
            data.append(datum)
            
        return data

    @classmethod
    def process_datum(self, datum):
        record = {}
        record['uploaded_on'] = datetime.datetime.now()
        record['animal'] = 'Unknown'
        
        for key in datum.keys():
            if key == 'date':
                record['date'] = dateutil.parser.parse(datum['date']).strftime("%Y-%m-%d")
            elif key == 'time':
                record['time'] = dateutil.parser.parse(datum['time']).strftime("%H:%M:%S")
            elif key == 'identification':
                group = datum['animal_group']
                if group == 'Mammal':
                    record['animal'] = datum['identification']["Mammals EZ-MI"]
                elif group == "Bird":
                    record['animal'] = datum['identification']["Birds EZ-MI"]
                elif group == "Amphibian":
                    record['animal'] = datum['identification']["Amphibians EZ-MI"]
                elif group == "Reptile":
                    record['animal'] = datum['identification']["Reptiles EZ-MI"]
                elif group == "Fish":
                    record['animal'] = datum['identification']["Fish EZ-MI"]
                elif group == "Myriapods":
                    record['animal'] = datum['identification']["Myriapods EZ-MI"]
                elif group == "Crustaceans":
                    record['animal'] = datum['identification']["Crustaceans EZ-MI"]
                elif group == "Mollusks":
                    record['animal'] = datum['identification']["Mollusks EZ MI"]
                elif group == "Annelids":
                    record['animal'] = datum['identification']["Annelids EZ MI"]
                elif group == "Arachnids":
                    record['animal'] = datum['identification']["Arachnids EZ-MI"]
                else:
                    record['animal'] = datum['identification'][group]
                    if datum['identification'].has_key(record['animal']):
                        record['animal'] = datum['identification'][record['animal']]
                    
            else:
                record[key] = datum[key]
        
        # return a S1Record
        del record['group_code']
        del record['sequence']
        return self(**record)
        # return record
        
    @classmethod
    def sequence_key(self):
        elements = [
         ['Date', 'date'],
         ['Time', 'time'],
         ['BioKIDS ID S5', 'group_code'],
         ['Zone', 'location'],
         ['Name', 'name'],
         ['See', 'how_observed'],
         ['Hear', 'how_observed'],
         ['Smell', 'how_observed'],
         ['Live animal', 'what_observed'],
         ['Track', 'what_observed'],
         ['Carcass', 'what_observed'],
         ['Scat', 'what_observed'],
         ['Sign', 'what_observed'],
         ['Animal Group', 'animal_group'],
         ['Annelids EZ MI', 'identification'],
         ['Mollusks EZ MI', 'identification'],
         ['Insects', 'identification'],
         ['Ant, Bee, or Wasp...', 'identification'],
         ['Cricket, Katydid, or Grasshopper...', '?'],
         ['Fly or mosquito...', 'identification'],
         ['Beetles...', 'identification'],
         ['Butterfly or Moth...', 'identification'],
         ['Aphid or other True bug...', 'identification'],
         ['Damselfly or Dragonfly...', 'identification'],
         ['Other insect...', 'identification'],
         ['Arachnids EZ-MI', 'identification'],
         ['Spiders - Araneae', 'identification'],
         ['Myriapods EZ-MI', 'identification'],
         ['Crustaceans EZ-MI', 'identification'],
         ['Microhabitats'],
         ['Bare ground', 'where_observed'],
         ['In water', 'where_observed'],
         ['Bushes', 'where_observed'],
         ['Under something', 'where_observed'],
         ['In the soil', 'where_observed'],
         ['Short grass', 'where_observed'],
         ['Tall grass', 'where_observed'],
         ['Leaf litter or mulch', 'where_observed'],
         ['In the air', 'where_observed'],
         ['Single tree', 'where_observed'],
         ['Trees together', 'where_observed'],
         ['Near water', 'where_observed'],
         ['Behavior'],
         ['Fighting', 'behavior_observed'],
         ['Feeding', 'behavior_observed'],
         ['Drinking', 'behavior_observed'],
         ['Resting or sleeping', 'behavior_observed'],
         ['Courting', 'behavior_observed'],
         ['Moving', 'behavior_observed'],
         ['Signaling', 'behavior_observed'],
         ['Building', 'behavior_observed'],
         ['Grooming', 'behavior_observed'],
         ['Other', 'behavior_observed'],
         ['Invertebrates', 'identification'],
         ['Birds EZ-MI', 'identification'],
         ['Mammals EZ-MI', 'identification'],
         ['Amphibians EZ-MI', 'identification'],
         ['Reptiles EZ-MI', 'identification'],
         ['Fish EZ-MI', 'identification'],
         ['How many?', 'how_many'],
         ['Exact/Estimate', 'how_exact'],
        ]
        return elements
    
class S4Record(models.Model):
    location = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)
    date = models.CharField(max_length=255, blank=True, null=True)
    uploaded_on = models.DateTimeField(blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    animal_group = models.CharField(max_length=255, blank=True, null=True)
    plant_group = models.CharField(max_length=255, blank=True, null=True)
    weight = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    what_eating = LinesField(blank=True, null=True)
    how_much_grass = models.CharField(max_length=255, blank=True, null=True)
    raw = JSONField(blank=True, null=True)

    group = models.ForeignKey(TrackerGroup)

    def __unicode__(self):
        return "<S4: %s> %s" % ( self.name, self.time )
        
    def is_animal(self):
        return True if self.animal_group else False
        
    def is_plant(self):
        return True if self.plant_group else False
    
    def save(self):
        self.weight = SORTED_MAP.get(self.animal_group, 999)
        super(S4Record, self).save()
        
    def group_icon(self):
        return ICON_MAP.get(self.animal_group, ICON_MAP['Unknown'])
        
    def timestamp(self):
        return dateutil.parser.parse(self.date + " " + self.time)
        
    # put the processing code here in the model
    @classmethod
    def process_csv(self, input_file):
        """
        It's either PLANT OR ANIMAL, NOT BOTH.
        """
        
        sequence = self.sequence_key()
        data = []
        
        keys = None
        reader = csv.reader(input_file)
        keys = reader.next()
        for row in reader:
            sequence_index = 0
            raw = []
            datum = {'sequence':'S4'}
            
            # use enumerate on the row?
            for index, value in enumerate(row):
                raw.append(value)
                if not keys[index:]:
                    continue
                
                try:
                    seq = sequence[sequence_index]
                except:
                    seq = None
                sequence_index += 1
                
                if seq is None or not seq[1:]:
                    print >>sys.stderr, "SKIPPING:", keys[index].strip(), "/", sequence_index
                    continue
                    
                key = seq[1]
                
                if not value.strip():
                    if key == 'location':
                        datum['location'] = 'Zone ?'
                    continue
                
                if not datum.has_key(key):
                    datum[key] = value.strip()
                    
                elif isinstance(datum[key], list):
                    datum[key].append(keys[index].strip())
                    
                elif isinstance(datum[key], dict):
                    datum[key][seq[0]] = value.strip()
                else:
                    datum[key] = value.strip()
                    
            if len(datum['group_code']) == 3:
                datum['group_code'] = '0' + datum['group_code']
            
            datum['raw'] = raw
            data.append(datum)
            
        return data

    @classmethod
    def process_datum(self, datum):
        record = {}
        record['uploaded_on'] = datetime.datetime.now()
        
        for key in datum.keys():
            if key == 'date':
                record['date'] = dateutil.parser.parse(datum['date']).strftime("%Y-%m-%d")
            elif key == 'time':
                record['time'] = dateutil.parser.parse(datum['time']).strftime("%H:%M:%S")
            else:
                record[key] = datum[key]
                
        # return a S4Record
        del record['group_code']
        del record['sequence']
        return self(**record)
        # return record
        
        # "Date","Time","BioKIDS ID","Name","Zone","Animal Group","How many?","What is it eating?","What kind of plant is it? (herbaceous)","How much grass?"

    @classmethod
    def sequence_key(self):
        elements = [
          ['Date','date'],
          ['Time','time'],
          ['BioKIDS ID S4','group_code'],
          ['Name','name'],
          ['Zone','location'],
          ['Animal Group','animal_group'],
          ['How many?','quantity'],
          ['What is it eating?', 'what_eating'],
          ['What kind of plant is it? (herbaceous)', 'plant_group'],
          ['How much grass?', 'how_much_grass'],
        ]
        return elements

class S456Record(models.Model):
    location = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)
    date = models.CharField(max_length=255, blank=True, null=True)
    uploaded_on = models.DateTimeField(blank=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    animal_group = models.CharField(max_length=255, blank=True, null=True)
    plant_group = models.CharField(max_length=255, blank=True, null=True)
    weight = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    animal = models.CharField(max_length=255, blank=True, null=True)
    how_many = models.IntegerField(default=0)
    how_exact = models.CharField(max_length=255, blank=True, null=True)
    how_observed = LinesField(blank=True, null=True)
    what_observed = LinesField(blank=True, null=True)
    where_observed = LinesField(blank=True, null=True)
    behavior_observed = LinesField(blank=True, null=True)
    what_eating = LinesField(blank=True, null=True)
    how_much_grass = models.CharField(max_length=255, blank=True, null=True)
    energy_role = models.CharField(max_length=255, blank=True, null=True)
    consumer_type = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    raw = JSONField(blank=True, null=True)
    
    guid = models.CharField(max_length=36, blank=True, null=True)

    group = models.ForeignKey(TrackerGroup, db_column='group_code')

    def __unicode__(self):
        return "<S456: %s> %s" % ( self.name, self.time )

    def is_animal(self):
        return True if self.animal_group else False

    def is_plant(self):
        return True if self.plant_group else False

    def save(self):
        self.weight = SORTED_MAP.get(self.animal_group, 999)
        super(S456Record, self).save()

    def group_icon(self):
        return ICON_MAP.get(self.animal_group, ICON_MAP['Unknown'])

    def timestamp(self):
        return dateutil.parser.parse(self.date + " " + self.time)

    # put the processing code here in the model
    @classmethod
    def process_csv(self, input_file):
        """
        It's either PLANT OR ANIMAL, NOT BOTH.
        """

        sequence = self.sequence_key()
        data = []

        keys = None
        reader = csv.reader(input_file)
        keys = reader.next()

        for row in reader:
            print >>sys.stderr, row
            sequence_index = 0
            raw = []
            datum = {'what_observed':[], 'where_observed':[], 'how_observed':[], 'behavior_observed':[], 'identification':{}, 'sequence':'S456'}

            # use enumerate on the row?
            for index, value in enumerate(row):
                raw.append(value)
                if not keys[index:]:
                    print >>sys.stderr, "SKIPPING COLUMN:", index, "/", keys[index:]
                    continue

                try:
                    seq = sequence[sequence_index]
                except:
                    seq = None
                sequence_index += 1

                if seq is None or not seq[1:]:
                    print >>sys.stderr, "SKIPPING:", keys[index].strip(), "/", sequence_index, ":", seq
                    continue

                key = seq[1]
                
                value = value.replace(". . .", "...").replace(" ...", "...")
                print >>sys.stderr, seq[0], ">", key, ":", value

                if not value.strip():
                    if key == 'location':
                        datum['location'] = 'Zone ?'
                    continue

                if not datum.has_key(key):
                    datum[key] = value.strip()

                elif isinstance(datum[key], list):
                    # datum[key].append(keys[index].strip())
                    datum[key].append(seq[0])

                elif isinstance(datum[key], dict):
                    datum[key][seq[0]] = value.strip()
                else:
                    datum[key] = value.strip()

            if not datum.has_key('group_code'):
                datum['group_code'] = '0000'
            
            elif len(datum['group_code']) == 3:
                datum['group_code'] = '0' + datum['group_code']

            datum['raw'] = raw
            data.append(datum)

        return data

    @classmethod
    def process_datum(self, datum):
        record = {}
        record['uploaded_on'] = datetime.datetime.now()
        record['animal'] = 'Unknown'
        record['notes'] = datum.get('notes', '')
        # record['plant'] = 'Unknown'

        is_plant = False

        for key in datum.keys():
            if key == 'date':
                record['date'] = dateutil.parser.parse(datum['date']).strftime("%Y-%m-%d")
            elif key == 'time':
                record['time'] = dateutil.parser.parse(datum['time']).strftime("%H:%M:%S")
            elif key == 'identification':
                if is_plant:
                    # a plant
                    # we don't have to look further, because the column
                    # is pointless...
                    ## record['plant'] = datum['identification'][group]

                    pass
                else:
                    # an animal
                    group = datum['animal_group']
                    if group == 'Mammal':
                        group = "Mammals EZ-MI"
                    elif group == "Bird":
                        group = "Birds EZ-MI"
                    elif group == "Amphibian":
                        group = "Amphibians EZ-MI"
                    elif group == "Reptile":
                        grou = "Reptiles EZ-MI"
                    elif group == "Fish":
                        group = "Fish EZ-MI"
                    elif group == "Myriapods":
                        group = "Myriapods EZ-MI"
                    elif group == "Crustaceans":
                        group = "Crustaceans EZ-MI"
                    elif group == "Mollusks":
                        group = "Mollusks EZ MI"
                    elif group == "Annelids":
                        group = "Annelids EZ MI"
                    elif group == "Arachnids":
                        group = "Arachnids EZ-MI"
                        
                    if datum['identification'].has_key(group):
                        import pprint
                        pprint.pprint(datum['identification'], stream=sys.stderr)
                        record['animal'] = datum['identification'][group]
                        if datum['identification'].has_key(record['animal']):
                            record['animal'] = datum['identification'][record['animal']]

            else:
                record[key] = datum[key]
                if key == 'what_observed' and "Plant" in record[key]:
                    is_plant = True

        # return a S1Record
        del record['group_code']
        del record['sequence']
        
        if record.get('guid', None):
            self.objects.filter(guid=record['guid']).delete()
        
        return self(**record)
        # return record


    @classmethod
    def sequence_key(self):
        elements = [
         ['Date', 'date'],
         ['Time', 'time'],
         ['BioKIDS ID S456', 'group_code'],
         ['Zone', 'location'],
         ['Name', 'name'],
         ['See', 'how_observed'],
         ['Hear', 'how_observed'],
         ['Smell', 'how_observed'],
         ['Plant', 'what_observed'],
         ['Live animal', 'what_observed'],
         ['Track', 'what_observed'],
         # ['Carcass', 'what_observed'],
         # ['Scat', 'what_observed'],
         ['Sign', 'what_observed'],
         ['Animal Group', 'animal_group'],
         ['Annelids EZ MI', 'identification'],
         ['Mollusks EZ MI', 'identification'],
         ['Insects', 'identification'],
         ['Ants; Bees; or Wasps...', 'identification'],
         ['Cricket; Katydid; or Grasshopper...', 'identification'],
         ['Fly or Mosquito...', 'identification'],
         ['Beetle...', 'identification'],
         ['Butterfly or moth...', 'identification'],
         ['Aphid or other True Bug...', 'identification'],
         ['Damselfly or Dragonfly...', 'identification'],
         ['Other insect...', 'identification'],
         ['Arachnids EZ-MI', 'identification'],
         ['Spiders...', 'identification'],
         ['Myriapods EZ-MI', 'identification'],
         ['Crustaceans EZ-MI', 'identification'],
         ['Microhabitats'],
         ['Bare ground', 'where_observed'],
         ['In water', 'where_observed'],
         ['Bushes', 'where_observed'],
         ['Under something', 'where_observed'],
         ['In the soil', 'where_observed'],
         ['Short grass', 'where_observed'],
         ['Tall grass', 'where_observed'],
         ['Leaf litter or mulch', 'where_observed'],
         ['In the air', 'where_observed'],
         ['Single tree', 'where_observed'],
         ['Trees together', 'where_observed'],
         ['Near water', 'where_observed'],
         ['Behavior'],
         ['Fighting', 'behavior_observed'],
         ['Feeding', 'behavior_observed'],
         ['Drinking', 'behavior_observed'],
         ['Resting or sleeping', 'behavior_observed'],
         ['Courting', 'behavior_observed'],
         ['Moving', 'behavior_observed'],
         ['Signaling', 'behavior_observed'],
         ['Building', 'behavior_observed'],
         ['Grooming', 'behavior_observed'],
         ['Other', 'behavior_observed'],
         ['What is it eating?', 'what_eating'],
         ['Invertebrates', 'identification'],
         ['Birds EZ-MI', 'identification'],
         ['Mammals EZ-MI', 'identification'],
         ['Amphibians EZ-MI', 'identification'],
         ['Reptiles EZ-MI', 'identification'],
         ['Fish EZ-MI', 'identification'],
         ['How many?', 'how_many'],
         ['Exact/Estimate', 'how_exact'],
         ['What kind of plant?', 'plant_group'],
         ['Grass', 'identification'],
         ['How much grass?', 'how_much_grass'],
         ['Shrub or bush', 'identification'],
         ['Vine', 'identification'],
         ['Weeds; herbs; or other small plants', 'identification'],
         ['Tree', 'identification'],
         ['What energy role?', 'energy_role'],
         ['What type of consumer is it?', 'consumer_type'],
        ]
        return elements