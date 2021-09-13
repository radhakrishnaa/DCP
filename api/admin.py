from django.contrib import admin

from api import models

admin.site.register(models.Region, models.RegionAdmin)
admin.site.register(models.Carrier, models.CarrierAdmin)
admin.site.register(models.Hwtype, models.HwtypeAdmin)
admin.site.register(models.SettingCategory, models.SettingCategoryAdmin)
admin.site.register(models.SettingDef, models.SettingDefAdmin)
admin.site.register(models.SettingValue, models.SettingValueAdmin)
admin.site.register(models.ConfigSetting, models.ConfigSettingAdmin)
admin.site.register(models.ConfigVersion, models.ConfigVersionAdmin)
admin.site.register(models.User, models.UserAdmin)
admin.site.register(models.ConfigSet, models.ConfigSetAdmin)
admin.site.register(models.EnvTransform, models.EnvTransformAdmin)
admin.site.register(models.CloudEnv, models.CloudEnvAdmin)
