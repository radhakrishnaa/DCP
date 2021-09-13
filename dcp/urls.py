from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
#from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic import RedirectView

from django.contrib import admin

from dcp.startup import override_django_cas
from api import views

override_django_cas()

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # The root redirects to the UI
    #url(r'^$', redirect_to, {'url': '/ui'}),

    url(r'^$', RedirectView.as_view(url='/ui')),
    # The UI route is the main user interface. It serves up a single
    # view, and all the rendering logic is in client-side AngularJS.
    #url(r'^ui/$', redirect_to, {'url': '/ui'}),
    url(r'^ui/$', RedirectView.as_view(url='/ui')),
    url(r'^ui$', login_required(views.ui)),

    # CAS Authentication
    url(r'^accounts/login/$', 'django_cas.views.login'),
    url(r'^accounts/logout/$', 'django_cas.views.logout'),

    # The RESTful API used by the AngularJS UI
    url(r'^api/', include('api.urls')),
)

# TODO: Look into serving up the Angular client through Django
# itself rather than as static files.
urlpatterns += patterns('django.contrib.staticfiles.views',
    url(r'^static/(?P<path>.*)$', 'serve'),
)

