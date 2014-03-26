import re

from django.contrib import admin
from django.contrib.admin.widgets import ManyToManyRawIdWidget, ForeignKeyRawIdWidget
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_unicode
from django.utils.html import escape

from utils import make_field


class EnhancedModelAdminMixin(object):

    def lookup_allowed(self, lookup, *args, **kwargs):
        """
        Allow to do querystring lookups without a sidebar filtering.
            'valid_lookups': specify valid querystring search lookups using
        """
        for valid_lookup in self.valid_lookups:
            if lookup.startswith(valid_lookup):
                return True
        return super(EnhancedModelAdminMixin, self).lookup_allowed(lookup, *args, **kwargs)

class ModelAdmin(admin.ModelAdmin, EnhancedModelAdminMixin):
    """
    You can pass a "_fieldname(:property(:f))" that will be automatically parsed using make_field
    the last :f means "filter_by" will be active
    """

    def __init__(self, *args, **kwargs):

        # do not take over __functions
        r = r'^_([a-zA-Z]\w+)\:?(\w*)\:?([f]*)'

        list_display = list(self.list_display)

        for i, name in enumerate(self.list_display):
            if (not isinstance(name, basestring)):
                continue # not a string, probably a function!
            field = re.search(r, name)
            if field:
                field = list(field.groups())
                name = list(field[:2]) # do not use the 'filter option even if it's there'
                if not name[1]:
                    del name[1] # no attribute
                method_name = '_'+'_'.join(name)
                if self.__dict__.get(method_name):
                    continue # it exists already!
                self.__dict__[method_name] = make_field(*field)
                list_display[i] = method_name

        self.list_display = list_display

        super(ModelAdmin, self).__init__(*args, **kwargs)

"""
TO BE TESTED!
"""
class VerboseForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        try:
            obj = self.rel.to._default_manager.using(self.db).get(**{key: value})
            change_url = reverse(
                "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.object_name.lower()),
                args=(obj.pk,)
            )
            return '&nbsp;<strong><a href="%s">%s</a></strong>' % (change_url, escape(obj))
        except (ValueError, self.rel.to.DoesNotExist):
            return ''

class VerboseManyToManyRawIdWidget(ManyToManyRawIdWidget):
    def label_for_value(self, value):
        values = value.split(',')
        str_values = []
        key = self.rel.get_related_field().name
        for v in values:
            try:
                obj = self.rel.to._default_manager.using(self.db).get(**{key: v})
                x = smart_unicode(obj)
                change_url = reverse(
                    "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.object_name.lower()),
                    args=(obj.pk,)
                )
                str_values += ['<strong><a href="%s">%s</a></strong>' % (change_url, escape(x))]
            except self.rel.to.DoesNotExist:
                str_values += [u'???']
        return u', '.join(str_values)

class ImprovedRawIdFieldsAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in self.raw_id_fields:
            kwargs.pop("request", None)
            type = db_field.rel.__class__.__name__
            if type == "ManyToOneRel":
                kwargs['widget'] = VerboseForeignKeyRawIdWidget(db_field.rel)
            elif type == "ManyToManyRel":
                kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel)
            return db_field.formfield(**kwargs)
        return super(ImprovedRawIdFieldsAdmin, self).formfield_for_dbfield(db_field, **kwargs)


#override of the InlineModelAdmin to support the link in the tabular inline
# http://stackoverflow.com/a/2201828/422670
class LinkedInline(admin.options.InlineModelAdmin):
#    template = "admin/linked.html"
    admin_model_path = None

    def __init__(self, *args):
        super(LinkedInline, self).__init__(*args)
        if self.admin_model_path is None:
            self.admin_model_path = self.model.__name__.lower()

class StackedInline(LinkedInline):
    template = "admin/edit_inline/linked_staked.html"
    show_link = False # not implemented yet! :)

class TabularInline(LinkedInline):
    template = "admin/edit_inline/linked_tabular.html"
    show_link = False

class LinkedStackedInline(StackedInline):
    template = "admin/edit_inline/linked_staked.html"
    show_link = True

class LinkedTabularInline(TabularInline):
    template = "admin/edit_inline/linked_tabular.html"
    show_link = True



    # would be nice to superpower Ta