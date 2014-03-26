from django.conf import settings
from options import ModelAdmin
from django.db.models.base import ModelBase
from django.core.exceptions import ImproperlyConfigured
from django.contrib.admin.sites import AlreadyRegistered

#from django.contrib.admin.sites import AdminSite as OriginalAdminSite

#class AdminSite(OriginalAdminSite):
def register(site, model_or_iterable, admin_class=None, **options):
    """
    Registers the given model(s) with the given admin class.

    The model(s) should be Model classes, not instances.

    If an admin class isn't given, it will use ModelAdmin (the default
    admin options). If keyword arguments are given -- e.g., list_display --
    they'll be applied as options to the admin class.

    If a model is already registered, this will raise AlreadyRegistered.

    If a model is abstract, this will raise ImproperlyConfigured.
    """
    if not admin_class:
        #SF: use our own ModelAdmin
        admin_class = ModelAdmin

    if isinstance(model_or_iterable, ModelBase):
        model_or_iterable = [model_or_iterable]
    for model in model_or_iterable:
        if model._meta.abstract:
            raise ImproperlyConfigured('The model %s is abstract, so it '
                    'cannot be registered with admin.' % model.__name__)

        if model in site._registry:
            raise AlreadyRegistered('The model %s is already registered' % model.__name__)

        # If we got **options then dynamically construct a subclass of
        # admin_class with those **options.
        if options:
            # For reasons I don't quite understand, without a __module__
            # the created class appears to "live" in the wrong place,
            # which causes issues later on.
            options['__module__'] = __name__
            admin_class = type("%sAdmin" % model.__name__, (admin_class,), options)

        # Validate (which might be a no-op)
        # SF: should modify validate to skip make_field fields
        try:
            try:
                #django 1.5
                # Don't import the humongous validation code unless required
                if admin_class and settings.DEBUG:
                    from django.contrib.admin.validation import validate
                    validate(admin_class, model)
#                else:
#                    validate = lambda model, adminclass: None
            except:
                # django 1.6
                admin_class.validate(model)
        except ImproperlyConfigured as e:
            """
            Little issue with validation here.

            All my special '_somthing' modules will raise an "ImproperlyConfigured"
            error, coming from "validate_SMTG" eg.
                `validate_list_display` in django.contrib.admin.validation
            But I have no structured way to understand if it's because it starts with '_'
            so I should rewrite all validators OR find a way to detect only them...

            Maybe the new GSoC validation framework will change something in 1.7
            """
            pass

        # Instantiate the admin class to save in the registry
        site._registry[model] = admin_class(model, site)


def auto_register(site, module):
    """
    Automagically add every model from module to the admin!
    """
    from django.db import models as django_models

    for model in dir(module):
        model = module.__dict__[model]
        if isinstance(model, django_models.base.ModelBase):
            if model not in site._registry: # avoid double registration
                if not model._meta.abstract:
                    register(site, model)
        else:
            pass