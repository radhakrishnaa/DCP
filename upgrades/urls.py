from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

from django.contrib import admin
import views
from settingsviews import defaultpollinginterval


from startup import override_django_cas

override_django_cas()

admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # The root redirects to the UI
    url(r'^$', RedirectView.as_view(url='/upgrades')),
    # The UI route is the main user interface. It serves up a single
    # view, and all the rendering logic is in client-side AngularJS.
    url(r'^upgrades/$', RedirectView.as_view(url='/upgrades')),
    url(r'^upgrades$', login_required(views.upgradesui)),

    # CAS Authentication
    url(r'^accounts/login/$', 'django_cas.views.login'),
    url(r'^accounts/logout/$', 'django_cas.views.logout'),

    # The Controller RESTful API around Upgrade Management RESTful service behind Indigo
    url(r'^umcontroller/$', login_required(views.umcontroller_list)),
    url(r'^umcontroller/(?P<pk>[0-9a-z-]+).*$', login_required(views.umcontroller_get)),

    # The Controller RESTful API around User service provided by Django
    url(r'^usercontroller/$', login_required(views.getCurrentUser)),
    
    # The Controller RESTful API to get version string of portal
    url(r'^version/$', views.getVersion),
    
    # The Controller RESTful API around UpgradePathStatus service provided by Django
    url(r'^deviceevents/$', login_required(views.deviceevents)),
    url(r'^savepath/$', login_required(views.savepath)),
    url(r'^nextaction/$', login_required(views.um_post_next_action)),
    url(r'^publishupgradepath/$', login_required(views.um_publish_upgradePath)),
    url(r'^deletepathandpackage/$', login_required(views.deletepathandpackage)),

    # The Controller RESTful API around UpgradePathStatus service provided by Django
    url(r'^uploadbinary/$', login_required(views.uploadbinary)),
    
    # The Controller RESTful API around auto path creation from a delta-ota package
    url(r'^getpackagefromjenkins/$', login_required(views.getpackagefromjenkins)),
    url(r'^getpackagewithoutxmlfromjenkins/$', login_required(views.getpackagewithoutxmlfromjenkins)),
    url(r'^getxmlfromjenkins/$', login_required(views.getxmlfromjenkins)),
    url(r'^autojenkins/$', views.autojenkins),

    # Device list requests
    url(r'^tlmslists/$', login_required(views.tlmslists)),
    url(r'^tlmsremove/(?P<pk>[0-9a-z-]+).*$', login_required(views.tlmsremove)),
    url(r'^tlmsclearlistentries/$', login_required(views.tlmsclearlistentries)),
    url(r'^tlmstargets/$', login_required(views.tlmstargets)),
    url(r'^tlmsaddlist/$', login_required(views.tlmsaddlist)),
    url(r'^tlmsupdatetarget/$', login_required(views.tlmsupdatetarget)),
    url(r'^tlmsuploadlist/$', login_required(views.tlmsuploadlist)),
    url(r'^tlmsdownloadlist/$', login_required(views.tlmsdownloadlist)),
    url(r'^tlmsmatch/(?P<pk>[0-9a-zA-Z-]+).*$', login_required(views.tlmsmatch)),
    url(r'^tlmslistsize/$', login_required(views.tlmslistsize)),
    url(r'^tlmscheckeligibility/$', login_required(views.tlmscheckeligibility)),

    # Upgrade Stats and Timeline
    url(r'^stats/guid/(?P<pk>[0-9a-zA-Z-]+).*$', login_required(views.stats)),

    # Published Path Retrieval
    url(r'^publishedpath/(?P<pk>[0-9a-zA-Z-]+).*$', login_required(views.publishedpath)),
    url(r'^diffrunning/$', login_required(views.diffrunning)),

    # get default polling interval
    url(r'^defaultpollinginterval/$', login_required(defaultpollinginterval)),
    
    
    
    #get list of eligible device
    url(r'^getdeviceeligibleforupgrade/$', login_required(views.getdeviceeligibleforupgrade)),
    
    
    
   
)

# TODO: Look into serving up the Angular client through Django
# itself rather than as static files.
urlpatterns += patterns('django.contrib.staticfiles.views',
    url(r'^static/(?P<path>.*)$', 'serve'),
)

