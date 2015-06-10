from django.contrib import admin
from models import TrackerGroup

# class WorkspaceAdmin(admin.ModelAdmin):
#     # list_display = ('full_title', 'active', 'begin_date', 'end_date')
#     list_display = ('organization', 'code', 'name', 'active', 'begin_date', 'end_date')
#     list_filter = ( 'active', )

admin.site.register(TrackerGroup)
# admin.site.register(ContributorRecord)
