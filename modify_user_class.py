from django.contrib.auth.models import User
from django.db import models

def tracker_code_summary(self):
    """ will this work? """
    
    # get the codes for this user, if we're not the superuser
    if self.is_superuser:
        return ''
    
    output = ['<ul>']
    for g in self.tracker_groups.all():
        output.append('<li>' + g.code + '</li>')
    output.append('</ul>')
    
    return ''.join(output)
tracker_code_summary.short_description = "Tracker Codes"
tracker_code_summary.allow_tags = True
    

def modify_user_class():
    """ add an organization to the built in User """
    """ to avoid creating an "organization" class """
    
    models.CharField(max_length=128, editable=True).contribute_to_class(User, "organization")
    User.tracker_code_summary = tracker_code_summary
    
    User._meta.list_display = ('username', 'first_name', 'last_name', 'organization', 'tracker_code_summary', 'is_staff')
    User._meta.ordering = ('organization', 'last_name', 'first_name', 'username')
    
modify_user_class()