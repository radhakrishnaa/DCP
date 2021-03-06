import logging
from django.db import models
from django.contrib.auth.models import User
import reversion

logger = logging.getLogger(__name__)


class UserProfile(models.Model):
    """Custom user profile to support object-level access control"""
    ROLE_CHOICES = (
        ('R', 'Readonly'),
        ('C', 'Creator'),
        ('A', 'Approver'),
        ('S', 'Superuser')
    )
    user = models.OneToOneField(User)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default='R')
    products = models.CharField(max_length=50, blank=True)
    carriers = models.CharField(max_length=50, blank=True)
    languages = models.CharField(max_length=25, blank=True)
    regions = models.CharField(max_length=25, blank=True)

    def __unicode__(self):
        return self.user.username

    def get_role(self):
        return self.role

    def get_products(self):
        return self.products.split(',') if self.products else []

    def get_carriers(self):
        return self.carriers.split(',') if self.carriers else []

    def get_languages(self):
        return self.languages.split(',') if self.languages else []

    def get_regions(self):
        return self.regions.split(',') if self.regions else []

    def to_hash(self):
        profile = {
            'username' : self.user.username,
            'role' : self.get_role(),
            'products' : self.get_products(),
            'carriers' : self.get_carriers(),
            'languages' : self.get_languages(),
            'regions' : self.get_regions()
        }
        return profile

    def isSuperuser(self):
        return self.role == 'S'


class UpgradePathStatus(models.Model):
    """Table for keeping track of Upgrade Path approval status"""
    APPROVAL_STATE_CHOICES = (      # steps in approval workflow state
        ('INVALID', 'INVALID'),
        ('DRAFT', 'EDITABLE'),
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
        ('PUBLISHED', 'PUBLISHED')
    )
    NEXT_ACTIONS = {                # allowed actions on current state
        'INVALID' :  ['EDITSAVE'],
        'DRAFT' :  ['NEWVERSION', 'REQUEST_APPROVAL'],
        'NEWVERSION' : ['EDITSAVE', 'CANCEL'],
        'PENDING' :  ['APPROVE', 'CANCEL'],
        'APPROVED' :  ['PUBLISH', 'CANCEL'],
        'PUBLISHED' :  ['RUN', 'STOP', 'NEWVERSION']
    }
    NEXT_STATE_AFTER_ACTION = {     # new state after action is applied to current state
        'INVALID/EDITSAVE' : 'DRAFT',
        'DRAFT/EDITSAVE' : 'DRAFT',
        'DRAFT/REQUEST_APPROVAL' : 'PENDING',
        'PENDING/APPROVE' : 'APPROVED',
        'PENDING/CANCEL' : 'DRAFT',
        'APPROVED/PUBLISH' : 'PUBLISHED',
        'APPROVED/CANCEL' : 'DRAFT',
        'PUBLISHED/NEWVERSION' : 'NEWVERSION',
        'PUBLISHED/RUN' : 'PUBLISHED',
        'PUBLISHED/STOP' : 'PUBLISHED',
        'DRAFT/NEWVERSION' : 'NEWVERSION',
        'NEWVERSION/EDITSAVE' : 'DRAFT',
        'NEWVERSION/CANCEL' : 'DRAFT',
    }
    guid = models.CharField(max_length=50, blank=False)
    revision = models.CharField(max_length=25, blank=True)
    state = models.CharField(max_length=20, choices=APPROVAL_STATE_CHOICES, default='DRAFT')
    created_on = models.DateField(auto_now_add=True)
    modified_on = models.DateField(auto_now=True)

    def __unicode__(self):
        return str(self.to_hash())

    def to_hash(self):
        status = {
            'guid' : self.guid,
            'revision' : self.revision,
            'state' : self.state,
            'created_on' : str(self.created_on),
            'modified_on' : str(self.modified_on)
        }
        return status

    def next_actions(self):
        return self.NEXT_ACTIONS[self.state]

    def apply_next_action(self, action, user, role):
        logger.debug("apply_next_action(): action=%s, guid=%s, user=%s, role=%s" % (action, self.guid, user, role))
        # @TODO: Enforce role-based access!!!
        currState = self.state        
        if currState+'/'+action in self.NEXT_STATE_AFTER_ACTION:
            self.state = self.NEXT_STATE_AFTER_ACTION[currState+'/'+action]
            self.save()
            logger.debug("Changed state of UpgradePath %s from %s to %s" % (self.guid, currState, self.state))
            return self.state
        else:
            return currState

class UpgradePath(models.Model):
    guid       = models.CharField('GUID generated by upgrade service', primary_key=True, max_length=100)
    bvs        = models.CharField('Source/Target', max_length=1024)
    pojo       = models.TextField('JSON', max_length=48000)
    created_on = models.DateTimeField('Created On', auto_now_add=True)
    updated_on = models.DateTimeField('Last Modified', auto_now=True)

reversion.register(UpgradePath)

class UpgradePathAdmin(reversion.VersionAdmin):
    list_display = ('bvs',)
    date_hierarchy = 'created_on'
    actions = None
    history_latest_first = True
    ignore_duplicate_revisions = True
    search_fields = ['guid', 'bvs']
    pass

from django.contrib import admin
admin.site.register(UpgradePath, UpgradePathAdmin)
