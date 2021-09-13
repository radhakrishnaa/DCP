from rest_framework import fields
from django.core.exceptions import ValidationError

class WritableFieldWithFieldName(fields.WritableField):
    model = None
    target = None
    field = None

    def __init__(self, source=None, read_only=False, required=None,
                 validators=[], error_messages=None, widget=None,
                 default=None, blank=None, model=None):
        super(WritableFieldWithFieldName, self).__init__(source=source, read_only=read_only,
                                                         required=required, validators=validators,
                                                         error_messages=error_messages, widget=widget,
                                                         default=default, blank=blank)
        self.model = model

    def field_from_native(self, data, files, field_name, into):
        if self.read_only:
            return

        try:
            if self.use_files:
                files = files or {}
                native = files[field_name]
            else:
                native = data[field_name]
        except KeyError:
            if self.default is not None and not self.partial:
                # Note: partial updates shouldn't set defaults
                native = self.default
            else:
                if self.required:
                    raise ValidationError(self.error_messages['required'])
                return

        value = self.from_native(native)
        if self.source == '*':
            if value:
                into.update(value)
        else:
            if self.source is None:
                raise ValidationError("Attribute 'source' is required for %s." % field_name)

            if value is None or len(str(value)) == 0:
                obj = None
            else:
                sourcelist = self.source.split('.')
                if len(sourcelist) > 1:
                    target_field = sourcelist[0]
                    query_field = sourcelist[1]

                    self.validate(value)
                    self.run_validators(value)

                    if self.empty(data, target_field) or field_name == target_field:
                        kwargs = {query_field: value}
                        try:
                            obj = self.model.objects.get(**kwargs)
                        except self.model.DoesNotExist:
                            raise ValidationError("%s '%s' doesn't exist!" % (query_field, value))

                        into[target_field] = obj

    def empty(self, data, field_name):
        if field_name not in data or data[field_name] is None or len(str(data[field_name])) == 0:
            return True
        return False