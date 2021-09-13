from rest_framework import fields
from django.conf import settings as djsettings

from api.models import *
from api.fields import WritableFieldWithFieldName
from rest_framework import serializers
from django.core.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)

class ExtraKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraKey

class ExtraValueSerializer(serializers.ModelSerializer):
    extra_key_code = WritableFieldWithFieldName(source='extra_key_id.code', required=False, model=ExtraKey)
    class Meta:
        model = ExtraValue

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region

class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier

class SettingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingCategory

class SettingDefSerializer(serializers.ModelSerializer):
    category_name = WritableFieldWithFieldName(source='category_id.name', required=False, model=SettingCategory)
    category_id = WritableFieldWithFieldName(source='category_id.id', required=False, model=SettingCategory)
    class Meta:
        model = SettingDef
        fields = ('id', 'category_id', 'category_name', 'name', 'group', 'order', 'datatype', 'rules', 'display_name', 'short_help')
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        
class HwtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hwtype

class EnvTransformSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvTransform

class CloudEnvSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloudEnv

class ConfigSetSerializer(serializers.ModelSerializer):
    extra_key = WritableFieldWithFieldName(source='extra_value_id.extra_key_id.code', required=False, model=ExtraKey)
    extra_value = WritableFieldWithFieldName(source='extra_value_id.value', required=False, model=ExtraValue)
    extra_value_id = WritableFieldWithFieldName(source='extra_value_id.id', required = False, model= ExtraValue)
    extra_value_name = WritableFieldWithFieldName(source='extra_value_id.name', required = False, model= ExtraValue)
    region = WritableFieldWithFieldName(source='region_id.code', required=False, model=Region)
    carrier = WritableFieldWithFieldName(source='carrier_id.code', required=False, model=Carrier)
    hwtype = WritableFieldWithFieldName(source='hwtype_id.code', required=False, model=Hwtype)
    category_name = WritableFieldWithFieldName(source='category_id.name', required=False, model=SettingCategory)
    category_id = WritableFieldWithFieldName(source='category_id.id', required=False, model=SettingCategory)

    def restore_object(self, attrs, instance=None):
        if instance is not None:
            for field_name, value in attrs.items():
                setattr(instance, field_name, value)
            return instance
        return ConfigSet(**attrs)

    class Meta:
        model = ConfigSet
        fields = ('id','extra_key','extra_value','extra_value_id','extra_value_name','region', 'carrier', 'hwtype', 'category_id',  'category_name', 'fallback_id', 'comment', 'delta_name')

class ConfigVersionSerializer(serializers.ModelSerializer):
    last_edited = fields.DateTimeField(
        source='last_edited', required=False,
        format=djsettings.DATETIME_FORMAT)
    last_editor = WritableFieldWithFieldName(
        source='last_editor_id.username',
        required=False, model=User)
    committed = fields.DateTimeField(
        source='committed', required=False,
        format=djsettings.DATETIME_FORMAT)
    committer = WritableFieldWithFieldName(
        source='committer_id.username',
        required=False, model=User)
    approved = fields.DateTimeField(
        source='approved', required=False,
        format=djsettings.DATETIME_FORMAT)
    approver = WritableFieldWithFieldName(
        source='approver_id.username',
        required=False, model=User)
    published = fields.DateTimeField(
        source='published', required=False,
        format=djsettings.DATETIME_FORMAT)
    publisher = WritableFieldWithFieldName(
        source='publisher_id.username',
        required=False, model=User)

    def restore_object(self, attrs, instance=None):
        if instance is not None:
            for field_name, value in attrs.items():
                setattr(instance, field_name, value)
            return instance

        return ConfigVersion(**attrs)

    class Meta:
        model = ConfigVersion
        fields = ('id', 'version_number', 'config_set_id', 'last_editor', 'last_edited', 'committer', 'committed', 'approver', 'approved', 'publisher', 'published', 'fallback_id', 'comment')

class ConfigSettingsSerializer(ConfigVersionSerializer):
    settings = serializers.Field(source='extra.settings');
    hwtype = serializers.Field(source='extra.hwtype');
    carrier = serializers.Field(source='extra.carrier');
    region = serializers.Field(source='extra.region');
    delta_name = serializers.Field(source='extra.delta_name');
    fallback = serializers.Field(source='extra.fallback');
    extra_key = serializers.Field(source='config_set_id.extra_value_id.extra_key_id.code');
    extra_value = serializers.Field(source='config_set_id.extra_value_id.value');

    class Meta:
        model = ConfigVersion
        fields = ConfigVersionSerializer.Meta.fields + ('settings',
            'hwtype', 'carrier', 'region', 'delta_name','extra_key','extra_value','fallback')

class SettingValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingValue


# class DeltaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Delta