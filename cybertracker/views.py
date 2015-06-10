from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
import datetime

from django.template import RequestContext, loader
from models import TrackerGroup, S5Record, S4Record, S456Record

from django.contrib.auth.decorators import login_required

import cybertracker_reports.settings
import mako.template
from mako.lookup import TemplateLookup

from StringIO import StringIO
import csv
import sys
import time

from http_auth import http_auth

mako_loader = TemplateLookup(directories=cybertracker_reports.settings.TEMPLATE_DIRS, module_directory='/tmp/mako_modules')

SEQUENCES = {
   'S4' : S4Record,
   'S5' : S5Record,
   'S456' : S456Record,
}

def index(request, message=None):
    
    user = request.user
    groups = get_groups(user)
    
    has_s5 = False
    has_s4 = False
    
    now = time.localtime()
    if request.REQUEST.get('start', None):
        start = request.REQUEST['start']
        end = request.REQUEST['end']
    elif 'start' in request.session:
        start = request.session['start']
        end = request.session['end']
    else:
        if now[1] >= 9 and now[1] <= 12:
            start = "%d-09-01" % now[0]
            end = "%d-12-31" % now[0]
        elif now[1] >= 1 and now[1] <= 6:
            start = "%d-01-01" % now[0]
            end = "%d-06-30" % now[0]
        else:
            start = "%d-07-01" % now[0]
            end = "%d-08-31" % now[0]
            
    if [ g for g in groups if g.sequence == 'S5' or g.sequence == 'S456' ]:
        has_s5 = True

    if [ g for g in groups if g.sequence == 'S4' or g.sequence == 'S456' ]:
        has_s4 = True
    
    
    t = loader.get_template("cybertracker/index.html")
    c = RequestContext(request, {'next':'/cybertracker/', 'groups':groups, 'group_code':request.session.get('group_code', None), 'number_groups':len(groups), 'has_s4':has_s4, 'has_s5':has_s5, 'start':start, 'end':end, 'now':time.strftime("%Y-%m-%d")})

    return HttpResponse(t.render(c))
    
@login_required
def recycle(request):
    user = request.user
    if not user.is_superuser:
        user.message_set.create(message="You are not authorized to delete data.")
        
    if request.method == 'POST' and request.POST.get('group_code', None):
        # which sequence is this? HAH!
        group_code = request.POST['group_code']
        S5Record.objects.filter(group__code=group_code).delete()
        S4Record.objects.filter(group__code=group_code).delete()
        S456Record.objects.filter(group__code=group_code).delete()
        user.message_set.create(message="Observation records deleted for Group " + group_code + ".")
        
    return HttpResponseRedirect("/cybertracker/")

##########################################################################
# UPLOADS
##########################################################################

def _process_upload(uploaded_data, user, groups, group_code=''):
    allowed_codes = [ g.code for g in groups ]
    
    num_entries = 0
    num_skipped = 0
    
    for datum in uploaded_data:
        if datum.has_key('group_code'):
            if group_code:
                datum['group_code'] = group_code
            elif not datum['group_code'] in allowed_codes:
                num_skipped += 1
                continue
    
            group = [ g for g in groups if g.code == datum['group_code'] ][0]
            record = SEQUENCES[datum['sequence']].process_datum(datum)
            record.group = group
            record.save()
            num_entries += 1
            
        else:
            num_skipped += 1
        
    return (num_entries, num_skipped)
    
@login_required
def process_upload(request):
    user = request.user
    groups = get_groups(user)
    
    group_code = request.GET.get('group_code', '')
    
    uploaded_data = request.session['uploaded_data']
    
    num_entries, num_skipped = _process_upload(uploaded_data, user, groups, group_code)
    
    del request.session['uploaded_data']
    
    t = loader.get_template("cybertracker/process_upload.html")
    c = RequestContext(request, {'num_skipped':num_skipped, 'num_entries':num_entries})
    
    return HttpResponse(t.render(c))
    
    
@login_required
def verify_upload(request):
    user = request.user
    groups = get_groups(user)
    
    uploaded_groups = []
    uploaded_data = None
    if request.method == 'GET' and "uploaded_data" in request.session:
        uploaded_data = request.session['uploaded_data']
    elif request.method == 'POST' and 'datafile' in request.FILES:
        uploaded_data = process_csv(StringIO(request.FILES['datafile']['content']))
        
    if not uploaded_data:
        # should have a message
        user.message_set.create(message="Did you upload a file?")
        return HttpResponseRedirect("/cybertracker/")
    
    uploaded_sequence = None
    for datum in uploaded_data:
        if datum.has_key('group_code') and not datum['group_code'] in uploaded_groups:
            uploaded_groups.append(datum['group_code'])
        uploaded_sequence = datum['sequence']
            
    request.session['uploaded_data'] = uploaded_data
    
    # if there's only one group in the data and user has access
    # to that data, go directly to process
    if len(uploaded_groups) == 1:
        if [ g.code for g in groups if g.code == uploaded_groups[0] ]:
            return HttpResponseRedirect("/cybertracker/process_upload/?group_code=%s" % uploaded_groups[0])
            
    # fill put uploaded_groups
    has_errors = False
    for index, group_code in enumerate(uploaded_groups):
        try:
            g = TrackerGroup.objects.get(code=group_code)
            has_access = g in groups
            uploaded_groups[index] = dict(code=g.code, sequence=g.sequence, name=g.name, is_valid=True, has_access=has_access)
            if g.sequence != uploaded_sequence:
                uploaded_groups[index]['wrong_sequence'] = True
            if not has_access: has_errors = True
        except:
            uploaded_groups[index] = dict(code=group_code, is_valid=False)
            has_errors = True
            
    print >>sys.stderr, "--", uploaded_groups
    
    t = loader.get_template("cybertracker/verify_upload.html")
    c = RequestContext(request, {'uploaded_groups':uploaded_groups, 'groups':groups, 'has_errors':has_errors, 'uploaded_sequence':uploaded_sequence})

    return HttpResponse(t.render(c))
    
def _upload_error(request, groups, message, uploaded_groups=None):
    t = loader.get_template("cybertracker/500.html")
    c = RequestContext(request, {'groups':groups, 'message':message, 'uploaded_groups':uploaded_groups})
    return HttpResponseServerError(t.render(c))
    
@http_auth
def upload(request):
    user = request.user
    groups = get_groups(user)

    fh = open("/tmp/" + user.username + "-" + str(time.time()) + ".txt", "w")
    print >>fh, "UPLOADING DATA:", user.username
    print >>fh, request.raw_post_data
    
    indata = StringIO(request.raw_post_data)
    
    try:
        uploaded_data = csv.DictReader(indata)
    except Exception, e:
        print >>fh, str(e)
        return _upload_error(request, groups, "Could not process upload data")

    # turn into a simple list
    uploaded_data = [ datum for datum in uploaded_data ]

    uploaded_groups = []
            
    uploaded_sequence = None
    for datum in uploaded_data:
        datum["sequence"] = "S456"
        if datum.has_key('group_code') and not datum['group_code'] in uploaded_groups:
            uploaded_groups.append(datum['group_code'])
        uploaded_sequence = datum['sequence']
        
    if not uploaded_groups:
        print >>fh, "YOU MUST SUPPLY A GROUP CODE"
        return _upload_error(request, groups, "You must supply a group code in your observations.")
    print >>fh, "UPLOADED GROUPS =", uploaded_groups
        
    # fill put uploaded_groups
    has_errors = False
    for index, group_code in enumerate(uploaded_groups):
        if group_code == '1': continue
        try:
            g = TrackerGroup.objects.get(code=group_code)
            has_access = g in groups
            uploaded_groups[index] = dict(code=g.code, sequence=g.sequence, name=g.name, is_valid=True, has_access=has_access)
            if g.sequence != uploaded_sequence:
                uploaded_groups[index]['wrong_sequence'] = True
            if not has_access: has_errors = True
        except Exception, e:
            uploaded_groups[index] = dict(code=group_code, is_valid=False,
                    error=str(e))
            has_errors = True
            
    print >>sys.stderr, "--", uploaded_groups
    if has_errors:
        print >>fh, "YOU CANNOT UPLOAD TO THESE GROUPS", uploaded_groups
        return _upload_error(requeset, groups, "You cannot uploaded to these groups.", uploaded_groups)
    
    num_entries, num_skipped = _process_upload(uploaded_data, user, groups)

    fh.close()

    t = loader.get_template("cybertracker/process_upload.html")
    c = RequestContext(request, {'num_skipped':num_skipped, 'num_entries':num_entries})
    return HttpResponse(t.render(c))
    
def process_csv(input_file):
    """ 
    Inspect the first line of the input file, and call the 
    appropriate processor.
    """
    
    keys = None
    # header row
    reader = csv.reader(input_file)
    keys = reader.next()
    input_file.seek(0)
    if "BioKIDS ID S456" in keys:
        # S456 sequence
        print >>sys.stderr, "S456 SEQUENCE!!"
        return S456Record.process_csv(input_file)
    elif "BioKIDS ID S5" in keys:
        # S5 sequence
        print >>sys.stderr, "S5 SEQUENCE!!"
        return S5Record.process_csv(input_file)
    elif "BioKIDS ID S4":
        # S4 sequence
        print >>sys.stderr, "S4 SEQUENCE!!"
        return S4Record.process_csv(input_file)
    
    return []
    
    
##########################################################################
# REPORTS
##########################################################################
    
@login_required
def choose_report(request):
    user = request.user
    report_name = request.GET.get('report_name', None)
    group_code = request.GET.get('group_code', None)
    if not report_name:
        user.message_set.create(message="Please select a report.")
        return index(request, message='Please select a report.')
    elif not group_code or group_code == '-':
        user.message_set.create(message="Please select a group.")
        return index(request, message='Please select a group.')
        
    redirect_to = "/cybertracker/" + report_name + "/" + group_code + "/"
    if request.REQUEST.get('start', None):
        redirect_to += "?start=" + request.REQUEST['start'] + "&end=" + request.REQUEST['end']
        request.session['start'] = request.REQUEST['start']
        request.session['end'] = request.REQUEST['end']
        request.session['group_code'] = group_code
    return HttpResponseRedirect(redirect_to)

@login_required
def habitat_report(request, group_code):
    
    group = TrackerGroup.objects.get(code=group_code)
    
    start = request.REQUEST.get('start','1969-01-01')
    end = request.REQUEST.get('end','2031-12-39')
        
    records = list(S5Record.objects.filter(group__code=group_code,date__gte=start,date__lte=end).order_by('date', 'time')) + \
        list(S456Record.objects.filter(group__code=group_code,date__gte=start,date__lte=end).exclude(animal_group='').order_by('date', 'time'))
        
    records.sort(lambda a, b: cmp(a.date + a.time, b.date + b.time))
    
    report = {}
    habitat_summary = {}
    critters_seen = {}
    groups_seen = {}
    
    habitats_observed = {}
    
    data = []
    
    if "sort_by" in request.GET:
        sort_by = request.GET['sort_by'].split(",")
    else:
        sort_by = [ "where_observed" ]
    if sort_by == [ "animal_group" ]:
        sort_by = [ "weight" ]
    elif sort_by == [ "name" ]:
        sort_by = []
        
    skipped = 0
    datum = {}
    for record in records:
        location = record.location
        how_many = record.how_many
        animal = record.animal
        animal_group = record.animal_group
        name = record.name
        
        if not name:
            name = "Unknown"
        
        weight = record.weight
        
        if record.name == "Test":
            continue
            
        if not record.where_observed:
            skipped += 1
            continue
            
        for wh in record.where_observed:
            habitats_observed[wh] = 1
            key = wh + ":" + animal
            if not key in datum:
                datum[key] = { 'animal' : animal, 'animal_group' : animal_group, 'weight' : weight, 'total_tally' : 0, 'location' : [], 'where_observed' : wh, 'animal_group_icon':record.group_icon() }
            
            if how_many is None: how_many = 0
            
            datum[key]['total_tally'] = datum[key]['total_tally'] + how_many
            
            if not wh in habitat_summary:
                habitat_summary[wh] = dict(total_animals=how_many, distinct_animals=0, distinct_groups=0)
            else:
                habitat_summary[wh]['total_animals'] += how_many
                
            if not wh in critters_seen:
                critters_seen[wh] = {}
            
            if not animal in critters_seen[wh]:
                critters_seen[wh][animal] = 1
                habitat_summary[wh]['distinct_animals'] += 1
                
            if not wh in groups_seen:
                groups_seen[wh] = {}
            
            if not animal_group in groups_seen[wh]:
                groups_seen[wh][animal_group] = 1
                habitat_summary[wh]['distinct_groups'] += 1
                
            if not location in datum[key]['location']:
                datum[key]['location'].append(location)
                datum[key]['location'].sort()
                
    for key in datum.keys():
        data.append(datum[key])
        
    sort_by.append('animal')
    data.sort(lambda a, b: cmp(mergekeys(a, sort_by), mergekeys(b, sort_by)))

    summary = dict(total_animals=0, distinct_animals=0, distinct_groups=0)
    for key in habitat_summary.keys():
        for attr in [ 'total_animals', 'distinct_animals', 'distinct_groups']:
            if attr == 'total_animals' or attr == 'distinct_groups':
                summary[attr] += habitat_summary[key][attr]
            elif attr == 'distinct_animals':
                summary[attr] = max(summary[attr], habitat_summary[key][attr])
                
    summary['distinct_animals'] = len(data)
    summary['number_records'] = len(records)
    summary['start'] = summary['end'] = None
    if records:
        summary['start'] = records[0].timestamp()
        summary['end'] = records[len(records) - 1].timestamp()
    
    m = mako_loader.get_template("cybertracker/_habitat_report.mao")
    kwargs = dict(group_code=group_code, skipped=skipped, summary=summary, data=data, habitat_summary=habitat_summary, sort_by=request.GET.get("sort_by", "where_observed"), base_path=request.base_path)

    ## print >>sys.stderr, "invoking mako..."
    c = RequestContext(request)
    c['body'] = m.render(**kwargs)
    c['title'] = 'Habitat Summary'
    c['group_code'] = group_code
    c['group'] = group
    ##print >>sys.stderr, "...back from mako"
    t = loader.get_template("cybertracker/report.html")
    return HttpResponse(t.render(c))
    
@login_required
def zone_report(request, group_code):

    group = TrackerGroup.objects.get(code=group_code)

    start = request.REQUEST.get('start','1969-01-01')
    end = request.REQUEST.get('end','2031-12-39')
        
    # records = S5Record.objects.filter(group__code=group_code).order_by('date', 'time')
    records = list(S5Record.objects.filter(group__code=group_code,date__gte=start,date__lte=end).order_by('date', 'time')) + \
        list(S456Record.objects.filter(group__code=group_code,date__gte=start,date__lte=end).exclude(animal_group='').order_by('date', 'time'))
        
    records.sort(lambda a, b: cmp(a.date + a.time, b.date + b.time))

    report = {}
    zone_summary = {}
    critters_seen = {}
    groups_seen = {}

    if "sort_by" in request.GET:
        sort_by = request.GET['sort_by'].split(",")
    else:
        sort_by = [ "weight" ]

    skipped = 0
    for record in records:

        location = record.location
        how_many = record.how_many
        animal = record.animal
        animal_group = record.animal_group

        weight = record.weight

        if record.name == "Test":
            continue
            
        if not animal in report:
            report[animal] = dict(animal=animal, animal_group=animal_group, animal_group_icon=record.group_icon(), weight=weight, total_tally=0, where_observed=[])
            
        if not location in report[animal]:
            report[animal][location] = 0
            
        if how_many is None: how_many = 0
        
        report[animal][location] = report[animal][location] + how_many
        report[animal]['total_tally'] += how_many
        
        if record.where_observed:
            for v in record.where_observed:
                if not v in report[animal]['where_observed']:
                    report[animal]['where_observed'].append(v)
            report[animal]['where_observed'].sort()
        
        if not location in zone_summary:
            zone_summary[location] = dict(total_animals=how_many, distinct_animals=0, distinct_groups=0)
            
        if not location in critters_seen:
            critters_seen[location] = {}
            
        if not animal in critters_seen[location]:
            critters_seen[location][animal] = 1
            zone_summary[location]['distinct_animals'] += 1
            
        if not location in groups_seen:
            groups_seen[location] = {}
            
        if not animal_group in groups_seen[location]:
            groups_seen[location][animal_group] = 1
            zone_summary[location]['distinct_groups'] += 1


    data = []
    for key in report.keys():
        data.append(report[key])

    last_item = 'Z' * 100
    sort_by.append('animal')
    data.sort(lambda a, b: cmp(mergekeys(a, sort_by), mergekeys(b, sort_by)))

    summary = dict(total_animals=0, distinct_animals=0, distinct_groups=0)
    for key in zone_summary.keys():
        for attr in [ 'total_animals', 'distinct_animals', 'distinct_groups']:
            if attr == 'total_animals' or attr == 'distinct_groups':
                summary[attr] += zone_summary[key][attr]
            elif attr == 'distinct_animals':
                summary[attr] = max(summary[attr], zone_summary[key][attr])

    summary['distinct_animals'] = len(data)
    summary['number_records'] = len(records)
    summary['start'] = summary['end'] = None
    if records:
        summary['start'] = records[0].timestamp()
        summary['end'] = records[len(records) - 1].timestamp()

    m = mako_loader.get_template("cybertracker/_zone_report.mao")
    kwargs = dict(group_code=group_code, summary=summary, data=data, zone_summary=zone_summary, sort_by=request.GET.get("sort_by", "weight"), base_path=request.base_path)

    ## print >>sys.stderr, "invoking mako..."
    c = RequestContext(request)
    c['body'] = m.render(**kwargs)
    c['title'] = 'Zone Report'
    c['group_code'] = group_code
    c['group'] = group
    ##print >>sys.stderr, "...back from mako"
    t = loader.get_template("cybertracker/report.html")
    return HttpResponse(t.render(c))    

@login_required
def observation_report(request, group_code):

    group = TrackerGroup.objects.get(code=group_code)

    start = request.REQUEST.get('start','1969-01-01')
    end = request.REQUEST.get('end','2031-12-39')
        
    # records = S5Record.objects.filter(group__code=group_code).order_by('date', 'time')
    records = list(S5Record.objects.filter(group__code=group_code,date__gte=start,date__lte=end).order_by('date', 'time')) + \
        list(S456Record.objects.filter(group__code=group_code,date__gte=start,date__lte=end).order_by('date', 'time'))
        
    records.sort(lambda a, b: cmp(a.date + a.time, b.date + b.time))

    report = {}
    zone_summary = {}
    critters_seen = {}
    groups_seen = {}

    habitats_observed = {}

    data = []

    if "sort_by" in request.GET:
        sort_by = request.GET['sort_by'].split(",")
    else:
        sort_by = [ "datetime", "name" ]
    if sort_by == [ "group" ]:
        sort_by = [ "weight" ]
    elif sort_by == [ "group", "name" ]:
        sort_by = []

    skipped = 0
    for record in records:
        datum = {}
        location = record.location
        how_many = record.how_many
        if record.animal_group:
            observed = record.animal
            group = record.animal_group
            is_animal = True
            weight = record.weight
        else:
            group = 'Plant'
            observed = record.plant_group
            is_animal = False
            weight = 99999
            
        name = record.name
        if not name:
            name = "Unknown"


        if record.name == "Test":
            continue
            
        datum = { 'is_animal':is_animal, 'observed' : observed, 'group' : group, 'group_icon':record.group_icon(), 'weight' : weight, 'how_many' : record.how_many, 'how_exact' : record.how_exact, 'where_observed' : [], 'behavior_observed' : [], 'what_observed' : [], 'how_observed' : [], 'date' : None, 'time' : None}
        
        datum['name'] = name
        datum['location'] = location
        datum['datetime'] = record.timestamp()

        for attr in [ 'where_observed', 'how_observed', 'what_observed', 'behavior_observed' ]:
            if getattr(record, attr):
                for v in getattr(record, attr):
                    if not v in datum[attr]:
                        datum[attr].append(v)
                        datum[attr].sort()
            

        data.append(datum)

    sort_by.append('observed')
    data.sort(lambda a, b: cmp(mergekeys(a, sort_by), mergekeys(b, sort_by)))

    summary = {}
    summary['number_records'] = len(records)
    summary['start'] = summary['end'] = None
    if records:
        summary['start'] = records[0].timestamp()
        summary['end'] = records[len(records) - 1].timestamp()

    m = mako_loader.get_template("cybertracker/_observation_report.mao")
    kwargs = dict(group_code=group_code, summary=summary, data=data, sort_by=request.GET.get("sort_by", "datetime,name"), base_path=request.base_path)

    ## print >>sys.stderr, "invoking mako..."
    c = RequestContext(request)
    c['body'] = m.render(**kwargs)
    c['title'] = 'Observation Report'
    c['group_code'] = group_code
    c['group'] = group
    ##print >>sys.stderr, "...back from mako"
    t = loader.get_template("cybertracker/report.html")
    return HttpResponse(t.render(c))


@login_required
def team_report(request, group_code):
    """
    The Team Report groups by zone and name.
    
    Each "team" report consists of a animal and plant summary.
    """

    group = TrackerGroup.objects.get(code=group_code)

    start = request.REQUEST.get('start','1969-01-01')
    end = request.REQUEST.get('end','2031-12-39')
        
    # records = S4Record.objects.filter(group__code=group_code).order_by('date', 'time')
    records = list(S4Record.objects.filter(group__code=group_code,date__gte=start,date__lte=end).order_by('date', 'time')) + \
        list(S456Record.objects.filter(group__code=group_code,date__gte=start,date__lte=end).order_by('date', 'time'))
        
    records.sort(lambda a, b: cmp(a.date + a.time, b.date + b.time))
    
    report = {}
    team_totals = {}
    data = []

    if "sort_by" in request.GET:
        sort_by = request.GET['sort_by'].split(",")
    else:
        sort_by = [ "weight" ] # not quantity
    if sort_by == [ "animal_group" ]:
        sort_by = [ "weight" ]
        
    plants_sort_by = ["plant_group"]

    skipped = 0
    
    teams = []
    
    for record in records:

        location = record.location
        name = record.name
        
        quantity = record.quantity
        if quantity == 0:
            try:
                quantity = record.how_many
            except:
                pass
        
        # if there are no name/location here, then skip
        if not name or not location:
            skipped += 1
            continue
            
        if name == "Test":
            continue
            
        if not (location, name) in report:
            report[(location, name)] = {'animals':{}, 'plants':{}, 'total_animals':0, 'total_plants':0}
            team_totals[(location, name)] = {'animals':0, 'plants':0}
            teams.append((location, name))
            
        animals_table = report[(location, name)]['animals']
        plants_table = report[(location, name)]['plants']
                
        # tally animal groups
        if record.is_animal():
            key = (record.weight, record.animal_group)
            if not record.animal_group in animals_table:
                animals_table[record.animal_group] = {'quantity':0, 'what_eating':[]}
                animals_table[record.animal_group]['animal_group'] = record.animal_group
                animals_table[record.animal_group]['weight'] = record.weight
                animals_table[record.animal_group]['animal_group_icon'] = record.group_icon()

            animals_table[record.animal_group]['quantity'] += quantity
            if record.what_eating:
                for w in record.what_eating:
                    if not w in animals_table[record.animal_group]['what_eating']:
                        animals_table[record.animal_group]['what_eating'].append(w)
                        animals_table[record.animal_group]['what_eating'].sort()

            report[(location, name)]['total_animals'] += quantity

        elif record.is_plant():
            key = record.plant_group
            if not key in plants_table:
                plants_table[key] = {'plant_group':'', 'quantity':0, 'how_much_grass':''}
            plants_table[key]['plant_group'] = key
            if key == 'Grass':
                plants_table[key]['how_much_grass'] = record.how_much_grass
                plants_table[key]['quantity'] = 999
            else:
                plants_table[key]['quantity'] += quantity
                report[(location, name)]['total_plants'] += quantity

            
    teams.sort()
    
    # then you need to sort the individual report tables
    for team in teams:
        data = []
        for key in report[team]['animals'].keys():
            data.append(report[team]['animals'][key])
        data.sort(lambda a, b: cmp(mergekeys(a, sort_by), mergekeys(b, sort_by)))
        report[team]['animals'] = data

        data = []
        for key in report[team]['plants'].keys():
            data.append(report[team]['plants'][key])
        data.sort(lambda a, b: cmp(mergekeys(a, plants_sort_by), mergekeys(b, plants_sort_by)))
        report[team]['plants'] = data

    summary = dict(total_animals=0, total_plants=0, distinct_animals=0, distinct_groups=0)
    # summary['distinct_animals'] = len(data)
    summary['number_records'] = len(records)
    summary['start'] = summary['end'] = None
    if records:
        summary['start'] = records[0].timestamp()
        summary['end'] = records[len(records) - 1].timestamp()

    m = mako_loader.get_template("cybertracker/_team_report.mao")
    kwargs = dict(group=group, group_code=group_code, report=report, summary=summary, teams=teams, sort_by=request.GET.get("sort_by", "how_many"), base_path=request.base_path)

    ## print >>sys.stderr, "invoking mako..."
    c = RequestContext(request)
    c['body'] = m.render(**kwargs)
    c['title'] = 'Team Report'
    c['group_code'] = group_code
    c['group'] = group
    ##print >>sys.stderr, "...back from mako"
    t = loader.get_template("cybertracker/report.html")
    return HttpResponse(t.render(c))    

@login_required
def energy_role_report(request, group_code):

    group = TrackerGroup.objects.get(code=group_code)

    start = request.REQUEST.get('start','1969-01-01')
    end = request.REQUEST.get('end','2031-12-39')

    # records = S5Record.objects.filter(group__code=group_code).order_by('date', 'time')
    records = list(S5Record.objects.filter(group__code=group_code,date__gte=start,date__lte=end).order_by('date', 'time')) + \
        list(S456Record.objects.filter(group__code=group_code,date__gte=start,date__lte=end).order_by('date', 'time'))

    records.sort(lambda a, b: cmp(a.date + a.time, b.date + b.time))

    report = {}
    energy_roles = {}

    data = []

    if "sort_by" in request.GET:
        sort_by = request.GET['sort_by'].split(",")
    else:
        sort_by = [ "group" ]
    if sort_by == [ "group" ]:
        sort_by = [ "weight" ]
    elif sort_by == [ "group", "name" ]:
        sort_by = []

    skipped = 0
    for record in records:
        datum = {}
        location = record.location
        how_many = record.how_many
        observed = None
        if record.animal_group:
            observed = record.animal
            group = record.animal_group
            is_animal = True
            weight = record.weight
        else:
            group = 'Plant'
            observed = record.plant_group
            is_animal = False
            weight = 99999


        if record.name == "Test":
            continue

        try:
            energy_role = record.energy_role
        except:
            energy_role = None

        if not energy_role:
            skipped += 1
            continue
        elif energy_role == 'Consumer':
            energy_role = record.consumer_type

        key = (observed, energy_role)
        if not energy_roles.has_key(key):
            energy_roles[key] = { 'how_much_grass':None, 'is_animal':is_animal, 'observed' : observed, 'group' : group, 'group_icon':record.group_icon(), 'weight' : weight, 'energy_role':energy_role, 'total_tally':0, 'what_eating':[]}
        datum = energy_roles[key]

        for attr in [ 'what_eating' ]:
            if getattr(record, attr):
                for v in getattr(record, attr):
                    if not v in datum[attr]:
                        datum[attr].append(v)
                        datum[attr].sort()

        if getattr(record, 'how_many'):
            datum['total_tally'] += record.how_many
            
        if getattr(record, 'how_much_grass'):
            datum['how_much_grass'] = record.how_much_grass

    data = energy_roles.values()
    sort_by.append('observed')
    data.sort(lambda a, b: cmp(mergekeys(a, sort_by), mergekeys(b, sort_by)))

    summary = {}
    summary['number_records'] = len(records)
    summary['start'] = summary['end'] = None
    if records:
        summary['start'] = records[0].timestamp()
        summary['end'] = records[len(records) - 1].timestamp()
        
    total = 0
    for datum in data:
        total += datum['total_tally']

    m = mako_loader.get_template("cybertracker/_energy_role_report.mao")
    kwargs = dict(total=total, group_code=group_code, summary=summary, data=data, sort_by=request.GET.get("sort_by", "datetime,name"), skipped=skipped, base_path=request.base_path)

    ## print >>sys.stderr, "invoking mako..."
    c = RequestContext(request)
    c['body'] = m.render(**kwargs)
    c['title'] = 'Schoolyard Energy Role Report'
    c['group_code'] = group_code
    c['group'] = group
    ##print >>sys.stderr, "...back from mako"
    t = loader.get_template("cybertracker/report.html")
    return HttpResponse(t.render(c))

    
def get_groups(user):
    groups = []
    if user.is_authenticated():
        if user.is_superuser or user.username == 'guest':
            # get everything
            groups = TrackerGroup.objects.all().order_by('code', 'name')
        else:
            groups = user.tracker_groups.all()
    
    return groups
    
def mergekeys(d, keys):
    r = []
    for k in keys:
        v = 0
        if d.has_key(k):
            v = d[k]
        if isinstance(v, int):
            v = "%6d" % v
        r.append(v)
    return r
