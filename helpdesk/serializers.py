from rest_framework import serializers
from django.contrib.humanize.templatetags import humanize

from .models import Ticket
from .lib import format_time_spent


class DatatablesTicketSerializer(serializers.ModelSerializer):
    """
    A serializer for the Ticket model, returns data in the format as required by
    datatables for ticket_list.html. Called from staff.datatables_ticket_list.
    """
    ticket = serializers.SerializerMethodField()
    assigned_to = serializers.SerializerMethodField()
    submitter = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    due_date = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    row_class = serializers.SerializerMethodField()
    time_spent = serializers.SerializerMethodField()
    queue = serializers.SerializerMethodField()
    kbitem = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        # fields = '__all__'
        fields = ('ticket', 'id', 'priority', 'title', 'queue', 'status',
                  'created', 'due_date', 'assigned_to', 'submitter', 'row_class',
                  'time_spent', 'kbitem')

    def get_queue(self, obj):
        return {"title": obj.queue.title, "id": obj.queue.id}

    def get_ticket(self, obj):
        return str(obj.id) + " " + obj.ticket

    def get_status(self, obj):
        return obj.get_status

    def get_created(self, obj):
        return humanize.naturaltime(obj.created)

    def get_due_date(self, obj):
        return humanize.naturaltime(obj.due_date)

    def get_assigned_to(self, obj):
        if obj.assigned_to:
            if obj.assigned_to.get_full_name():
                return obj.assigned_to.get_full_name()
            elif obj.assigned_to.email:
                return obj.assigned_to.email
            else:
                return obj.assigned_to.username
        else:
            return "None"

    def get_submitter(self, obj):
        return obj.submitter_email

    def get_time_spent(self, obj):
        return format_time_spent(obj.time_spent)

    def get_row_class(self, obj):
        return obj.get_priority_css_class

    def get_kbitem(self, obj):
        return obj.kbitem.title if obj.kbitem else ""


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            'id', 'queue', 'title', 'description', 'resolution', 'submitter_email', 'assigned_to', 'status', 'on_hold',
            'priority', 'due_date', 'last_escalation', 'merged_to'
        )
