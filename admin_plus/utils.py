#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_list import _boolean_icon

def make_field(name, property=None, filterby=False):
    """
    Nice function that allows to get related propertys using the "__" pattern
    """

    if isinstance(name, basestring):
        _name = name.split('__')

    def f(obj):
        instance = obj
        template_str = u'<a href="{url}" title="Go to">{label}</a>'
        if filterby:
            template_str += u'&nbsp;(<a href="{url_filter}" title="Filter by">F</a>)'

        for s in _name:
            obj = getattr(obj, s)

        if obj is None:
            return None

        if property:
            label = getattr(obj, property)
        else:
            try:
                label = obj.__unicode__()
            except: # likely label is a unicode obj already
                label = obj

        id = getattr(obj, 'pk', None)

        if isinstance(label, bool):
            return _boolean_icon(label)

        if not id:
            # this is not a (linkable) objet
            if hasattr(label, '__call__'):
                return label()
            return label

        #url_filter = reverse('admin:'+ obj._meta.__str__().replace('.', '_') + '_changelist')
        url_filter = reverse('admin:'+ instance._meta.__str__().replace('.', '_') + '_changelist')+'?{0}={1}'.format(name, id)
        #filter =
        # @TODO TO BE FINISHED

        # _meta.__str__.replace == obj._meta.app_label + '_' + obj.__class__.__name__.lower()
        url = reverse('admin:'+ obj._meta.__str__().replace('.', '_') + '_change', args=[id])
#            return mark_safe("""<a href="{url}" title="Go to">{label}</a>&nbsp;[<a href="{url_filter}?id__exact={id}" title="filter by">F</a>]""".format(
#                url=url, url_filter=url_filter, id=id, label=label,)
#                )
        return mark_safe(template_str.format(
            url=url, id=id, label=label, url_filter=url_filter)
        )

    f.allow_tags = True
    f.short_description = ':'.join(_name)+(("."+property) if property else "")
    # also to set 'boolean' if it's a boolean
    # would be nice to try ordering by name if there's one! but we do not have access to the object here.
    f.admin_order_field = name

    return f

