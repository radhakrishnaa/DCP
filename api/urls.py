from django.conf.urls import patterns, include, url

from api import views

urlpatterns = patterns('',
    url(r'^api-auth', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^extra_key$', views.ExtraKeyList.as_view()),
    url(r'^extra_key/(?P<pk>[0-9]+)$', views.ExtraKeyDetail.as_view()),

    url(r'^extra_value$', views.ExtraValueList.as_view()),
    url(r'^extra_value/(?P<pk>[0-9]+)$', views.ExtraValueDetail.as_view()),

    url(r'^region$', views.RegionList.as_view()),
    url(r'^region/(?P<pk>[0-9]+)$', views.RegionDetail.as_view()),

    url(r'^carrier$', views.CarrierList.as_view()),
    url(r'^carrier/(?P<pk>[0-9]+)$', views.CarrierDetail.as_view()),

    url(r'^setting_category$', views.SettingCategoryList.as_view()),
    url(r'^setting_category/(?P<pk>[0-9]+)$', views.SettingCategoryDetail.as_view()),

    url(r'^setting_def$', views.SettingDefList.as_view()),
    url(r'^setting_def/(?P<pk>[0-9]+)$', views.SettingDefDetail.as_view()),
    
    url(r'^user$', views.UserList.as_view()),
    url(r'^user/(?P<pk>[0-9]+)$', views.UserInstance.as_view()),
    url(r'^currentuser$', views.CurrentUserInstance.as_view()),
    
    url(r'^hwtype$', views.HwtypeList.as_view()),
    url(r'^hwtype/(?P<pk>[0-9]+)$', views.HwtypeInstance.as_view()),
    
    url(r'^config_set$', views.ConfigSetList.as_view()),
    url(r'^config_set/(?P<pk>[0-9]+)$', views.ConfigSetInstance.as_view()),
    
    url(r'^config_version$', views.ConfigVersionList.as_view()),
    url(r'^config_version/(?P<pk>[0-9]+)$', views.ConfigVersionInstance.as_view()),
    url(r'^config_version/(?P<pk>[0-9]+)/settings$', views.ConfigSettingsInstance.as_view()),
    url(r'^config_version/(?P<pk>[0-9]+)/propagate$', views.ConfigVersionPropagate.as_view()),
    url(r'^config_version/(?P<pk>[0-9]+)/discard$', views.ConfigVersionDiscard.as_view()),
    url(r'^config_version/(?P<pk>[0-9]+)/commit$', views.ConfigVersionCommit.as_view()),
    url(r'^config_version/(?P<pk>[0-9]+)/approve$', views.ConfigVersionApprove.as_view()),
    url(r'^config_version/(?P<pk>[0-9]+)/publish$', views.ConfigVersionPublish.as_view()),
    url(r'^config_version/(?P<pk>[0-9]+)/testpublish$', views.ConfigVersionTestPublish.as_view()),
    url(r'^config_version/(?P<pk>[0-9]+)/revert$', views.ConfigVersionRevert.as_view()),
    
    url(r'^setting_value$', views.SettingValueList.as_view()),
    url(r'^setting_value/(?P<pk>[0-9]+)$', views.SettingValueInstance.as_view()),
    url(r'^env_transform$', views.EnvTransformList.as_view()),
    url(r'^env_transform/(?P<pk>[0-9]+)$', views.EnvTransformInstance.as_view()),
    url(r'^cloud_env$', views.CloudEnvList.as_view()),
    url(r'^cloud_env/(?P<pk>[0-9]+)$', views.CloudEnvInstance.as_view()),
       
    url(r'^cfgreport$', views.ConfigReport.as_view()),    
    url(r'^livequery$', views.ConfigSetQuery.as_view()),    
    url(r'^cfgimport$', views.ImportConfig.as_view()),    
    url(r'^bulkupdate$', views.BulkUpdate.as_view()),
    url(r'^diff$', views.ConfigSetsDiff.as_view()),
    url(r'^unpublished$', views.ConfigSetsUnpublished.as_view()),
    url(r'^diffpublished$', views.ConfigSetDiffPublishedApi.as_view()),
    url(r'^diffapproved$', views.ConfigSetDiffApprovedApi.as_view()),
    url(r'^importDataExplorerSettings', views.DataExplorerImport.as_view()),
    url(r'^discardUnEditedCommits', views.DiscardBulkUpdate.as_view()),
#     url(r'^delta$', views.DeltaList.as_view()),
#     url(r'^delta/(?P<pk>[0-9]+)$', views.DeltaInstance.as_view()),
)

