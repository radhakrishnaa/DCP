from django.db import models
from django.conf import settings as djsettings
import reversion

class Region(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=80)
    comment = models.CharField(max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        db_table = 'region'
        ordering = ['code']

class Carrier(models.Model):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    comment = models.CharField(max_length=1000, blank=True, null=True)
    old_code = models.CharField(max_length=40, blank=True, null=True)
    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        db_table = 'carrier'
        ordering = ['code']

class Hwtype(models.Model):
    code = models.CharField(max_length=40, unique=True)
    internal_name = models.CharField(max_length=40, blank=True, null=True)
    marketing_name = models.CharField(max_length=80, blank=True, null=True)
    model_number = models.CharField(max_length=40, blank=True, null=True)
    comment = models.CharField(max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return unicode("%s(%s)" % (self.code, self.marketing_name))

    class Meta:
        db_table = 'hwtype'
        ordering = ['code']

# class Delta(models.Model):
#     name = models.CharField(max_length=80, unique=True)
#     comment = models.CharField(max_length=1000, blank=True, null=True)
# 
#     def __unicode__(self):
#         return unicode(self.name)
# 
#     class Meta:
#         db_table = 'delta'
#         ordering = ['name']

class ExtraKey(models.Model):
    code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    comment = models.CharField(max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.code)

    class Meta:
        db_table = 'extra_key'
        ordering = ['code']

class ExtraValue(models.Model):
    value = models.CharField(max_length=100, blank=False, null=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    comment = models.CharField(max_length=100, blank=True, null=True)
    extra_key_id = models.ForeignKey(ExtraKey, on_delete=djsettings.ON_DELETE)
    extra_key_id.db_column = 'extra_key_id'

    def __unicode__(self):
        return unicode(str(self.id))

    class Meta:
        db_table = 'extra_value'
        unique_together = (('value', 'extra_key_id'),)

class SettingCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    comment = models.CharField(max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        db_table = 'setting_category'
        ordering = ['name']

class SettingDef(models.Model):
    category_id = models.ForeignKey(SettingCategory, on_delete=djsettings.ON_DELETE)
    name = models.CharField(max_length=255, unique=True)
    group = models.CharField(max_length=80, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    datatype = models.CharField(max_length=40)
    rules = models.CharField(max_length=1000, blank=True, null=True)
    display_name = models.CharField(max_length=80, blank=True, null=True)
    short_help = models.CharField(max_length=1000, blank=True, null=True)
    category_id.db_column = 'category_id'

    def __unicode__(self):
        return unicode(self.display_name)

    class Meta:
        db_table = 'setting_def'
        ordering = ['group', 'order', 'display_name']

class SettingValue(models.Model):
    setting_def_id = models.ForeignKey(SettingDef, on_delete=djsettings.ON_DELETE)
    value = models.CharField(max_length=8000, blank=True, null=True)
    setting_def_id.db_column = 'setting_def_id'

    def __unicode__(self):
        return unicode(str(self.id))

    class Meta:
        db_table = 'setting_value'

class ConfigSet(models.Model):
    region_id = models.ForeignKey(Region, blank=True, null=True, on_delete=djsettings.ON_DELETE)
    carrier_id = models.ForeignKey(Carrier, blank=True, null=True, on_delete=djsettings.ON_DELETE)
    hwtype_id = models.ForeignKey(Hwtype, blank=True, null=True, on_delete=djsettings.ON_DELETE)
    extra_value_id = models.ForeignKey(ExtraValue, blank=True, null=True, on_delete=djsettings.ON_DELETE)
    category_id = models.ForeignKey(SettingCategory, on_delete=djsettings.ON_DELETE)
    fallback_id = models.ForeignKey('self', blank=True, null=True, on_delete=djsettings.ON_DELETE)
    comment = models.CharField(max_length=1000, blank=True, null=True)
    delta_name = models.CharField(max_length=500, null=True, blank=True)
    region_id.db_column = 'region_id'
    carrier_id.db_column = 'carrier_id'
    hwtype_id.db_column = 'hwtype_id'
    category_id.db_column = 'category_id'
    fallback_id.db_column = 'fallback_id'
    extra_value_id.db_column = 'extra_value_id'
    #delta_id.db_column = 'delta_id'

    def __unicode__(self):
        return unicode(
            (self.hwtype_id.code + '.'
                if self.hwtype_id is not None else '') +
            (self.carrier_id.code + '.'
                if self.carrier_id is not None else '') +
            (self.region_id.code
                if self.region_id is not None else 'Global') +
            ' (' + self.category_id.name + ')' )

    class Meta:
        db_table = 'config_set'
#         ordering = ['category_id', 'hwtype_id', 'carrier_id', 'region_id', 'delta_name']
        ordering = ['category_id', 'hwtype_id', 'carrier_id', 'region_id',]
#         unique_together = (('category_id', 'hwtype_id',
#             'carrier_id', 'region_id'), ('category_id', 'delta_name'), )
        unique_together = (('category_id', 'hwtype_id',
             'carrier_id', 'region_id', 'delta_name','extra_value_id'), )
#         unique_together = (('category_id', 'hwtype_id',
#              'carrier_id', 'region_id'), )
class User(models.Model):
    username = models.CharField(max_length=40, unique=True)
    email = models.CharField(max_length=80, blank=True, null=True)
    display_name = models.CharField(max_length=40, blank=True, null=True)
    editor = models.BooleanField(default=0)
    approver = models.BooleanField(default=0)
    publisher = models.BooleanField(default=0)
    admin = models.BooleanField(default=0)
    manager = models.BooleanField(default=0)

    def __unicode__(self):
        return self.username

    class Meta:
        db_table = 'user'
        ordering = ['username']

class ConfigVersion(models.Model):
    version_number = models.IntegerField()
    config_set_id = models.ForeignKey(ConfigSet, on_delete=djsettings.ON_DELETE)
    setting_value = models.ManyToManyField(SettingValue, blank=True, null=True, through='ConfigSetting')
    last_editor_id = models.ForeignKey(User, related_name='config_version_last_editor', blank=True, null=True, on_delete=djsettings.ON_DELETE)
    last_edited = models.DateTimeField(blank=True, null=True)
    committer_id = models.ForeignKey(User, related_name='config_version_committer', blank=True, null=True, on_delete=djsettings.ON_DELETE)
    committed = models.DateTimeField(blank=True, null=True)
    approver_id = models.ForeignKey(User, related_name='config_version_approver', blank=True, null=True, on_delete=djsettings.ON_DELETE)
    approved = models.DateTimeField(blank=True, null=True)
    publisher_id = models.ForeignKey(User, related_name='config_version_publisher', blank=True, null=True, on_delete=djsettings.ON_DELETE)
    published = models.DateTimeField(blank=True, null=True)
    fallback_id = models.ForeignKey('self', blank=True, null=True, on_delete=djsettings.ON_DELETE)
    comment = models.CharField(max_length=1000, blank=True, null=True)
    
    config_set_id.db_column = 'config_set_id'
    fallback_id.db_column = 'fallback_id'
    last_editor_id.db_column = 'last_editor_id'
    committer_id.db_column = 'committer_id'
    approver_id.db_column = 'approver_id'
    publisher_id.db_column = 'publisher_id'

    def __unicode__(self):
        return unicode(str(self.id))

    class Meta:
        db_table = 'config_version'

class ConfigSetting(models.Model):
    config_version_id = models.ForeignKey(ConfigVersion, on_delete=djsettings.ON_DELETE)
    setting_value_id = models.ForeignKey(SettingValue, on_delete=djsettings.ON_DELETE)

    config_version_id.db_column = 'config_version_id'
    setting_value_id.db_column = 'setting_value_id'

    def __unicode__(self):
        return unicode(str(self.id))

    class Meta:
        db_table = 'config_setting'

class EnvTransform(models.Model):
    order = models.IntegerField()
    env_pat = models.CharField(max_length=255)
    hwtype_pat = models.CharField(max_length=255)
    carrier_region_pat = models.CharField(max_length=255)
    extra_level_pat = models.CharField(max_length=255, default='.*')
    setting_name_pat = models.CharField(max_length=1000)
    value_pat = models.CharField(max_length=1000)
    value_sub = models.CharField(max_length=8000, blank=True, null=True)
    comment = models.CharField(max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return unicode(str(self.id))

    class Meta:
        db_table = 'env_transform'
        ordering = ['order', 'env_pat']

class CloudEnv(models.Model):
    PROD = 'prod'
    SDC = 'sdc'
    QA = 'qa'
    ENV_TYPE_CHOICES = (
        (PROD, 'Production'),
        (SDC, 'Staging'),
        (QA, 'QA'),
    )
    order = models.IntegerField(blank=True, null=True)
    short_name = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=40, unique=True)
    network_name = models.CharField(max_length=40, unique=True)
    env_type = models.CharField(max_length=8, choices=ENV_TYPE_CHOICES)
    comment = models.CharField(max_length=1000, blank=True, null=True)

    def __unicode__(self):
        return self.short_name

    class Meta:
        db_table = 'cloud_env'
        ordering = ['order', 'short_name']

class RegionAdmin(reversion.VersionAdmin):
    pass

class CarrierAdmin(reversion.VersionAdmin):
    pass

class HwtypeAdmin(reversion.VersionAdmin):
    pass

class SettingCategoryAdmin(reversion.VersionAdmin):
    pass

class SettingDefAdmin(reversion.VersionAdmin):
    pass

class SettingValueAdmin(reversion.VersionAdmin):
    pass

class ConfigSettingAdmin(reversion.VersionAdmin):
    pass

class ConfigVersionAdmin(reversion.VersionAdmin):
    pass

class UserAdmin(reversion.VersionAdmin):
    pass

class ConfigSetAdmin(reversion.VersionAdmin):
    pass

class EnvTransformAdmin(reversion.VersionAdmin):
    pass

class CloudEnvAdmin(reversion.VersionAdmin):
    pass
