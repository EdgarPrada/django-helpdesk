"""
django-helpdesk - A Django powered ticket tracker for small enterprise.

(c) Copyright 2008 Jutda. All Rights Reserved. See LICENSE for details.

urls.py - Mapping of URL's to our various views. Note we always used NAMED
          views for simplicity in linking later on.
"""

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from helpdesk.decorators import helpdesk_staff_member_required, protect_view
from helpdesk.views import feeds, staff, public, login
from helpdesk import settings as helpdesk_settings
from helpdesk.views.api import TicketViewSet

if helpdesk_settings.HELPDESK_KB_ENABLED:
    from helpdesk.views import kb

try:
    # TODO: why is it imported? due to some side-effect or by mistake?
    import helpdesk.tasks  # NOQA
except ImportError:
    pass


class DirectTemplateView(TemplateView):
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        if self.extra_context is not None:
            for key, value in self.extra_context.items():
                if callable(value):
                    context[key] = value()
                else:
                    context[key] = value
        return context


app_name = 'helpdesk'

base64_pattern = r'(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'

urlpatterns = [
    url(r'^dashboard/$',
        staff.dashboard,
        name='dashboard'),

    url(r'^tickets/$',
        staff.ticket_list,
        name='list'),

    url(r'^tickets/update/$',
        staff.mass_update,
        name='mass_update'),

    url(r'^tickets/merge$',
        staff.merge_tickets,
        name='merge_tickets'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/$',
        staff.view_ticket,
        name='view'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/followup_edit/(?P<followup_id>[0-9]+)/$',
        staff.followup_edit,
        name='followup_edit'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/followup_delete/(?P<followup_id>[0-9]+)/$',
        staff.followup_delete,
        name='followup_delete'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/edit/$',
        staff.edit_ticket,
        name='edit'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/update/$',
        staff.update_ticket,
        name='update'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/delete/$',
        staff.delete_ticket,
        name='delete'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/hold/$',
        staff.hold_ticket,
        name='hold'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/unhold/$',
        staff.unhold_ticket,
        name='unhold'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/cc/$',
        staff.ticket_cc,
        name='ticket_cc'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/cc/add/$',
        staff.ticket_cc_add,
        name='ticket_cc_add'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/cc/delete/(?P<cc_id>[0-9]+)/$',
        staff.ticket_cc_del,
        name='ticket_cc_del'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/dependency/add/$',
        staff.ticket_dependency_add,
        name='ticket_dependency_add'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/dependency/delete/(?P<dependency_id>[0-9]+)/$',
        staff.ticket_dependency_del,
        name='ticket_dependency_del'),

    url(r'^tickets/(?P<ticket_id>[0-9]+)/attachment_delete/(?P<attachment_id>[0-9]+)/$',
        staff.attachment_del,
        name='attachment_del'),

    url(r'^raw/(?P<type>\w+)/$',
        staff.raw_details,
        name='raw'),

    url(r'^rss/$',
        staff.rss_list,
        name='rss_index'),

    url(r'^reports/$',
        staff.report_index,
        name='report_index'),

    url(r'^reports/(?P<report>\w+)/$',
        staff.run_report,
        name='run_report'),

    url(r'^save_query/$',
        staff.save_query,
        name='savequery'),

    url(r'^delete_query/(?P<id>[0-9]+)/$',
        staff.delete_saved_query,
        name='delete_query'),

    url(r'^settings/$',
        staff.EditUserSettingsView.as_view(),
        name='user_settings'),

    url(r'^ignore/$',
        staff.email_ignore,
        name='email_ignore'),

    url(r'^ignore/add/$',
        staff.email_ignore_add,
        name='email_ignore_add'),

    url(r'^ignore/delete/(?P<id>[0-9]+)/$',
        staff.email_ignore_del,
        name='email_ignore_del'),

    url(r'^datatables_ticket_list/(?P<query>{})$'.format(base64_pattern),
        staff.datatables_ticket_list,
        name="datatables_ticket_list"),

    url(r'^timeline_ticket_list/(?P<query>{})$'.format(base64_pattern),
        staff.timeline_ticket_list,
        name="timeline_ticket_list"),

]

urlpatterns += [
    url(r'^$',
        protect_view(public.Homepage.as_view()),
        name='home'),

    url(r'^tickets/submit/$',
        public.create_ticket,
        name='submit'),

    url(r'^tickets/submit_iframe/$',
        public.CreateTicketIframeView.as_view(),
        name='submit_iframe'),

    url(r'^tickets/success_iframe/$',  # Ticket was submitted successfully
        public.SuccessIframeView.as_view(),
        name='success_iframe'),

    url(r'^view/$',
        public.view_ticket,
        name='public_view'),

    url(r'^change_language/$',
        public.change_language,
        name='public_change_language'),
]

urlpatterns += [
    url(r'^rss/user/(?P<user_name>[^/]+)/$',
        helpdesk_staff_member_required(feeds.OpenTicketsByUser()),
        name='rss_user'),

    url(r'^rss/user/(?P<user_name>[^/]+)/(?P<queue_slug>[A-Za-z0-9_-]+)/$',
        helpdesk_staff_member_required(feeds.OpenTicketsByUser()),
        name='rss_user_queue'),

    url(r'^rss/queue/(?P<queue_slug>[A-Za-z0-9_-]+)/$',
        helpdesk_staff_member_required(feeds.OpenTicketsByQueue()),
        name='rss_queue'),

    url(r'^rss/unassigned/$',
        helpdesk_staff_member_required(feeds.UnassignedTickets()),
        name='rss_unassigned'),

    url(r'^rss/recent_activity/$',
        helpdesk_staff_member_required(feeds.RecentFollowUps()),
        name='rss_activity'),
]


# API
router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')
urlpatterns += [
    url(r'^api/', include(router.urls))
]


urlpatterns += [
    url(r'^login/$',
        login.login,
        name='login'),

    url(r'^logout/$',
        auth_views.LogoutView.as_view(
            template_name='helpdesk/registration/login.html',
            next_page='../'),
        name='logout'),

    url(r'^password_change/$',
        auth_views.PasswordChangeView.as_view(
            template_name='helpdesk/registration/change_password.html',
            success_url='./done'),
        name='password_change'),

    url(r'^password_change/done$',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='helpdesk/registration/change_password_done.html',),
        name='password_change_done'),
]

if helpdesk_settings.HELPDESK_KB_ENABLED:
    urlpatterns += [
        url(r'^kb/$',
            kb.index,
            name='kb_index'),

        url(r'^kb/(?P<slug>[A-Za-z0-9_-]+)/$',
            kb.category,
            name='kb_category'),

        url(r'^kb/(?P<item>[0-9]+)/vote/$',
            kb.vote,
            name='kb_vote'),

        url(r'^kb_iframe/(?P<slug>[A-Za-z0-9_-]+)/$',
            kb.category_iframe,
            name='kb_category_iframe'),
    ]

urlpatterns += [
    url(r'^help/context/$',
        TemplateView.as_view(template_name='helpdesk/help_context.html'),
        name='help_context'),

    url(r'^system_settings/$',
        login_required(DirectTemplateView.as_view(template_name='helpdesk/system_settings.html')),
        name='system_settings'),
]
