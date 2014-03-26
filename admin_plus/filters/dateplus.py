"""
Custom DateField filter with more smart options
"""
import datetime

from django.db import models
from django.utils import timezone
#from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
from django.contrib.admin.filters import (DateFieldListFilter, FieldListFilter)

def get_now():
    now = timezone.now()
    # When time zone support is enabled, convert "now" to the user's time
    # zone so Django's definition of "Today" matches what the user expects.
    if now.tzinfo is not None:
        current_tz = timezone.get_current_timezone()
        now = now.astimezone(current_tz)
        if hasattr(current_tz, 'normalize'):
            # available for pytz time zones
            now = current_tz.normalize(now)

    return now

class DatePlusFieldListFilter(DateFieldListFilter):

    PAST_24H = 'past_24h'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super(DatePlusFieldListFilter, self).__init__(
            field, request, params, model, model_admin, field_path)

        now = get_now()

        if isinstance(field, models.DateTimeField):
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:       # field is a models.DateField
            today = now.date()
        tomorrow = today + datetime.timedelta(days=1)
        yesterday = today - datetime.timedelta(days=1)

        self.lookup_kwarg_since = '%s__gte' % field_path
        self.lookup_kwarg_until = '%s__lt' % field_path
        self.links = (
            (_('Any date'), {}),
            (_('Today'), {
                self.lookup_kwarg_since: str(today),
                self.lookup_kwarg_until: str(tomorrow),
            }),
            (_('Past 24 hours'), {
                #self.lookup_kwarg_since: str(now - datetime.timedelta(days=1))#,
                #self.lookup_kwarg_until: str(now),
                self.lookup_kwarg_since: self.PAST_24H
            }),
            (_('Yesterday'), {
                self.lookup_kwarg_since: str(yesterday),
                self.lookup_kwarg_until: str(today),
            }),
            (_('Past 7 days'), {
                self.lookup_kwarg_since: str(today - datetime.timedelta(days=7)),
                self.lookup_kwarg_until: str(tomorrow),
            }),
            (_('This month'), {
                self.lookup_kwarg_since: str(today.replace(day=1)),
                self.lookup_kwarg_until: str(tomorrow),
            }),
            (_('Past 30 days'), {
                self.lookup_kwarg_since: str(today - datetime.timedelta(days=30)),
                self.lookup_kwarg_until: str(tomorrow),
            }),
            (_('This year'), {
                self.lookup_kwarg_since: str(today.replace(month=1, day=1)),
                self.lookup_kwarg_until: str(tomorrow),
            }),
        )

    def queryset(self, request, queryset):
        if self.used_parameters.get('datetime__gte') == self.PAST_24H:
            # make it now... NOW!
            now = get_now()
            params = {
                self.lookup_kwarg_since: str(now - datetime.timedelta(days=1)),
                self.lookup_kwarg_until: str(now)
            }
        else:
            # no need to copy, we don't modify
            params = self.used_parameters

        return queryset.filter(**params)

# register filter will replace the existing one
FieldListFilter.register(
    lambda f: isinstance(f, models.DateField), DatePlusFieldListFilter, take_priority=True)

# registering the filter for only this specific filter using a boolean option "date_plus_filter" on the model
#FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'date_plus_filter', False),
#                               IsLiveFilterSpec))