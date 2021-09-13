"""
 Generic views that provide DC-portal needed behaviour.
"""
from __future__ import unicode_literals

import datetime
import pprint
import re
import os
import errno
import json
import logging
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import generics
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from util import gdiservice
from api.permissions import get_user_model
from api.mixins import ListModelMixin
from api.serializers import ConfigVersionSerializer, ConfigSetSerializer
from api.models import *
import urllib

logger = logging.getLogger()

pp = pprint.PrettyPrinter(indent=4)


def debug_print(*args):
    print_nl = True
    msg = []
    for arg in args:
        if isinstance(arg, basestring):
            print arg,
            msg.append('%s')
            print_nl = True
        else:
            pp.pprint(arg)
            msg.append('%r')
            print_nl = False
    logger.debug(' '.join(msg), *args)
    if print_nl:
        print ''


class PlannedException(Exception):
    pass


class BadRequestException(PlannedException):
    pass


class DebugException(PlannedException):
    pass


def newest_versions_only(version_list):
    version_map = {}
    # Go through the versions and keep only the newest for each config set.
    for version in version_list:
        if (version.config_set_id.id not in version_map or
                version.version_number >
                version_map[version.config_set_id.id].version_number):
            version_map[version.config_set_id.id] = version
    # Convert the {version_map} dictionary into an array to return.
    results = []
    for cfgset,version in version_map.iteritems():
        results.append(version)
    return results


def oldest_versions_only(version_list):
    version_map = {}
    # Go through the versions and keep only the oldest for each config set.
    for version in version_list:
        if (version.config_set_id.id not in version_map or
                version.version_number <
                version_map[version.config_set_id.id].version_number):
            version_map[version.config_set_id.id] = version
    # Convert the {version_map} dictionary into an array to return.
    results = []
    for cfgset,version in version_map.iteritems():
        results.append(version)
    return results


def retrieve_data_explorer_settings(productline):
    # DEFAULT URL when there is no match.
    url = 'https://ds-dataexplorer.appspot.com'
    url += '/de/stabilityWhitelistsQuery?ot=dcp&pl='
    if productline is not None and len(productline) != 0:
        url += productline.upper()
    else:
        url += 'DEFAULT'
    pp.pprint(url)
    u = urllib.urlopen(url)
    data = u.read()
    json_obj = json.loads(data)
    print json_obj
    settings = json_obj['properties']
    data_explorer_settings = {}
    for setting in settings:
        data_explorer_settings[setting['key']] = setting['value']
    return data_explorer_settings


class DCPortalRetrieveUpdateDestroyAPIView(mixins.RetrieveModelMixin,
                                   mixins.UpdateModelMixin,
                                   mixins.DestroyModelMixin,
                                   generics.SingleObjectAPIView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        data = request.DATA
        print('Received PUT request')
        if (data.get('delta_name') is not None) and (len(str(data['delta_name'])) == 0):
            return Response('Delta name cannot be blank string', status=status.HTTP_400_BAD_REQUEST)
        if data.get('delta_name', None) is None:
            request.DATA['delta_name'] = None
        if 'fallback_id' in request.DATA and 'id' in request.DATA:
            fallback_id = request.DATA['fallback_id']
            config_set_id = request.DATA['id']
            config_set = ConfigSet.objects.get(id=config_set_id)
            fallback_config_set = ConfigSet.objects.get(id=fallback_id)

            # if we are trying to update the configset's fallback, Update to right
            # fallback version.
            if (fallback_id != config_set.fallback_id.id):
                print('fallback_id, config_set_id- %d %d ', fallback_id, config_set_id)
#                 print('config_set.id %d', config_set.id)
#                 print('config_set fallback before change', config_set.fallback_id.id)
                config_set.fallback_id = fallback_config_set
                # No need to save the config_set as REST API takes care of it.
#                 print('new config_set fallback afer change', config_set.fallback_id .id)
        #         uncommited_version = ConfigVersion.objects.filter(
        #             config_set_id=config_set_id ).order_by('-version_number')[0]
                uncommited_version = ConfigVersion.objects.filter(
                    config_set_id=config_set.id ).order_by('-version_number')[0]
        #         fallback_last_approved_version = ConfigVersion.objects.filter(
        #             config_set_id=fallback_config_set ).exclude(
        #             approved__isnull=True ).order_by('-version_number')[0]
                fallback_last_approved_version = ConfigVersion.objects.filter(
                    config_set_id=fallback_config_set.id ).exclude(
                    approved__isnull=True ).order_by('-version_number')[0]
        #         config_version_list = oldest_versions_only(
        #                 ConfigVersion.objects.filter(config_set_id=config_set.id))
#                 print('vernum for cv- %d', uncommited_version.version_number)
#                 print('uncommited config_version- %d', uncommited_version.id)
#                 print('uncommited config_version fallback before change- %d', uncommited_version.fallback_id.id)
                uncommited_version.fallback_id = fallback_last_approved_version
#                 print('uncommited config_version fallback after change- %d',uncommited_version.fallback_id.id)
            uncommited_version.save()
        return self.patch(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
#         print "request is- %s",  request.DATA
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        try:
            return self.destroy(request, *args, **kwargs)
        except models.ProtectedError:
            return Response('Cannot delete the item as it is being referenced', status=status.HTTP_400_BAD_REQUEST)


class DCPortalListCreateAPIView(ListModelMixin,
                        mixins.CreateModelMixin,
                        generics.MultipleObjectAPIView):
    """
    Concrete view for listing a queryset or creating a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CurrentUserRetrieveAPIView(mixins.RetrieveModelMixin,
                                 generics.SingleObjectAPIView):
    """
    Concrete view for retrieving the model instance corresponding
    to the currently logged in user.
    """
    def get(self, request, *args, **kwargs):
        self.object = get_user_model(request.user.username)
        serializer = self.get_serializer(self.object)
        data = serializer.data
        data['cloud'] = djsettings.DEFAULT_CLOUD
        data['dcp_version'] = open(os.path.join(
            djsettings.SITEPATH, 'VERSION.txt')).read().strip()
        data['extra_info'] = 'NOT PUBLISHING' \
            if djsettings.DONOT_PUBLISH else ''
        return Response(data)


class ConfigSettingsRetrieveUpdateAPIView(mixins.RetrieveModelMixin,
                                   mixins.UpdateModelMixin,
                                   generics.SingleObjectAPIView):
    """
    Concrete view for retrieving or updating the settings for
    a model version instance.
    """
    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)

    @transaction.commit_on_success
    def patch(self, request, *args, **kwargs):
        self.object = self.get_object()
        #pp.pprint(request.DATA)
        ConfigSetting.objects.filter(config_version_id=self.object).delete()
        for name,value in request.DATA['settings'].items():
            setting_value = None
            setting_values = SettingValue.objects.filter(
                value=value, setting_def_id__name=name)
            if len(setting_values) > 0:
                setting_value = setting_values[0]
            else:
                setting_defs = SettingDef.objects.filter(name=name)
                if len(setting_defs) > 0:
                    setting_value = SettingValue.objects.create(
                        value=value, setting_def_id=setting_defs[0])
            if setting_value is not None:
                ConfigSetting.objects.create(config_version_id=self.object,
                    setting_value_id=setting_value)
        userdata = get_user_model(request.user.username)
        self.object.last_edited = datetime.datetime.now()
        self.object.last_editor_id = userdata
        self.object.comment = request.DATA['comment']
        self.object.save()
        return Response(status=status.HTTP_200_OK)

    def getCode(self, modelObj):
        if modelObj is not None:
            return modelObj.code
        return None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        currVerObj = self.object
        currExtra = currVerObj.extra = {}
        while currVerObj is not None:
            currExtra['settings'] = {}
            currExtra['hwtype'] = self.getCode(currVerObj.config_set_id.hwtype_id)
            currExtra['carrier'] = self.getCode(currVerObj.config_set_id.carrier_id)
            currExtra['region'] = self.getCode(currVerObj.config_set_id.region_id)
            currExtra['delta_name'] = currVerObj.config_set_id.delta_name
            currExtra['version_number'] = currVerObj.version_number
            for sv in currVerObj.setting_value.all():
                currExtra['settings'][sv.setting_def_id.name] = sv.value
            currExtra['fallback'] = None
            currVerObj = currVerObj.fallback_id
            if currVerObj is not None:
                currExtra['fallback'] = {}
                currExtra = currExtra['fallback']
        serializer = self.get_serializer(self.object)
        return Response(serializer.data)


class ConfigVersionDiscardAPIView(mixins.UpdateModelMixin,
                                  generics.SingleObjectAPIView):

    @transaction.commit_on_success
    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.last_edited = None
        self.object.last_editor_id = None
        self.object.save()
        ConfigSetting.objects.filter(config_version_id=self.object).delete()
        prevVersion = ConfigVersion.objects.filter(
            config_set_id=self.object.config_set_id,
            version_number=self.object.version_number-1)[0]
        for sv in prevVersion.setting_value.all():
            ConfigSetting.objects.create(
                config_version_id=self.object,
                setting_value_id=sv)
        return Response(status=status.HTTP_200_OK)


# An API call to propagate a config set version to all descendants.
# With this you can do something like make a change to a global config
# set and propagate that change to all carrier and devicetype config
# sets. It also allows you to publish the devicetype config sets (only
# for test currently). Without this feature, after making the global
# change, you would need to go to each carrier config set and commit
# then approve it to make the change visible to the devicetype config
# sets. Then you would need to go to each devicetype config set and
# commit, possibly approve, then publish it to each cloud where it is
# needed.
#
class ConfigVersionPropagateAPIView(mixins.UpdateModelMixin,
                                    generics.SingleObjectAPIView):

    def __init__(self):
      pass

    def put(self, request, *args, **kwargs):
        self.userdata = get_user_model(request.user.username)
        errors = []
        updates = []
        logger.debug("Loggedin user- %s ", self.userdata)
        self.recursiveUpdate(self.get_object().pk,
            request.DATA.get('commitdepth', 99),
            request.DATA.get('approvedepth', 99),
            request.DATA.get('publish_envs', []),
            errors, updates)
        errordata = []
        for error in errors:
            configset = ConfigSetSerializer(error[0].config_set_id).data
            configset['version_number'] = error[0].version_number
            errordata.append({'item':configset, 'data':str(error[1])})
        updatedata = []
        for update in updates:
            configset = ConfigSetSerializer(update[0].config_set_id).data
            configset['version_number'] = update[0].version_number
            updatedata.append({'item':configset, 'data':update[1]})
        return Response({'errors':errordata, 'updates':updatedata},
            status=status.HTTP_200_OK)

    # Update the config set corresponding to objid and all of its
    # descendants. {commitdepth} tells how many levels deep to do commits,
    # and {approvedepth} tells how many levels deep to do approvals.
    # Note that a version is not visible to child config sets until it is
    # approved, so changes will not propagate beyond the approval depth.
    # {publish_envs} is a list of cloud environment short names (like
    # "qa300") to publish to (only happens at the devicetype level).
    # Arrays can be passed for {updates} and {errors} to have a log of
    # the updates performed and errors encountered added to those lists.
    def recursiveUpdate(self, objid, commitdepth=99, approvedepth=99,
            publish_envs=[], errors=None, updates=None):

        logger.debug("In recursion. C.V. objid = %d " %objid)

        logger.debug("commitdepth %d" %commitdepth)

        obj = ConfigVersion.objects.get(pk=objid)
        if (obj.config_set_id.hwtype_id is not None):
            logger.debug("hwtype- %s " %obj.config_set_id.hwtype_id)
        if (obj.config_set_id.carrier_id is not None):
            logger.debug("Carrier- %s " %obj.config_set_id.carrier_id)
            logger.debug("Region- %s " %obj.config_set_id.region_id)

        logger.debug("C.V. objid %d " %objid )
        if (obj.committed is not None):
            logger.debug("Obj already commited at - %s" %obj.committed)
        if (obj.approved is not None) :
            logger.debug("Object already approved at- %s " %obj.approved)

        helper = ConfigVersionHelper(self.userdata, objid)
        updateinfo = {}
        if updates is not None:
            updates.append([obj,updateinfo])
        try:
            if commitdepth >= 0 and obj.committed is None:
                logger.debug("Commiting.")
                if (self.userdata.editor):
                    helper.commit()
                    updateinfo['commit'] = True
                    logger.debug("Commit successful")
                else:
                    logger.error("User doesn not have commit permission. Throwing exception")
                    raise BadRequestException("User does not have commit " +
                    "permission")
            if approvedepth >= 0 and obj.approved is None:
                if (self.userdata.approver):
                    helper.approve(True)
                    updateinfo['approve'] = True
                    logger.debug("Approve successful.")
                else:
                    logger.error("User does not have approve permission. Throwing exception")
                    raise BadRequestException("User does not have approve permission")
            if obj.config_set_id.hwtype_id is not None:
                pubresults = []
                updateinfo['publish'] = pubresults
                for envname in publish_envs:
                    env = CloudEnv.objects.filter(short_name=envname)[0]
                    if (env.env_type == CloudEnv.PROD):
                        # User already has admin privileges. Thats the reason
                        # propagate is called.
                        # Now we are checking if user has  publish privileges,
                        # then only we allow the publish to the production cloudsets
                        # else the PROPOGATE will be only to the QA/SDC environment
                        # only.
                        if (self.userdata.publisher):
                            helper.publish(False, False, envname)
                        else:
                            raise BadRequestException("Only user with publish " +
                                  "permission can publish to production.")
                    else:
                        helper.publish(False, True, envname)
                    pubresults.append(envname)
            # Get the child versions of the config set version {obj}. This
            # returns just the oldest version in each child config set that
            # has this version as its parent/fallback. There could be newer
            # versions (due to local changes in the child config set) that
            # also have {obj} as the parent, but we just want the changes
            # that came from {obj}. It is possible that even the first
            # version with {obj} as the parent has local child-level changes
            # mixed in. Technically we should not automatically approve such
            # versions since doing so implicitly approves the child-level
            # changes mixed in, but we do not catch that case currently.
            downstream_versions = oldest_versions_only(
                ConfigVersion.objects.filter(fallback_id=obj))
            child_versions = len(downstream_versions)
            logger.debug("Number of child versions- %d" %child_versions)

            for dv in downstream_versions:
                self.recursiveUpdate(dv.pk, commitdepth-1,
                    approvedepth-1, publish_envs, errors, updates)
        except Exception as e:
            if errors is not None:
                logger.debug("Error- %s " %e)
                errors.append([obj,e])

class ConfigVersionBulkUpdateAPIView(APIView):

    def get_last_version(self, configset):
        """
            Returns the last version (which is also uncommited version)
             for a configset .
            - indicates descending
        """
        return ConfigVersion.objects.filter(
            config_set_id=configset).order_by('-version_number')[0]

    def bulkUpdate(self, user_data, config_set_ids, settings, commit, approve,
                   publish_envs, errors, updates):
        for config_set_id in config_set_ids:
            config_version = None
            update_info = {}
            try:
                config_version = self.get_last_version(config_set_id)
                helper = ConfigVersionHelper(user_data, config_version.pk)

                if updates is not None:
                    updates.append([config_version, update_info])

                # only apply settings if the settings are given
                if len(settings) > 0:
                    helper.applySettings(user_data, settings=settings,
                                         config_version=config_version)
                    update_info['edited'] = True
                debug_print('config_set_id =', config_set_id)
                config_set_obj = ConfigSet.objects.get(id=config_set_id)

                debug_print('commit', commit)
                debug_print(
                    'config_version committed',
                    ConfigVersion.objects.get(id=config_version.id).committed)
                if commit > 0 and config_version.committed is None:
                    # If version is not edited as part of bulk update and is
                    # already edited (has local changes) then don't commit it.
                    debug_print('update_info', update_info)
                    debug_print('config_version.last_edited',
                                config_version.last_edited)
                    if not config_version.last_edited:
                        raise BadRequestException(
                            "No edited version present. No need to commit.")
                    if 'edited' not in update_info:
                        debug_print('category_id ', config_set_obj.category_id)
                        helper.discard(config_version)
                    helper.commit(client_settings=settings,
                                  comment="bulk update fix",
                                  skipValidation=True)
                    # update_info['commit'] = config_version.version_number
                    update_info['commit'] = True

                if approve > 0:
                    config_version = helper.get_last_committed(config_set_id)
                    debug_print('lastCommittedVersion =', config_version)
                    helper = ConfigVersionHelper(user_data, config_version.pk)
                    helper.approve(auto=True, comment="Bulk")
                    # update_info['approve'] = config_version.version_number
                    update_info['approve'] = True

                if len(publish_envs) > 0:
                    config_version = helper.get_last_committed(config_set_id)
                    debug_print('lastCommittedVersion =', config_version)
                    helper = ConfigVersionHelper(user_data, config_version.pk)
                    pub_results = []
                    update_info['publish'] = pub_results
                    for env_name in publish_envs:
                        env = CloudEnv.objects.filter(short_name=env_name)[0]
                        if env.env_type == CloudEnv.PROD:
                            if user_data.publisher:
                                # For production publish we want to approve only
                                # the last approved version.
                                config_version = helper.get_last_approved(
                                    config_set_id)
                                helper = ConfigVersionHelper(user_data,
                                                             config_version.pk)
                                helper.publish(False, False, env_name)
                            else:
                                debug_print("User does not have permission to "
                                            "publish to production.")
                                raise BadRequestException(
                                    "Only user with publish permission can "
                                    "publish to production.")
                        else:
                            helper.publish(False, True, env_name)
                        pub_results.append(env_name)

            except Exception as e:
                if errors is not None:
                    errors.append([config_version, e])

    def post(self, request, *args, **kwargs):
        userdata = get_user_model(request.user.username)
        pp.pprint(request.DATA)
        pp.pprint(request.DATA['settings'])
        pp.pprint(request.DATA['configsets'])
        pp.pprint("commit")
        pp.pprint(request.DATA['commit'])
        pp.pprint("approve")
        pp.pprint(request.DATA['approve'])
        pp.pprint(request.DATA['publish_envs'])

        errors = []
        updates = []

        self.bulkUpdate(userdata, request.DATA['configsets'],
                        request.DATA['settings'], request.DATA['commit'],
                        request.DATA['approve'], request.DATA['publish_envs'], errors, updates)

        pp.pprint('errors, updates')
        pp.pprint(errors)
        pp.pprint(updates)
        logger.debug('errors, updates during bulk %s %s', errors, updates)
        errordata = []
        for error in errors:
            configset = ConfigSetSerializer(error[0].config_set_id).data
            configset['version_number'] = error[0].version_number
            errordata.append({'item':configset, 'data':str(error[1])})
        updatedata = []
        for update in updates:
            configset = ConfigSetSerializer(update[0].config_set_id).data
            configset['version_number'] = update[0].version_number
            updatedata.append({'item':configset, 'data':update[1]})
        return Response({'errors':errordata, 'updates':updatedata},
            status=status.HTTP_200_OK)

class ConfigVersionHelper(mixins.UpdateModelMixin,
                                    generics.SingleObjectAPIView):

    def __init__(self, userdata, objid):
        self.objid = objid
        self.userdata = userdata
        self.object = None

    @transaction.commit_on_success
    def commit(self, client_settings=None, comment=None, skipValidation=False):
        logger.debug("config_version_id=%r", self.objid)
        obj = ConfigVersion.objects.get(pk=self.objid)
        # if object has a committed date means object is already committed
        if obj.committed is not None:
            raise BadRequestException('This version is already commited. '
                                      'Cannot commit same version again.')
        # Check if the config_set belongs to Checkin Category. If so verify
        # the settings with the DataDictionary Service
        category_name = obj.config_set_id.category_id.name
        logger.debug('config_set_id=%r', obj.config_set_id.id)
        delta_name = obj.config_set_id.delta_name
        logger.debug('category_name=%r, delta_name=%r',
                     category_name, delta_name)
        # settings_mismatch = {}
        settings_mismatch = ''
        settings_mismatch_values = {}
        settings_mismatch_list = []
        if category_name == 'Checkin' and delta_name is not None:
            complete_settings = self.get_settings(obj, {})
            productline = delta_name
            #request.DATA['productline']
            #compare client_settings with the settings from Data Dictionary service
            data_explorer_settings = retrieve_data_explorer_settings(productline)
            if client_settings is not None:
                complete_settings = self.get_settings(obj, {})
                pp.pprint(complete_settings)
                for key in data_explorer_settings:
                    if key not in complete_settings.keys():
                        continue
                    if data_explorer_settings[key] == complete_settings[key]:
                        continue
                    logger.debug(
                        'key=%r, data_explorer_setting=%r, complete_setting=%r',
                        key, data_explorer_settings[key],
                        complete_settings[key])
                    # settings_mismatch[key] =  ''
                    settings_mismatch += key
                    settings_mismatch += ','
                    # settings_mismatch_values += self.diffStrings(complete_settings[key], data_explorer_settings[key], ",")
                    # settings_mismatch_values += ','
                    # No comma in setting but :
                    # 3 cases-1. No comma in setting but has :
                    # 2. Both comma and : in setting.
                    # 3. Anything other than this
                    if (complete_settings[key].find(",") < 0
                        and complete_settings[key].find(':') > 0):
                        complete_settingtags = complete_settings[key].split(",")
                        data_explorer_settings = data_explorer_settings[key].split(",")
                        arr1 = []
                        arr2 = []
                        for data_explorer_setting in data_explorer_settings:
                            arr2.extend(data_explorer_setting.split(":"))
                        for setting_tag in complete_settingtags:
                            arr1.extend(setting_tag.split(":"))
                        settings_mismatch_values[key] = self.diffArrays(arr1, arr2)
                    elif complete_settings[key].find(',') > 0:
                        arr1 = complete_settings[key].split(",")
                        arr2 = data_explorer_settings[key].split(",")
                        settings_mismatch_values[key] = self.diffArrays(arr1, arr2)
                    else:
                        settings_mismatch_values[key] = {
                            'present': complete_settings[key],
                            'absent': data_explorer_settings[key],
                        }
                    settings_mismatch_list.append(key)
                if len(settings_mismatch) > 0:
                    settings_mismatch = settings_mismatch.rstrip(',')
                logger.info('settings_mismatch=%r, settings_mismatch_values=%r',
                            settings_mismatch, settings_mismatch_values)
        # Update the commit info on the version. This will be rolled
        # back if the commit fails.
        obj.committed = datetime.datetime.now()
        obj.committer_id = self.userdata
        if comment is not None:
            obj.comment = comment
        obj.save()
        logger.info('Creating a new config version for config_set_id=%r, '
                    'fallback_id=%r, version_number=%r', obj.config_set_id,
                    obj.fallback_id, obj.version_number+1)
        # Creating a new uncommitted version.
        newversion = ConfigVersion.objects.create(
            config_set_id=obj.config_set_id,
            fallback_id=obj.fallback_id,
            version_number=obj.version_number+1)
        logger.debug("New version created with vernum=%d", obj.version_number+1)
        logger.debug("client_settings (settings for new version as received) "
                     "= %s", client_settings)
        if not skipValidation:
            # Compare the client_settings passed to the ones in the database.
            # If these do not match, then it implies that the person doing the
            # commit is not seeing the same thing that will be committed (maybe
            # someone made a change while the committer was still looking at the
            # commit review screen). If there is a mismatch, stop the commit and
            # return an error. If no client_settings were passed (as might be
            # the case when automatically PROPOGATING changes from parent config
            # set), then allow the commit only if there are no local changes.
            # In propagate client_settings are none
            if client_settings is None:
                if obj.last_edited is not None:
                    logger.error('Cannot blindly commit local edits. '
                                 'Reverting back the commit.')
                    raise BadRequestException(
                        'Cannot blindly commit local edits.')
                # Make sure that we are taking local overrides into account. So
                # applying local overrides.
                logger.debug('setting_value.all()=%r', obj.setting_value.all())
                for sv in obj.setting_value.all():
                    settingname = sv.setting_def_id.name
                    logger.debug('settingname=%r, sv=%r', settingname, sv.value)
                    ConfigSetting.objects.create(
                        config_version_id=newversion,
                        setting_value_id=sv)
            else:
                client_settings = client_settings.copy()
                logger.debug('setting_value.all()=%r', obj.setting_value.all())
                for sv in obj.setting_value.all():
                    settingname = sv.setting_def_id.name
                    logger.debug('settingname=%r, sv=%r', settingname, sv.value)
                    if (settingname not in client_settings or
                            client_settings[settingname] != sv.value):
                        raise BadRequestException(
                            'Settings being committed do not match settings on '
                            'server')
                    del client_settings[settingname]
                    ConfigSetting.objects.create(
                        config_version_id=newversion,
                        setting_value_id=sv)
                if len(client_settings) > 0:
                    raise BadRequestException(
                        'Settings being committed do not match settings on '
                        'server')
        else:
            for sv in obj.setting_value.all():
                    settingname = sv.setting_def_id.name
                    logger.debug('settingname=%r, sv=%r', settingname, sv.value)
                    ConfigSetting.objects.create(
                        config_version_id=newversion,
                        setting_value_id=sv)

        if len(settings_mismatch) > 0:
            return {
                'settings_mismatch':settings_mismatch,
                'settings_mismatch_values': settings_mismatch_values,
                'settings_mismatch_list':settings_mismatch_list,
            }
        return None

    @transaction.commit_on_success
    def approve(self, auto=False, comment=None):
        obj = ConfigVersion.objects.get(pk=self.objid)
        if obj.committed is None:
            raise BadRequestException('Cannot approve an uncommitted version.')
        if obj.approved is not None:
            raise BadRequestException('This version is already approved.' +
                ' Cannot approve the same version again.')
        # If this is part of an automatic operation, then we do not want
        # to implicitly approve changes from other sources (in previous
        # versions). Therefore, fail if the previous version is not already
        # approved. Technically even the version being apporved could have
        # changes mixed in that did not come from the automatic action
        # being performed, but we do not check for that currently.
        if auto and obj.approved == None:
            prev_ver = ConfigVersion.objects.get(
                config_set_id=obj.config_set_id,
                version_number=obj.version_number-1)
            if prev_ver.approved == None:
                raise BadRequestException(
                    'Cannot blindly approve previous unapproved versions.')
        # Update the approval info on the version. This will be rolled
        # back if the approval fails.
        obj.approved = datetime.datetime.now()
        obj.approver_id = self.userdata
        if (comment is not None ):
            obj.comment = comment
        obj.save()
        # If there are no approvals on later versions, then this becomes
        # the new latest approved version, and the uncommited versions of
        # child config sets need to be updated to reference it.
        later_approvals = ConfigVersion.objects.filter(
            config_set_id=obj.config_set_id,
            version_number__gt=obj.version_number,
            approved__isnull=False)
        if len(later_approvals) == 0:
            downstream_versions = ConfigVersion.objects.filter(
                committed=None,
                config_set_id__fallback_id=obj.config_set_id)
            for dv in downstream_versions:
                dv.fallback_id = obj
                dv.save()

    def get_code(self, model_obj):
        if model_obj is not None:
            return model_obj.code
        return None

    def get_old_code(self, model_obj):
        if model_obj is not None:
            return model_obj.old_code
        return None

    def get_settings(self, ver_obj, settings):
        if ver_obj is None:
            return settings
        self.get_settings(ver_obj.fallback_id, settings)
        for sv in ver_obj.setting_value.all():
            settings[sv.setting_def_id.name] = sv.value
        return settings

    def compile_re(self, re_str):
        if not re_str.startswith('^'):
            re_str = '^' + re_str
        if not re_str.endswith('$'):
            re_str = re_str + '$'
        return re.compile(re_str)

    def transform_settings(self, settings, env, hwtype, carrier, region,
                           extra_key, extra_value_name):
        for transform in EnvTransform.objects.all():
            env_re = self.compile_re(transform.env_pat)
            extra_re = self.compile_re(transform.extra_level_pat)
            hwtype_re = self.compile_re(transform.hwtype_pat)
            carrier_re = self.compile_re(transform.carrier_region_pat)
            extra = extra_key + '.' + extra_value_name \
                if extra_key and extra_value_name else ''
            if (env_re.match(env.network_name) and hwtype_re.match(hwtype) and
                    carrier_re.match(carrier + '.' + region) and
                    extra_re.match(extra)):
                name_re = self.compile_re(transform.setting_name_pat)
                value_re = re.compile(transform.value_pat)
                value_sub = transform.value_sub
                if value_sub is None:
                    value_sub = ''
                value_sub = value_sub.replace('{{env}}',
                    env.network_name)
                for name in settings.keys():
                    if name_re.match(name):
                        settings[name] = value_re.sub(value_sub, settings[name])
        return settings

    def get_last_committed(self, configset):
        return ConfigVersion.objects.filter(
            config_set_id=configset ).exclude(
            committed__isnull=True ).order_by('-version_number')[0]

    def get_last_approved(self, configset):
        return ConfigVersion.objects.filter(
            config_set_id=configset ).exclude(
            approved__isnull=True ).order_by('-version_number')[0]

    def get_approved_versions(self, configset_id):
        versions = ConfigVersion.objects.filter(
            config_set_id=configset_id ).exclude(
            approved__isnull=True).order_by('-version_number')
        return versions;

    def get_published_versions(self, configset_id):
        versions = ConfigVersion.objects.filter(
            config_set_id=configset_id ).exclude(
            published__isnull=True).order_by('-version_number')
        return versions;

    def export_test(self):
        envs = CloudEnv.objects.all()
        cfgs = ConfigSet.objects.all().exclude(hwtype_id=None)
        for cfg in cfgs:
            settings = self.get_settings(self.get_last_approved(cfg), {})
            for env in envs:
                dirpath = 'exportall/' + env.short_name
                try:
                    os.makedirs(dirpath)
                except OSError as exc:
                    if exc.errno != errno.EEXIST or not os.path.isdir(dirpath):
                        raise
                f = open(dirpath + '/cfg.' + cfg.hwtype_id.code + '.' +
                         cfg.carrier_id.code + '.' + cfg.region_id.code +
                         '.properties', 'a')
                env_settings = self.transform_settings(
                    settings.copy(), env, cfg.hwtype_id.code,
                    cfg.carrier_id.code, cfg.region_id.code, cfg.extra_key,
                    cfg.extra_value_name)
                for name, value in sorted(env_settings.items()):
                    if len(value) > 0:
                        f.write(name + '=' + value.replace(':', '\\:') + "\n")
                f.close()

    @transaction.commit_on_success
    def publish(self, dryrun=False, test=False, envname='', hwsuffix='', comment=None,
                revert=False):
        obj = ConfigVersion.objects.get(pk=self.objid)
        hwtype = self.get_code(obj.config_set_id.hwtype_id)
        if hwtype is None:
            if dryrun:
                hwtype = 'noHwtype'
            else:
                raise BadRequestException('hwtype must be specified.')
        target_hwtype = hwtype
        if envname == '':
            envname = djsettings.DEFAULT_CLOUD
        env = CloudEnv.objects.filter(short_name=envname)[0]

        if test:  # If this is a publish for testing.
            if hwsuffix == '':  # If going to a test hwtype
                if env.env_type == CloudEnv.PROD:
                    raise BadRequestException('To publish for testing, ' +
                        'either a test HW type or a non-production ' +
                        'cloud must be specified.')
            elif not re.match(r'.*_TEST$', hwsuffix):
                raise BadRequestException('Test HW types must end in "_TEST".')
            else:
                # Allow "#c" or "#n" to indicate build-type extensions. This
                # is a hack, but we don't want it in the long term anyway.
                if hwsuffix == '_#c_TEST':
                    hwsuffix = '-continuous'
                elif hwsuffix == '_#n_TEST':
                    hwsuffix = '-nightly'
                target_hwtype = target_hwtype + hwsuffix

        if not re.match(r'^[a-zA-Z0-9_-]*$', target_hwtype):
            raise BadRequestException('HW types should contain only letters, ' +
                            'numbers and underscores.')

        carrier = self.get_code(obj.config_set_id.carrier_id)
        if carrier is None:
            if dryrun:
                carrier = 'noCarrier'
            else:
                raise BadRequestException('carrier must be specified.')

        #old carrier code. This is optional. It may be null
        old_carrier = self.get_old_code(obj.config_set_id.carrier_id)

        region = self.get_code(obj.config_set_id.region_id)
        if region is None:
            if dryrun:
                region = 'noRegion'
            else:
                raise BadRequestException('region must be specified.')

        carriers = [carrier]

        if old_carrier is not None:
            carriers = [carrier, old_carrier]

        extra_filter = None
        extra_key = None
        extra_value_name = None
        if obj.config_set_id.extra_value_id:
            extra_key = obj.config_set_id.extra_value_id.extra_key_id.code
            extra_value_name =  obj.config_set_id.extra_value_id.name
            extra_filter = '%s:%s' % (extra_key,
                                      obj.config_set_id.extra_value_id.value)

        for carrier in carriers:
            devicetype = target_hwtype + '.' + carrier + '.' + region
            category = obj.config_set_id.category_id
            setting_defs = SettingDef.objects.filter(category_id=category.id)

            curr_settings = gdiservice.get_settings(
                envname, hwType=target_hwtype, carrier=carrier, region=region,
                extra=extra_filter)

            # If there are no settings, then this is a new devicetype. This is
            # often the case when a test hwtype is used (hwsuffix is not "").
            is_new = len(curr_settings) == 0

            # If this is not for test, then mark the config version as published
            if not test:
                obj.published = datetime.datetime.now()
                obj.publisher_id = self.userdata

            # Else if this is a new test devicetype, try to get intial
            # settings from the corresponding non-test devicetype. Otherwise,
            # the test devicetype will end up missing all settings for
            # categories other than the one being published.
            elif is_new and hwsuffix != '':
                curr_settings = gdiservice.get_settings(
                    envname, hwType=hwtype, carrier=carrier, region=region,
                    extra=extra_filter)

            if comment is not None:
                obj.comment = comment
            obj.save()

            # Initialize the settings that we will publish to be the
            # same as the ones already on the server.
            settings = curr_settings.copy()

            # Remove all previous settings for the category being published.
            for s_def in setting_defs:
                settings.pop(s_def.name, None)

            # Get the setting values being published, transform them as
            # appropriate for the target cloud env/etc, and add them
            # to the settings gotten from the server.
            new_settings = self.get_settings(obj, {})
            self.transform_settings(new_settings, env, hwtype, carrier, region,
                                    extra_key, extra_value_name)
            settings.update(new_settings)

            # In the config portal, empty strings are considered equivalent
            # to having no value, so those should be removed from the
            # settings being published. To indicate an actual empty string,
            # the config portal allows the keyword "-BLANK-" to be used.
            for name,val in settings.items():
                if val == '':
                    del settings[name]
                elif val == '-BLANK-':
                    settings[name] = ''

            # Add a special setting with the config set version for traceability
            settings['portalVersion.' + re.sub(r"[^a-zA-Z0-9_]", '_',
                category.name)] = obj.version_number

            gdifilter = {
                'hwType': target_hwtype,
                'carrier': carrier,
                'region': region,
            }

            if extra_filter:
                gdifilter['extra'] = extra_filter

            # Record debugging information with the old and new values.
            if os.path.isdir('publish_out'):
                with open( 'publish_out/cfg.' + target_hwtype + '.' + carrier +
                        '.' + region + '.' + envname + '.old.json', 'w') as f:
                    json.dump(curr_settings, f, indent=2, sort_keys=True)
                with open( 'publish_out/cfg.' + target_hwtype + '.' + carrier +
                        '.' + region + '.' + envname + '.new.json', 'w') as f:
                    json.dump(settings, f, indent=2, sort_keys=True)

            # If this is a dry-run return an "error" showing the old and
            # new values along with some other information.
            if dryrun:
                dryrun_data = {}
                for k,v in curr_settings.iteritems():
                    dryrun_data[k+'__CURR'] = v
                for k,v in settings.iteritems():
                    dryrun_data[k+'___NEW'] = v
                dryrun_data['_1_curr_cnt'] = len(curr_settings)
                dryrun_data['_2_new_cnt'] = len(settings)
                dryrun_data['_3_env_name'] = envname
                dryrun_data['_4_target_hwtype'] = target_hwtype
                dryrun_data['_5_carrier'] = carrier
                dryrun_data['_6_region'] = region
                raise DebugException(dryrun_data)

            #Response object containing settings to hold the response of publish
            #operation
            response = {}
            # Publish the settings to the live servers.
            donot_publish = djsettings.DONOT_PUBLISH
            if donot_publish:
                logger.info('DONOT_PUBLISH is enabled. Check file: %r ' %
                            djsettings.LOGFILE)
            if is_new:
                if donot_publish:
                    # If we don't want to publish the settings then we will just
                    # write to logfile.
                    with open(djsettings.LOGFILE, 'a') as f:
                        f.write('Going to write New devicetype: %r to %r\n' %
                                (devicetype, envname))
                        f.write("DONOT_PUBLISH=%r\n" % djsettings.DONOT_PUBLISH)
                        json.dump(settings, f, indent=2, sort_keys=True)
                else:
                    response = gdiservice.add_one(envname, gdifilter, settings)
                message = 'Added ' + devicetype
            else:
                if donot_publish:
                    # If we don't want to publish the settings then we will just
                    # write to logfile.
                    with open(djsettings.LOGFILE, 'a') as f:
                        f.write("Going to update devicetype: %r to %r\n" %
                                (devicetype, envname))
                        f.write("DONOT_PUBLISH=%r\n" % djsettings.DONOT_PUBLISH)
                        json.dump(settings, f, indent=2, sort_keys=True)
                else:
                    logger.info("envname=" + envname)
                    response = gdiservice.update_one(envname, gdifilter, settings)
                    logger.info('response: %r', response)
                message = 'Updated ' + devicetype


            # For revert we want to unpublish the last published version.
            # config_set_id is same for all versions.
            if revert:
                pub_versions = self.get_published_versions(obj.config_set_id)
            # TODO: Add Enforcement from server to make sure we can never revert when we
            # have less than 2 published versions.
            #    if (len(pub_versions) < 2):
            #        raise Exception("No published config version exist to be reverted")
                objLP = pub_versions[0]
                objLP.published = None
                objLP.publisher_id = None
                objLP.save()

            # Get and return the resulting settings after publishing. The
            # client may choose to display or otherwise verify these.
            updated_settings = {}
            if not donot_publish:
                jd = json.loads(response if response else {})
                if "error" not in jd:
                    raise BadRequestException('Unrecognized response.')
                if jd["error"] != "OK":
                    raise BadRequestException(
                        'SettingId from response  not in proper format.')
                if not isinstance(jd["config"]["settingId"], basestring):
                    raise BadRequestException(
                        'SettingId from response not in proper format.')
                logger.debug(jd["config"]["settingId"])
                setting_id = json.loads(jd["config"]["settingId"])
                logger.debug("settingId= %s" % str(setting_id))
                updated_settings = gdiservice.get_settings_by_id(
                    envname, setting_id)["settings"]["settings"]

#                 pp.pprint('updated_settings-')
#                 pp.pprint(updated_settings)
            # Validate the publish operation only for production.
            if envname == 'prod':
                # Code for validating the settings that we want to publish to GDM.
                # Validation for last published settings in DCP with the available settings
                # at GDM.
                last_published_versions = self.get_published_versions(obj.config_set_id)
                if last_published_versions is not None:
                    last_published_version = last_published_versions[0]
                else:
                    raise BadRequestException('Incorrect state. There are no ' +
                    'local published versions')
                last_published_setting = self.get_settings(last_published_version, {})
                # Iterate over DCP key,value pairs.
                for (key, value) in last_published_setting.items():
                      # if no value exists for setting means, the local setting was
                      # never published. So ignore those settings.
                    if value == "":
                        continue
                     # Check if the key present in the local setting is present in
                     # the GDM setting object.
                    if key not in updated_settings:
                        pp.pprint("Setting missing- ")
                        pp.pprint(key)
                        logger.debug("Setting missing %s " %key)
                        raise BadRequestException('Publish unsuccessful. Settings '
                            + 'dont match with GDM. Try again.')
                    if value != updated_settings[key]:
                        pp.pprint(key)
                        pp.pprint("not equal")
                        raise BadRequestException('Publish unsuccessful. Settings '
                            + ' dont match with GDM. Try again.')
        return {'message':message,'settings':updated_settings}

#     def applySettings(self, userdata, configset, settings, comment=""):

    @transaction.commit_on_success
    def applySettings(self, userdata, config_version, settings, comment=""):
        """
            Apply settings to uncommitted/last config version of a config set.
            settings - name, value pair holding the config setting.
        """
        self.object = config_version

        existing_settings = self.get_settings(self.object, {})
        debug_print("ExistingSettings for config_version -", self.object, '-',
                    existing_settings)
        debug_print("settings.items()", settings.items())

        for name, value in settings.items():
            debug_print("setting name", name, 'new value', value['new'])
            setting_defs = SettingDef.objects.filter(name=name)

            if len(setting_defs) <= 0:
                raise BadRequestException('No setting definition: %r' % name)
            setting_def = setting_defs[0]

            existing_value = existing_settings[name] \
                if name in existing_settings.keys() else ''

            debug_print('existing_value', existing_value,
                        'passed value[old]', value['old'])
            if value['old'] != existing_value:
                raise BadRequestException("Values don't match. Can't update")

            debug_print("Old value match with the value that is specified.")

            # Remove old value for that version, if exists
            ConfigSetting.objects.filter(
                config_version_id=self.object,
                setting_value_id__setting_def_id=setting_def).delete()

            # Now adds new value, if necessary
            if value['new'] == '*remove*':
                continue

            setting_values = SettingValue.objects.filter(
                value=value['new'], setting_def_id=setting_def)
            if len(setting_values) > 0:
                setting_value = setting_values[0]
            else:
                setting_value = SettingValue.objects.create(
                    value=value['new'], setting_def_id=setting_def)
            if setting_value is None:
                raise BadRequestException('Error setting new value')

            # Create entry in config_setting, with config_version and
            # setting_value information. For inspecting object use:
            # debug_print(inspect.getmembers(setting_value))
            ConfigSetting.objects.create(
                config_version_id=self.object, setting_value_id=setting_value)

        if self.object.last_edited is not None:
            raise BadRequestException(
                'Cannot blindly apply on top of local edits.')
        self.object.last_edited = datetime.datetime.now()
        self.object.last_editor_id = userdata
        self.object.comment = comment
        self.object.save()

    def set_object_id(self, objid):
        self.objid = objid

    def diffArrays(self, arr1, arr2):
        present = ''
        absent = ''
        #Find elements that are in first array and not in second.
        for elem1 in arr1:
            try:
                arr2.index(elem1)
            except Exception as  e:
                present += elem1 + ';'
        # Find elements that are in second array but not in first.
        for elem2 in arr2:
            try:
                arr1.index(elem2)
            except Exception  as e:
                absent += elem2 + ';'
        return {'present': present, 'absent': absent}

    def removeColon(self, elem):
        if elem.find(":") > -1:
            elem.replace(":", " ")

    def discard(self, config_version):
        self.object = config_version
        print 'discarding config_version ', self.object

        self.object.last_edited = None
        self.object.last_editor_id = None
        self.object.save()
        ConfigSetting.objects.filter(config_version_id=self.object).delete()
        prevVersion = ConfigVersion.objects.filter(
            config_set_id=self.object.config_set_id,
            version_number=self.object.version_number-1)[0]
        for sv in prevVersion.setting_value.all():
            ConfigSetting.objects.create(
                config_version_id=self.object,
                setting_value_id=sv)

class ConfigVersionCommitAPIView(mixins.UpdateModelMixin,
                                 generics.SingleObjectAPIView):

    def put(self, request, *args, **kwargs):
        try:
            userdata = get_user_model(request.user.username)
            helper = ConfigVersionHelper(userdata, self.get_object().pk)
            settings_mismatch = helper.commit(request.DATA['settings'], request.DATA['comment'])
            if settings_mismatch is not None and len(settings_mismatch) > 0:
                return Response(settings_mismatch, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_200_OK)
        except PlannedException as e:
            return Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)


class ConfigVersionApproveAPIView(mixins.UpdateModelMixin,
                                  generics.SingleObjectAPIView):

    def put(self, request, *args, **kwargs):
        try:
            userdata = get_user_model(request.user.username)
            helper = ConfigVersionHelper(userdata, self.get_object().pk)
            helper.approve(comment=request.DATA['comment'])
            return Response(status=status.HTTP_200_OK)
        except PlannedException as e:
            return Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)


class ConfigVersionPublishAPIView(mixins.UpdateModelMixin,
                                  generics.SingleObjectAPIView):

    def put(self, request, *args, **kwargs):
        try:
            userdata = get_user_model(request.user.username)
            helper = ConfigVersionHelper(userdata, self.get_object().pk)
            dryrun = request.DATA.get('dryrun', '') == '1'
            return Response(helper.publish(dryrun, comment=request.DATA['comment']), status=status.HTTP_200_OK)
        except PlannedException as e:
            return Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)

class ConfigVersionRevertAPIView(mixins.UpdateModelMixin,
                                  generics.SingleObjectAPIView):

    def put(self, request, *args, **kwargs):
        try:
            userdata = get_user_model(request.user.username)
            helper = ConfigVersionHelper(userdata, self.get_object().pk)
            dryrun = request.DATA.get('dryrun', '') == '1'
            return Response(helper.publish(dryrun, comment=request.DATA['comment'], revert=True), status=status.HTTP_200_OK)
        except PlannedException as e:
            return Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)


class ConfigVersionTestPublishAPIView(ConfigVersionPublishAPIView):

    def put(self, request, *args, **kwargs):
        try:
            userdata = get_user_model(request.user.username)
            helper = ConfigVersionHelper(userdata, self.get_object().pk)
            dryrun = request.DATA.get('dryrun', '') == '1'
            if request.DATA.get('exportall', '') == '1':
                helper.export_test()
                return Response(
                    'Settings exported for all devicetypes and clouds.',
                    status=status.HTTP_200_OK)
            return Response(
                helper.publish(dryrun, test=True,
                    hwsuffix=request.DATA.get('hwsuffix', ''),
                    envname=request.DATA.get('env', ''),
                    comment=request.DATA['comment']),
                status=status.HTTP_200_OK)
        except PlannedException as e:
            return Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)


class ConfigSetHelper():

    def __init__(self, userdata):
        self.userdata = userdata

    @transaction.commit_on_success
    def create(self, data):
        result = []
        category_id_list = data.get('category_id_list', [])
        if len(category_id_list) == 0:
            if 'category_id' in data:
                category_id_list.append(data['category_id'])
            else:
                raise BadRequestException(
                    'A settings category must be specified.')

        for category_id in category_id_list:
            category_obj = SettingCategory.objects.get(pk=category_id)
            if category_obj is None:
                raise BadRequestException(
                    'Specified settings category does not exist.')
            result.append(self.recursiveCreate(data, category_obj))

        return result

    def recursiveCreate(self, data, category_obj, reuse=False):
        hwtype_obj = None
        carrier_obj = None
        region_obj = None
        fallback_obj = None
        delta_name = None
        extra_value_obj = None

        try:
            if data.get('hwtype', None) is not None:
                hwtype_obj = Hwtype.objects.get(code=data['hwtype'])
            if data.get('carrier', None) is not None:
                carrier_obj = Carrier.objects.get(code=data['carrier'])
            if data.get('region', None) is not None:
                region_obj = Region.objects.get(code=data['region'])
            if data.get('delta_name', None) is not None:
                delta_name = data.get('delta_name')
            if data.get('extra_value_id', None) is not None:
                extra_value_obj = ExtraValue.objects.get(pk=data['extra_value_id'])
            if data.get('fallback_id', None) is not None:
                fallback_obj = ConfigSet.objects.get(pk=data['fallback_id'])
            elif data.get('fallback', None) is not None:
                fallback_obj = self.recursiveCreate(
                    data['fallback'], category_obj, reuse=True)
        except ObjectDoesNotExist as e:
            raise BadRequestException(str(e))

        if (fallback_obj is not None and
                fallback_obj.category_id.id != category_obj.id):
            raise BadRequestException(
                'Fallback category does not match specified category.')

        # Verify if this new config set exists
        obj = None
        objlist = ConfigSet.objects.filter(
            hwtype_id = hwtype_obj,
            carrier_id = carrier_obj,
            region_id = region_obj,
            category_id = category_obj,
            delta_name = delta_name,
            extra_value_id = extra_value_obj)

        if len(objlist) > 1:
            raise Exception('Non-unique config sets already exist.')
        elif len(objlist) == 1:
            if reuse:
                obj = objlist[0]
            else:
                raise BadRequestException('Config set already exists.')
        else:
            print('Creating new configset object with delta name- %s ', data.get('delta_name'))
            try:
                obj = ConfigSet.objects.create(
                    hwtype_id = hwtype_obj,
                    carrier_id = carrier_obj,
                    region_id = region_obj,
                    delta_name = data.get('delta_name', None),
                    extra_value_id = extra_value_obj,
                    category_id = category_obj,
                    fallback_id = fallback_obj,
                    comment = data.get('comment', None))
            except Exception as e:
                print('Exception- %s ', e )
                raise BadRequestException('Config Set already exists.')
            now = datetime.datetime.now()
            fallback_version_obj = None
            if fallback_obj is not None:
                versions = ConfigVersion.objects.filter(
                    config_set_id=fallback_obj).exclude(
                    approved__isnull=True).order_by('-version_number')
                if len(versions) > 0:
                    fallback_version_obj = versions[0]
                else:
                    raise Exception('Failed to determine version fallback.')

            verobj = ConfigVersion.objects.create(
                config_set_id = obj,
                version_number = 1,
                committed = now,
                committer_id = self.userdata,
                approved = now,
                approver_id = self.userdata,
                fallback_id = fallback_version_obj)

            ConfigVersion.objects.create(
                config_set_id = obj,
                version_number = 2,
                fallback_id = fallback_version_obj)

            if obj.hwtype_id is not None:
                verhelper = ConfigVersionHelper(self.userdata, verobj.id)
                for envname in data.get('publish_envs', []):
                    verhelper.publish(False, True, envname)

        return obj


class ConfigSetListCreateAPIView(ListModelMixin,
                        mixins.CreateModelMixin,
                        generics.MultipleObjectAPIView):

    def post(self, request, *args, **kwargs):
        try:
            userdata = get_user_model(request.user.username)
            helper = ConfigSetHelper(userdata)
            result = helper.create(request.DATA)
            # TODO: Return more information when multiple config sets are created.
            resultdata = ConfigSetSerializer(result[0]).data
            return Response(resultdata, status=status.HTTP_201_CREATED)
        except PlannedException as e:
            return Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ConfigReportAPIView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        versions = ConfigVersion.objects.all()
        cfgsets = ConfigSet.objects.all()
        cfgsetmap = {}
        for cfgset in cfgsets:
            cfgsetmap[cfgset.pk] = cfgset

        # Find the latest committed, approved, and published
        # versions for each config set.
        committed = {}
        approved = {}
        published = {}
        # Go through every version to find the ones we want.
        for version in versions:
            cfgset_id = version.config_set_id_id
            if (version.committed is not None and (
                    cfgset_id not in committed or version.version_number >
                    committed[cfgset_id].version_number)):
                committed[cfgset_id] = version
            if (version.approved is not None and (
                    cfgset_id not in approved or version.version_number >
                    approved[cfgset_id].version_number)):
                approved[cfgset_id] = version
            if (version.published is not None and (
                    cfgset_id not in published or version.version_number >
                    published[cfgset_id].version_number)):
                published[cfgset_id] = version

        # Restructure the data into something that is suitable to return.
        # It will be a list of config sets with all the usual config set
        # data plus some basic information about the latest committed,
        # approved, and published versions.
        reportdata = []
        for cfgset in cfgsets:
            cfgsetdata = ConfigSetSerializer(cfgsetmap[cfgset.pk]).data
            if cfgset.pk in committed:
                verobj = ConfigVersionSerializer(committed[cfgset.pk]).data
                cfgsetdata['committed'] = {
                    'ver': verobj['version_number'],
                    'user': verobj['committer'],
                    'date': verobj['committed']
                }
            if cfgset.pk in approved:
                verobj = ConfigVersionSerializer(approved[cfgset.pk]).data
                cfgsetdata['approved'] = {
                    'ver': verobj['version_number'],
                    'user': verobj['approver'],
                    'date': verobj['approved']
                }
            if cfgset.pk in published:
                verobj = ConfigVersionSerializer(published[cfgset.pk]).data
                cfgsetdata['published'] = {
                    'ver': verobj['version_number'],
                    'user': verobj['publisher'],
                    'date': verobj['published']
                }
            reportdata.append(cfgsetdata)

        return Response(reportdata, status=status.HTTP_200_OK)


class ConfigSetQueryAPIView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        return self.query(request)

    def query(self, request, *args, **kwargs):
        hwtype = request.QUERY_PARAMS['hwtype']
        carrier = request.QUERY_PARAMS['carrier']
        region = request.QUERY_PARAMS['region']
        extra = request.QUERY_PARAMS['extra']
        envname = request.QUERY_PARAMS['env']
        devicetype = hwtype + '.' + carrier + '.' + region
        if envname is None:
            envname = djsettings.DEFAULT_CLOUD
        curr_settings = gdiservice.get_settings(
            envname, hwType=hwtype, carrier=carrier, region=region, extra=extra)
        for key, value in curr_settings.items():
            logger.debug("key=%r, value=%r", key, value)
        return Response({
            'settings': curr_settings,
        }, status=status.HTTP_200_OK)


class ConfigzipImportAPIView( mixins.CreateModelMixin,
                              generics.MultipleObjectAPIView):
    """
    Import a config.zip and create config sets based on it.
    This imports from a fixed file on the server, not an upload.
    """
    NO_COMMON_VAL = None

    def post(self, request, *args, **kwargs):
        return Response(
            {'stats':self.import_cfg(request)},
            status=status.HTTP_200_OK )

    def getAt(self, array, index, default=None):
        try:
            return array[index]
        except IndexError:
            return default

    def init_stats(self, stats):
        stats.setdefault('filter',{})
        stats.setdefault('children',{})
        stats.setdefault('settings',{})
        return stats

    def calc_norm(self, stats):
        totals = {}
        cnts = {}
        children = stats['children']
        for scope, child in children.iteritems():
            for name, val in child['settings'].iteritems():
                valcnts = cnts.setdefault(name,{})
                valcnts[''] = valcnts.get('',len(children)) - 1
                valcnts[val] = 1 + valcnts.get(val,0)
                if( valcnts[''] < 1 ):
                    del valcnts['']
        for name, valcnts in cnts.iteritems():
            commonval = None
            commoncnt = 1
            for val, cnt in valcnts.iteritems():
                if cnt > commoncnt:
                    commonval = val;
                    commoncnt = cnt;
                elif cnt == commoncnt:
                    commonval = self.NO_COMMON_VAL;
            stats['settings'][name] = commonval
            stats.setdefault('cnts',{})[name] = ( str(commoncnt) + ' ' +
                str(len(children)) + ' ' + str(len(valcnts)) )

    def calc_stats(self):
        props = gdiservice.read_config_zip('prod',
            os.path.join(djsettings.SITEPATH, '../config.zip'))
        if (False):
            return
        stats = self.init_stats({})
        for f, settings in props:
            cfilter = { k: f[k] for k in ['carrier','region'] }
            dfilter = { k: f[k] for k in ['hwType','carrier','region'] }
            cname = f['carrier'] + '.' + f['region']
            dname = f['hwType']
            cstats = stats['children'].setdefault(cname, self.init_stats({}))
            dstats = cstats['children'].setdefault(dname, self.init_stats({}))
            cstats['filter'] = cfilter
            dstats['filter'] = dfilter
            dstats['settings'] = settings
        for cname, cstats in stats['children'].iteritems():
            self.calc_norm(cstats)
        self.calc_norm(stats)
        return stats

    def get_last_approved(self, configset):
        return ConfigVersion.objects.filter(
            config_set_id=configset ).exclude(
            approved__isnull=True ).order_by('-version_number')[0]

    def get_flat_settings(self, configver):
        settings = {}
        while configver is not None:
            for sv in configver.setting_value.all():
                if not sv.setting_def_id.name in settings:
                    settings[sv.setting_def_id.name] = sv.value
            configver = configver.fallback_id
        return settings

    def produce_region(self, code):
        if code is None:
            return None
        result = self.getAt(Region.objects.filter(code=code), 0)
        if result is None:
            result = Region.objects.create(code=code, name=code)
        return result

    def produce_carrier(self, code):
        if code is None:
            return None
        result = self.getAt(Carrier.objects.filter(code=code), 0)
        if result is None:
            result = Carrier.objects.create(code=code, name=code)
        return result

    def produce_hwtype(self, code):
        if code is None:
            return None
        result = self.getAt(Hwtype.objects.filter(code=code), 0)
        if result is None:
            result = Hwtype.objects.create(code=code)
        return result

    def create_configset(self, stats, category, catmap, parent):
        f = stats['filter']
        parentver = None
        fallbacks = {}
        if parent is not None:
            parentver = self.get_last_approved(parent)
            fallbacks = self.get_flat_settings(parentver)
        configset = ConfigSet.objects.create(
            region_id=self.produce_region(f.get('region',None)),
            carrier_id=self.produce_carrier(f.get('carrier',None)),
            hwtype_id=self.produce_hwtype(f.get('hwType',None)),
            category_id=category,
            fallback_id=parent )
        ver1 = ConfigVersion.objects.create(
            version_number=1,
            config_set_id=configset,
            committer_id=self.user,
            committed=self.now,
            approver_id=self.user,
            approved=self.now,
            fallback_id=parentver )
        ver2 = ConfigVersion.objects.create(
            version_number=2,
            config_set_id=configset,
            committer_id=self.user,
            committed=self.now,
            approver_id=self.user,
            approved=self.now,
            fallback_id=parentver )
        ver3 = ConfigVersion.objects.create(
            version_number=3,
            config_set_id=configset,
            fallback_id=parentver )
        names = set(stats['settings'].keys())
        names.update(fallbacks.keys())
        for name in names:
            if catmap[name] != category.name:
                continue
            value = stats['settings'].get(name,'')
            fallback = fallbacks.get(name,'')
            if value != self.NO_COMMON_VAL and value != fallback:
                setting_def = SettingDef.objects.filter(name=name)[0]
                setting_value = None
                setting_values = SettingValue.objects.filter(
                    value=value, setting_def_id=setting_def)
                if len(setting_values) > 0:
                    setting_value = setting_values[0]
                else:
                    setting_value = SettingValue.objects.create(
                        value=value, setting_def_id=setting_def)
                ConfigSetting.objects.create(config_version_id=ver2,
                    setting_value_id=setting_value)
                ConfigSetting.objects.create(config_version_id=ver3,
                    setting_value_id=setting_value)
        return configset

    def load_categories(self):
        catmap = {}
        fname = os.path.join(djsettings.SITEPATH, '../import_categories.json')
        if os.path.isfile(fname):
            struct = json.load(open(fname))
            for cat,settings in struct.iteritems():
                for s in settings:
                    catmap[s] = cat
        return catmap

    @transaction.commit_on_success
    def import_cfg(self, request):
        self.now = timezone.now()
        self.user = get_user_model(request.user.username)
        stats = self.calc_stats()
        catmap = self.load_categories()
        for name, val in stats['settings'].iteritems():
            catmap.setdefault(name, 'Core')
        for catname in set(catmap.values()):
            category = self.getAt(
                SettingCategory.objects.filter(name=catname), 0)
            if category is None:
                category = SettingCategory.objects.create(name=catname)
            for name, val in stats['settings'].iteritems():
                if catmap[name] != catname:
                    continue
                setting_def = self.getAt(SettingDef.objects.filter(
                    name=name, category_id=category), 0)
                if setting_def is None:
                    setting_def = SettingDef.objects.create(
                        name=name, category_id=category, datatype='str',
                        display_name=name )
            globalcfg = self.create_configset(stats, category, catmap, None)
            for cname,cstats in stats['children'].iteritems():
                carrcfg = self.create_configset(
                    cstats, category, catmap, globalcfg)
                for dname,dstats in cstats['children'].iteritems():
                    self.create_configset(dstats, category, catmap, carrcfg)
        return stats

class ConfigSetDiffApiView(APIView):
    def get(self, request):
        # Code for validating the settings that we want to publish to GDM.
        # Validation for last published settings in DCP with the available settings
        # at GDM.
        errors = ''
        try:
            config_sets = ConfigSet.objects.all()
            envname = 'prod'
            diff_result = ''
            with open(djsettings.DIFFSFILE, 'w') as f:
                for config_set in config_sets:
                    ver_helper = ConfigVersionHelper(userdata=request.user.username, objid=None)
                    last_published_versions = ver_helper.get_published_versions(config_set)
                    if len(last_published_versions) > 0:
                        last_published_version = last_published_versions[0]
                        ver_helper.set_object_id(last_published_version.pk)
                        last_published_setting = ver_helper.get_settings(last_published_version, {})
                        hwtype = ver_helper.get_code(last_published_version.config_set_id.hwtype_id)
                        # for both carrier and global config sets we don't want to do any
                        # diff. So skipping them.
                        if (hwtype == None):
                            continue
                        carrier = ver_helper.get_code(last_published_version.config_set_id.carrier_id)
                        old_carrier = ver_helper.get_old_code(last_published_version.config_set_id.carrier_id)
                        carriers = [carrier]
                        if old_carrier is not None:
                            carriers = [carrier, old_carrier]
                            pp.pprint('carrier')
                        region = ver_helper.get_code(last_published_version.config_set_id.region_id)

                        for carrier in carriers:
                            config_set = hwtype + '-' +carrier + '-' + region + '\n'
                            gdm_settings = gdiservice.get_settings(
                                envname, hwType=hwtype, carrier=carrier,
                                region=region)
                            # Iterate over DCP key,value pairs.
                            error = ''
                            for (key, value) in last_published_setting.items():
                                # if no value exists for setting means, the local setting was
                                # never published. So ignore those settings.
                                if value == "":
                                    continue
                                # Check if the key present in the local setting is present in
                                # the GDM setting object.
                                if key not in gdm_settings:
                                    error = error + 'Setting ' + key + ' not published in GDM'
                                    error = error + '\n'
                                    continue
                                if value != gdm_settings[key]:
                                    error = error + 'Setting values not match for -' + key
                                    error = error + '\n'
                            if (len(error) > 0):
                                diff_result = diff_result + config_set + error
                f.write (diff_result)
        except Exception as e:
            errors = 'Exception during diff- ' + e
            result = 'Exception occured while doing diff- ' + e

        if errors == '':
            result = 'Diff finished successfully. Check log file.'

        return Response({'Result':result }, status=status.HTTP_200_OK)

class ConfigSetUnpublishedApiView(APIView):
    def get(self, request):
        # Code for finding the configsets that don't have
        # blur.service.push.xmppHost as    jabber-blur.svcmot.com
        errors = []
        result = ''
        count = 0
        try:
            config_sets = ConfigSet.objects.all()
            envname = 'prod'
            with open(os.path.join(djsettings.SITEPATH, 'logs/unpublished.log'), 'w') as f:
                for config_set in config_sets:
                    ver_helper = ConfigVersionHelper(userdata=request.user.username, objid=None)
                    last_approved_version = ver_helper.get_last_approved(config_set)
                    if (last_approved_version is not None):
                        ver_helper.set_object_id(last_approved_version.pk)
                        last_approved_setting = ver_helper.get_settings(last_approved_version, {})
                        hwtype = ver_helper.get_code(last_approved_version.config_set_id.hwtype_id)

                        # for both carrier and global config sets we don't want to do any
                        # diff. So skipping them.
                        if (hwtype == None):
                            continue
                        carrier = ver_helper.get_code(last_approved_version.config_set_id.carrier_id)
                        old_carrier = ver_helper.get_old_code(last_approved_version.config_set_id.carrier_id)
                        carriers = [carrier]
                        if old_carrier is not None:
                            carriers = [carrier, old_carrier]
                            pp.pprint('carrier')
                        region = ver_helper.get_code(last_approved_version.config_set_id.region_id)

                        for carrier in carriers:
                            config_set = hwtype + '-' +carrier + '-' + region + '\n'
                            gdm_settings = gdiservice.get_settings(
                                envname, hwType=hwtype, carrier=carrier,
                                region=region)
                            # Iterate over DCP key,value pairs.
                            # Check if blur.service.push.xmppHost exist in the setting.
                            settings_to_check = ["blur.service.push.xmppHost", "blur.service.push.xmppHostPrivate" , "blur.service.push.xmppHostPublic", "blur.service.push.xmppService"]
                            for setting in settings_to_check:
                                error = ''
#                                 if "blur.service.push.xmppHost" in last_approved_setting:
                                if setting in last_approved_setting:
#                                     dcp_xmpp_host = last_approved_setting.get("blur.service.push.xmppHost")
                                    dcp_xmpp_host = last_approved_setting.get(setting)
#                                     if "blur.service.push.xmppHost" in gdm_settings:
                                    if setting in gdm_settings:
#                                         gdm_xmpp_host = gdm_settings["blur.service.push.xmppHost"]
                                        gdm_xmpp_host = gdm_settings[setting]
                                    else:
#                                         error = error + 'Setting ' + 'blur.service.push.xmppHost' + ' not published in GDM'
                                        error = error + 'Setting ' + setting + ' not published in GDM'
                                        error = error + '\n'
                                        result = result + config_set + error
                                        continue
                                    if dcp_xmpp_host != gdm_xmpp_host:
#                                         error = error+ 'Setting value for ' + 'blur.service.push.xmppHost not match'
                                        error = error+ 'Setting value for ' + setting +' not match'
                                        error = error + '\n'
                                        result = result + config_set + error
                                    pp.pprint("dcp_xmpp_host")
                                    pp.pprint(dcp_xmpp_host)
                                    pp.pprint("gdm_xmpp_host")
                                    pp.pprint(gdm_xmpp_host)
                                    count = count + 1
#                         if count > 100:
#                             break
                f.write (result)
        except Exception as e:
            errors.append('Exception during search- ')
            errors.append(str(e))
            result = 'Exception occured while doing diff- ' + errors[0] + errors[1]

        if errors == []:
            result = 'Search for unpublished versions finished successfully. Check log file.'

        return Response({'Result':result }, status=status.HTTP_200_OK)

class ConfigSetDiffPublishedApiView(APIView):
    def get(self, request):
        # Code for doing diff of last 2 published settings.
        errors = ''
        try:
            config_sets = ConfigSet.objects.all()
            diff_result = ''
            count = 0
            with open(djsettings.DIFFSFILE, 'w') as f:
                for config_set in config_sets:
                    ver_helper = ConfigVersionHelper(userdata=request.user.username, objid=None)
                    last_published_versions = ver_helper.get_published_versions(config_set)
                    #if there are more than 2 published versions.
                    if len(last_published_versions) > 1:
                        last_published_version0 = last_published_versions[0]
                        last_published_version1 = last_published_versions[1]
                        ver_helper.set_object_id(last_published_version1.pk)
                        last_published_setting0 = ver_helper.get_settings(last_published_version0, {})
                        last_published_setting1 = ver_helper.get_settings(last_published_version1, {})
                        hwtype = ver_helper.get_code(last_published_version0.config_set_id.hwtype_id)
                        # for both carrier and global config sets we don't want to do any
                        # diff. So skipping them. IF any of the version refers to config set
                        # that does not have the hwtype then other version will also refer to configset
                        # that does not have the hwtype
                        pp.pprint('hwtype')
                        pp.pprint(hwtype)
                        #if (hwtype == None or (not hwtype.startswith('ghost')) or (not hwtype.startswith('falcon'))):
                        if (hwtype == None):
                            continue
                        if ((not hwtype.startswith('ghost')) and (not hwtype.startswith('falcon'))):
                            continue
                        if (not hwtype.startswith('falcon_umts')):
                            continue

                        pp.pprint(config_set)
                        carrier = ver_helper.get_code(last_published_version0.config_set_id.carrier_id)
                        old_carrier = ver_helper.get_old_code(last_published_version0.config_set_id.carrier_id)
                        carriers = [carrier]
                        if old_carrier is not None:
                            carriers = [carrier, old_carrier]
                            pp.pprint('carrier')
                        region = ver_helper.get_code(last_published_version0.config_set_id.region_id)

                        for carrier in carriers:
                            config_set = hwtype + '-' +carrier + '-' + region + '\n'
                            # Iterate over DCP key,value pairs.
                            error = ''
                            # Multiple diffs need to be done. To compare last version with secondlast version.
                            # And to compare second last version with last version. The reason is we don't store
                            # values for the keys which don't exist.
#                             for (key, value) in last_published_setting1.items():
                            for (key, value) in last_published_setting0.items():
                                # Check if the key present in the second last version is present in
                                # the latest version.
                                if key not in last_published_setting1:
                                    error = error + 'Setting ' + key + ' not present in previous version'
                                    error = error + '\n'
                                    continue
                                if value != last_published_setting1[key]:
                                    error = error + 'Setting values not match for -' + key
                                    error = error + '\n'
#                                 if carrier == 'EURetail':
#                                     error = error + 'key =' + key
#                                     error = error + 'value1 = ' + value
#                                     error = error + 'value0 =' + last_published_setting0[key]
                            if (len(error) > 0):
                                diff_result = diff_result + config_set + error
                        #pp.pprint("Setting0")
                        #pp.pprint(config_set)
                        #pp.pprint(last_published_setting0)
                        #pp.pprint(last_published_setting1)
                        count = count + 1
                        #if count > 5:
                        #    break;
                pp.pprint('processed')
                pp.pprint(count)
                #if hwtype.startswith('ghost') or hwtype.startswith('falcon'):
                f.write (diff_result)
        except Exception as e:
            errors = 'Exception during diff- ' + e
            result = 'Exception occured while doing diff- ' + e

        if errors == '':
            result = 'Diff finished successfully. Check log file.'

        return Response({'Result':result }, status=status.HTTP_200_OK)

class ConfigSetDiffApprovedApiView(APIView):
    def get(self, request):
        # Code for doing diff of last 2 approved settings.
        errors = ''
        try:
            config_sets = ConfigSet.objects.all()
            diff_result = ''
            count = 0
            current_time = datetime.datetime.now().time()
            file_name = djsettings.DIFFSFILE_APPROVED + str(current_time)
            with open(file_name, 'w') as f:
                for config_set in config_sets:
                    ver_helper = ConfigVersionHelper(userdata=request.user.username, objid=None)
                    last_approved_versions = ver_helper.get_approved_versions(config_set)
                    #if there are more than 2 approved versions.
                    if len(last_approved_versions) > 1:
                        last_approved_version0 = last_approved_versions[0]
                        last_approved_version1 = last_approved_versions[1]
                        ver_helper.set_object_id(last_approved_version1.pk)
                        last_approved_setting0 = ver_helper.get_settings(last_approved_version0, {})
                        last_approved_setting1 = ver_helper.get_settings(last_approved_version1, {})
                        hwtype = ver_helper.get_code(last_approved_version0.config_set_id.hwtype_id)
                        carrier = ver_helper.get_code(last_approved_version0.config_set_id.carrier_id)
                        # for both carrier and global config sets we don't want to do any
                        # diff. So skipping them. If any of the version refers to config set
                        # that does not have the hwtype then other version will also refer to configset
                        # that does not have the hwtype
#                         pp.pprint('hwtype')
#                         pp.pprint(hwtype)
                        #if (hwtype == None or (not hwtype.startswith('ghost')) or (not hwtype.startswith('falcon'))):
                        # Only interested in carrier configs. So skip both devicetype and global config
                        if (hwtype is not None):
                            continue
                        if (carrier == None):
                            continue
#                         if ((not hwtype.startswith('ghost')) and (not hwtype.startswith('falcon'))):
#                             continue
#                         if (not hwtype.startswith('falcon_umts')):
#                             continue

                        pp.pprint(config_set)
                        carrier = ver_helper.get_code(last_approved_version0.config_set_id.carrier_id)
                        old_carrier = ver_helper.get_old_code(last_approved_version0.config_set_id.carrier_id)
                        carriers = [carrier]
                        if old_carrier is not None:
                            carriers = [carrier, old_carrier]
                            pp.pprint('carrier')
                        region = ver_helper.get_code(last_approved_version0.config_set_id.region_id)

                        for carrier in carriers:
                            config_set = carrier + '-' + region + '\n'
                            # Iterate over DCP key,value pairs.
                            error = ''
                            # Multiple diffs need to be done. To compare last version with secondlast version.
                            # And to compare second last version with last version. The reason is we don't store
                            # values for the keys which don't exist.
#                             for (key, value) in last_published_setting1.items():
                            for (key, value) in last_approved_setting0.items():
                                # Check if the key present in the second last version is present in
                                # the latest version.
                                if key not in last_approved_setting1:
#                                     error = error + 'Setting ' + key + ' not present in previous version'
#                                     error = error + '\n'
                                    continue
                                if value != last_approved_setting1[key]:
                                    error = error + 'Setting values not match for -' + key
                                    error = error + '\n'

                            if (len(error) > 0):
                                diff_result = diff_result + config_set + error
                        count = count + 1
                        #if count > 5:
                        #    break;
                pp.pprint('processed')
                pp.pprint(count)
                #if hwtype.startswith('ghost') or hwtype.startswith('falcon'):
                f.write (diff_result)
        except Exception as e:
            errors = 'Exception during diff- ' + str(e)
            result = 'Exception occured while doing diff- ' + str(e)

        if errors == '':
            result = 'Diff finished successfully. Check log file.'

        return Response({'Result':result }, status=status.HTTP_200_OK)

# class ConfigSetDeltaApiView(APIView):
#     # Code for retriving configs for delta //////////
#     def get(self, request):
#
#         return Response({'Result':200 }, status=status.HTTP_200_OK)


class DataExplorerSettingsImportAPIView(APIView):

    def get(self, request, *args, **kwargs):
        userdata = get_user_model(request.user.username)

        request_data = request.QUERY_PARAMS.lists()
        productline = request_data[0][1][0]

        return Response({
            'settings': retrieve_data_explorer_settings(productline),
        }, status=status.HTTP_200_OK)


class DiscardBulkUpdateAPIView(ListModelMixin,
                        mixins.CreateModelMixin,
                        generics.MultipleObjectAPIView):
    def get(self, request, *args, **kwargs):
        config_sets = ConfigSet.objects.filter(category_id=5)

        return Response({'count':len(config_sets)}, status=status.HTTP_200_OK)
