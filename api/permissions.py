import re
import logging

from django.conf import settings as djsettings

from rest_framework import permissions

from api.models import User

logger = logging.getLogger(__name__)

ADMIN_METHODS = ['PUT', 'POST', 'DELETE']


def get_local_username(username):
    return re.sub(r'@motorola.com$', '', username)


def get_user_model(username):
    username = get_local_username(username)
    matching_users = User.objects.filter(username=username)
    if len(matching_users) == 1:
        return matching_users[0]
    if len(matching_users) > 1:
        logger.error('Username "'+username+'" is not unique.')
    return User(username=username)


class IsRoleOrReadOnly(permissions.BasePermission):

    def check_role(self, request, userdata):
        return False

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated():
            if request.method in permissions.SAFE_METHODS:
                return True
            userdata = get_user_model(request.user.username)
            if (userdata is not None and
                    self.check_role(request, userdata)):
                return True
        return False


class IsEditorOrReadOnly(IsRoleOrReadOnly):
    def check_role(self, request, userdata):
        return userdata.editor is True


class IsApproverOrReadOnly(IsRoleOrReadOnly):
    def check_role(self, request, userdata):
        return userdata.approver is True


class IsPublisherOrReadOnly(IsRoleOrReadOnly):
    def check_role(self, request, userdata):
        return userdata.publisher is True


class IsAdminOrReadOnly(IsRoleOrReadOnly):
    def check_role(self, request, userdata):
        return userdata.admin is True


class IsUserAdminOrReadOnly(IsRoleOrReadOnly):
    def check_role(self, request, userdata):
        if userdata.username in djsettings.USERADMINS:
            return True
        return userdata.admin is True


class IsManagerOrReadOnly(IsRoleOrReadOnly):
    def check_role(self, request, userdata):
        return userdata.manager is True
