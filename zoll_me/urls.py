'''
James D. Zoll

1/20/2013

Purpose: Defines URL rules for the project.

License: This is a public work.

'''

# Library Imports
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^scarf/', include('scarf.urls')),
    url(r'^rss/', include('rss.urls')),
    url(r'^files/', include('files.urls')),
    url(r'^xbmc_photos/', include('xbmc_photos.urls')),
    url(r'^leapday/', include('leapday.urls')),
    url(r'^lensoftruth/', include('lensoftruth.urls')),
    url(r'^dk_optimize/', include('dk_optimize.urls')),
    url(r'^$', 'zoll_me.views.index'),
    url(r'^resume/$', 'zoll_me.views.resume'),
    url(r'^projects/$', 'zoll_me.views.projects'),
    url(r'^account/login/$','django.contrib.auth.views.login', {'template_name': 'zoll_me/account/login.html'}, name="zoll_me-login"),
    url(r'^account/logout/$','django.contrib.auth.views.logout', {'template_name': 'zoll_me/account/logged_out.html'}),
    url(r'^account/password_change/$','django.contrib.auth.views.password_change', {'template_name': 'zoll_me/account/password_change.html'}),
    url(r'^account/password_change_done/$','django.contrib.auth.views.password_change_done', {'template_name': 'zoll_me/account/password_change_done.html'}),
    url(r'^account/password_reset/$','django.contrib.auth.views.password_reset', {'template_name': 'zoll_me/account/password_reset.html', 'email_template_name': 'zoll_me/account/password_reset_email.txt', 'subject_template_name':'zoll_me/account/password_reset_subject.txt'}),
    url(r'^account/password_reset_done/$','django.contrib.auth.views.password_reset_done', {'template_name': 'zoll_me/account/password_reset_done.html'}),
    url(r'^account/password_reset_complete/$','django.contrib.auth.views.password_reset_complete', {'template_name': 'zoll_me/account/password_reset_complete.html'}),
    url(r'^account/password_reset_confirm/(?P<uidb36>\d+)/(?P<token>[\d\w-]+)$','django.contrib.auth.views.password_reset_confirm', {'template_name': 'zoll_me/account/password_reset_confirm.html'})
)

# When we're in DEBUG mode, I want to be able to access some
# resources that aren't accessible directly in production. These URLconfs
# are added to make that possible.
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^400/$', 'zoll_me.views.error_400'),
        url(r'^403/$', 'zoll_me.views.error_403'),
        url(r'^404/$', 'zoll_me.views.error_404'),
        url(r'^500/$', 'zoll_me.views.error_500'),
   )
    
# Define error handling views.
handler403 = 'zoll_me.views.error_403'
handler404 = 'zoll_me.views.error_404'
handler500 = 'zoll_me.views.error_500'