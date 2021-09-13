"""
Basic building blocks for generic class based views.

We don't bind behaviour to http method handlers yet,
which allows mixin classes to be composed in interesting ways.
"""
from __future__ import unicode_literals

from django.http import Http404
from rest_framework.response import Response

import re
import pprint

class ListModelMixin(object):
    """
    List a queryset.
    Should be mixed in with `MultipleObjectAPIView`.
    """
    empty_error = "Empty list and '%(class_name)s.allow_empty' is False."
        
    def list(self, request, *args, **kwargs):
        #pp = pprint.PrettyPrinter(indent=4)
        serializer_fields = self.serializer_class.base_fields
        queryset = self.get_queryset()
        action = ''
        for queryitem in self.request.QUERY_PARAMS.lists():
            if queryitem[0] == 'action':
                action = queryitem[1][0]
            option = queryitem[0].split('.')
            if len(option) > 1:
                oper = option.pop(0)
                for i in range(0, len(option)):
                    fieldpart = option[i]
                    if i == 0 and fieldpart in serializer_fields:
                        # This might not be the most robust way to filter
                        # on API fields that are joins, but is concise and
                        # works well enough.
                        fieldpart = serializer_fields[fieldpart].source
                        fieldpart = re.sub(r'\.id$', '', fieldpart)
                    option[i] = fieldpart.replace('.', '__')
                fieldname = '__'.join(option)
                print 'fieldname: ' + fieldname

                if oper == 'eq':
                    feildvalue = queryitem[1][0]
                    kwargs = {}
                    kwargs[fieldname+'__exact']=feildvalue
                    print kwargs
                    queryset = queryset.filter(**kwargs)
                if oper == 'ne':
                    feildvalue = queryitem[1][0]
                    kwargs = {}
                    kwargs[fieldname+'__exact']=feildvalue
                    print kwargs
                    queryset = queryset.exclude(**kwargs)
                if oper == 'gt':
                    feildvalue = queryitem[1][0]
                    kwargs = {}
                    kwargs[fieldname+'__gt']=feildvalue
                    print kwargs
                    queryset = queryset.filter(**kwargs)
                if oper == 'lt':
                    feildvalue = queryitem[1][0]
                    kwargs = {}
                    kwargs[fieldname+'__lt']=feildvalue
                    print kwargs
                    queryset = queryset.filter(**kwargs)
                if oper == 'ge':
                    feildvalue = queryitem[1][0]
                    kwargs = {}
                    kwargs[fieldname+'__gte']=feildvalue
                    print kwargs
                    queryset = queryset.filter(**kwargs)                        
                if oper == 'le':
                    feildvalue = queryitem[1][0]
                    kwargs = {}
                    kwargs[fieldname+'__lte']=feildvalue
                    print kwargs
                    queryset = queryset.filter(**kwargs)        
                if oper == 'like':
                    feildvalue = queryitem[1][0]
                    kwargs = {}
                    kwargs[fieldname+'__contains']=feildvalue
                    print kwargs
                    queryset = queryset.filter(**kwargs)        
                if oper == 'nlike':
                    feildvalue = queryitem[1][0]
                    kwargs = {}
                    kwargs[fieldname+'__icontains']=feildvalue
                    print kwargs
                    queryset = queryset.filter(**kwargs)
                if oper == 'nul':
                    feildvalue = queryitem[1][0]
                    if feildvalue =='1' or feildvalue =='true':
                        feildvalue = True
                    elif feildvalue =='0' or feildvalue =='false':
                        feildvalue = False    
                    kwargs = {}
                    kwargs[fieldname+'__isnull']=feildvalue
#                     print 'kwargs'
#                     print kwargs
                    queryset = queryset.filter(**kwargs)
#                     print queryset
        if action == 'count':
            count_items = queryset.count()
            count_result = {"count":count_items}
            return Response(count_result)
        else:    
            #The sort below is not used as of now, as we don't pass any sort from the front end
            # and we are using the default sorting provided by the model. 
            sort = self.request.QUERY_PARAMS.get('sort', None)
            qmax = self.request.QUERY_PARAMS.get('max', 100000)
            qoffset = self.request.QUERY_PARAMS.get('offset', 0)
            
            if sort is not None:
                queryset = queryset.order_by(sort)
        
            queryset = queryset[qoffset:int(qmax)+int(qoffset)]         
            
            self.object_list = queryset

            # Default is to allow empty querysets.  This can be altered by setting
            # `.allow_empty = False`, to raise 404 errors on empty querysets.
            allow_empty = self.get_allow_empty()
            if not allow_empty and not self.object_list:
                class_name = self.__class__.__name__
                error_msg = self.empty_error % {'class_name': class_name}
                raise Http404(error_msg)

            # Pagination size is set by the `.paginate_by` attribute,
            # which may be `None` to disable pagination.
            page_size = self.get_paginate_by(self.object_list)
            if page_size:
                packed = self.paginate_queryset(self.object_list, page_size)
                paginator, page, queryset, is_paginated = packed
                serializer = self.get_pagination_serializer(page)
            else:
                serializer = self.get_serializer(self.object_list, many=True)

            return Response(serializer.data)
