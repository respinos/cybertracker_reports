from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponseRedirect

import datetime

from cybertracker_reports.biokids.models import *
from cybertracker.models import TrackerGroup

from django.template import RequestContext, loader
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User

def manage_user(request, id):
    
    change_user = User.objects.get(id=id)

    if request.method == 'POST':
        # do something
        change_user.first_name = request.POST['first_name']
        change_user.last_name = request.POST['last_name']
        change_user.organization = request.POST['organization']
        change_user.email = request.POST['email']
        change_user.save()
        
        request.user.message_set.create(message="Changed saved.")
        
        if request.POST['sequence'] and request.POST.get('number_classes', None):
            sequence = request.POST['sequence']
            number_classes = int(request.POST['number_classes'])
            TrackerGroup.assign(change_user, sequence, number_classes)
        
        redirect_to = "/admin/auth/user/"
        if "_continue" in request.POST:
            redirect_to = "/admin/auth/user/%s/" % id
        elif "_addanother" in request.POST:
            redirect_to = "/admin/auth/user/add/"
        
        return HttpResponseRedirect(redirect_to)
        

    t = loader.get_template("admin/auth/user/edit_form.html")
    c = RequestContext(request, dict(
        change_user=change_user, opts=User._meta,
        tracker_groups=change_user.tracker_groups.all(),
        change=True, add=False,
        is_popup=False,
        has_add_permission=True,
        has_delete_permission=True,
        has_change_permission=True,
        save_as=False
    ))

    return HttpResponse(t.render(c))
