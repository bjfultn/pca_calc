## Imports for Users
import logging

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField
from functools import reduce
import operator

import datetime

from django.conf import settings
from django.contrib.sites.models import Site
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.core.validators import int_list_validator
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

## User Class & Methods
class UserManager(UserManager):
    pass


class User(AbstractUser):
    email = models.EmailField('email address', blank=True, unique=True)
    data = JSONField(default=dict)
    comment = models.CharField(max_length=300, blank=True, default="")
    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta:
        ordering = ('username',)

    def name(self):
        return self.first_name + " " + self.last_name

    def settings(self, *keys):
        """ Dig for a data setting by array of keys
        """
        try:
            return reduce(operator.getitem, keys, self.data)
        except:
            return None

    def update_settings(self, key, object):
        """ Update a data setting by key
        """
        self.data[key] = object
        self.save(update_fields=['data'])

