from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'status', 'priority', 'assignee', 'created_by',
        'due_date', 'is_overdue', 'created_at' 
    )
    list_filter = ('status', 'priority', 'assignee', 'created_at')
    search_fields = ('title', 'description')
    raw_id_fields = ('assignee', 'created_by')
    date_hierarchy = 'due_date'
    readonly_fields = ('created_at', 'updated_at')

    def is_overdue(self, obj):
        return obj.is_overdue()
    is_overdue.boolean = True
    is_overdue.short_description = 'Просрочена?' 
