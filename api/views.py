# Create your views here.

import os

from django.conf import settings as djsettings
from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from api import models
from api import permissions
from api import generics
from api import serializers

def ui(request):
    template = loader.get_template('ui/index.html')
    sourcepath = os.path.join(djsettings.SITEPATH, 'static/ui/index.html')
    context = Context({'sourcepath': sourcepath})
    return HttpResponse(template.render(context))

@api_view(['GET'])
def api_root(request, format=None):
    """
    The entry endpoint of our API.
    """
    return Response({
        'setting_category': reverse('setting_category', request=request),
    })

class ExtraKeyList(generics.DCPortalListCreateAPIView):
    model = models.ExtraKey
    serializer_class = serializers.ExtraKeySerializer
    permissions_classes = (permissions.IsAdminOrReadOnly,)

class ExtraKeyDetail(generics.DCPortalRetrieveUpdateDestroyAPIView):
    model = models.ExtraKey
    serializer_class = serializers.ExtraKeySerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class ExtraValueList(generics.DCPortalListCreateAPIView):
    model = models.ExtraValue
    serializer_class = serializers.ExtraValueSerializer
    permissions_classes = (permissions.IsAdminOrReadOnly,)

class ExtraValueDetail(generics.DCPortalRetrieveUpdateDestroyAPIView):
    model = models.ExtraValue
    serializer_class = serializers.ExtraValueSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class RegionList(generics.DCPortalListCreateAPIView):
    model = models.Region
    serializer_class = serializers.RegionSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class RegionDetail(generics.DCPortalRetrieveUpdateDestroyAPIView):
    model = models.Region
    serializer_class = serializers.RegionSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class CarrierList(generics.DCPortalListCreateAPIView):
    model = models.Carrier
    serializer_class = serializers.CarrierSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class CarrierDetail(generics.DCPortalRetrieveUpdateDestroyAPIView):
    model = models.Carrier
    serializer_class = serializers.CarrierSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class SettingCategoryList(generics.DCPortalListCreateAPIView):
    model = models.SettingCategory
    serializer_class = serializers.SettingCategorySerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class SettingCategoryDetail(generics.DCPortalRetrieveUpdateDestroyAPIView):
    model = models.SettingCategory
    serializer_class = serializers.SettingCategorySerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class SettingDefList(generics.DCPortalListCreateAPIView):
    model = models.SettingDef
    serializer_class = serializers.SettingDefSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class SettingDefDetail(generics.DCPortalRetrieveUpdateDestroyAPIView):
    model = models.SettingDef
    serializer_class = serializers.SettingDefSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class UserList(generics.DCPortalListCreateAPIView):
    model = models.User
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsUserAdminOrReadOnly,)

class UserInstance(generics.DCPortalRetrieveUpdateDestroyAPIView):
    model = models.User
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsUserAdminOrReadOnly,)
    
class CurrentUserInstance(generics.CurrentUserRetrieveAPIView):
    model = models.User
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsUserAdminOrReadOnly,)
    
class HwtypeList(generics.DCPortalListCreateAPIView):
    model = models.Hwtype
    serializer_class = serializers.HwtypeSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class HwtypeInstance(generics.DCPortalRetrieveUpdateDestroyAPIView):
    model = models.Hwtype
    serializer_class = serializers.HwtypeSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)
    
class ConfigSetList(generics.ConfigSetListCreateAPIView):
    model = models.ConfigSet
    serializer_class = serializers.ConfigSetSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class ConfigSetInstance(generics.DCPortalRetrieveUpdateDestroyAPIView):
    model = models.ConfigSet
    serializer_class = serializers.ConfigSetSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)
    
class ConfigVersionList(generics.DCPortalListCreateAPIView):
    model = models.ConfigVersion
    serializer_class = serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class ConfigVersionInstance(generics.DCPortalRetrieveUpdateDestroyAPIView):
    model = models.ConfigVersion
    serializer_class = serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class ConfigSettingsInstance(generics.ConfigSettingsRetrieveUpdateAPIView):
    model = models.ConfigVersion
    serializer_class = serializers.ConfigSettingsSerializer
    permission_classes = (permissions.IsEditorOrReadOnly,)

class SettingValueList(generics.DCPortalListCreateAPIView):
    model = models.SettingValue
    serializer_class = serializers.SettingValueSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class SettingValueInstance(generics.DCPortalRetrieveUpdateDestroyAPIView):
    model = models.SettingValue
    serializer_class = serializers.SettingValueSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class EnvTransformList(generics.DCPortalListCreateAPIView):
    model = models.EnvTransform
    serializer_class = serializers.EnvTransformSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class EnvTransformInstance(generics.DCPortalRetrieveUpdateDestroyAPIView):
    model = models.EnvTransform
    serializer_class = serializers.EnvTransformSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class CloudEnvList(generics.DCPortalListCreateAPIView):
    model = models.CloudEnv
    serializer_class = serializers.CloudEnvSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class CloudEnvInstance(generics.DCPortalRetrieveUpdateDestroyAPIView):
    model = models.CloudEnv
    serializer_class = serializers.CloudEnvSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class ConfigVersionPropagate(generics.ConfigVersionPropagateAPIView):
    model = models.ConfigVersion
    serializer_class = serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)           

class ConfigVersionDiscard(generics.ConfigVersionDiscardAPIView):
    model = models.ConfigVersion
    serializer_class = serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsEditorOrReadOnly,)           

class ConfigVersionCommit(generics.ConfigVersionCommitAPIView):
    model = models.ConfigVersion
    serializer_class = serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsEditorOrReadOnly,)           

class ConfigVersionApprove(generics.ConfigVersionApproveAPIView):
    model = models.ConfigVersion
    serializer_class = serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsApproverOrReadOnly,)           

class ConfigVersionPublish(generics.ConfigVersionPublishAPIView):
    model = models.ConfigVersion
    serializer_class = serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsPublisherOrReadOnly,)           

class ConfigVersionTestPublish(generics.ConfigVersionTestPublishAPIView):
    model = models.ConfigVersion
    serializer_class = serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsEditorOrReadOnly,)           

# TODO: This does not use the fact that it is based on the ConfigSet model.
# We should consider removing "model" and "serializer_class" below.
class ConfigReport(generics.ConfigReportAPIView):
    model = models.ConfigSet
    serializer_class = serializers.ConfigSetSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class ConfigSetQuery(generics.ConfigSetQueryAPIView):
    model = models.ConfigSet
    serializer_class = serializers.ConfigSetSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

# TODO: Should this not use the REST view class since
#       it does not correspond to a specific table?
class ImportConfig(generics.ConfigzipImportAPIView):
    model = models.ConfigSet
    serializer_class = serializers.ConfigSetSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class ConfigVersionRevert(generics.ConfigVersionRevertAPIView):
    model = models.ConfigVersion
    serializer_class = serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsPublisherOrReadOnly,)

class BulkUpdate(generics.ConfigVersionBulkUpdateAPIView):
    model = models.ConfigSet
    serializer_class = serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)

class ConfigSetsDiff(generics.ConfigSetDiffApiView):
    model = models.ConfigSet
    serializer_class = serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsEditorOrReadOnly,)
    
class ConfigSetsUnpublished(generics.ConfigSetUnpublishedApiView):
    model = models.ConfigSet
    serializer_class = serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsEditorOrReadOnly,)
    
class ConfigSetDiffPublishedApi(generics.ConfigSetDiffPublishedApiView):
    model = models.ConfigSet
    serializer_class = serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsEditorOrReadOnly,)
    
class ConfigSetDiffApprovedApi(generics.ConfigSetDiffApprovedApiView):
    model = models.ConfigSet
    serializer_class = serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsEditorOrReadOnly,)

# class DeltaList(generics.DCPortalListCreateAPIView):
#     model = models.Delta
#     serializer_class = serializers.DeltaSerializer
#     permission_classes = (permissions.IsAdminOrReadOnly,)
# 
# class DeltaInstance(generics.DCPortalRetrieveUpdateDestroyAPIView):
#     model = models.Delta
#     serializer_class = serializers.DeltaSerializer
#     permission_classes = (permissions.IsAdminOrReadOnly,)

class DataExplorerImport(generics.DataExplorerSettingsImportAPIView):
    #model and serializer_class fields are not used.
    model = models.ConfigSet
    serializer_class =  serializers.ConfigVersionSerializer
    permission_classes = (permissions.IsEditorOrReadOnly,)

class DiscardBulkUpdate(generics.DiscardBulkUpdateAPIView):
    model = models.ConfigSet
    serializer_class = serializers.ConfigSetSerializer
    permission_classes = (permissions.IsAdminOrReadOnly,)
