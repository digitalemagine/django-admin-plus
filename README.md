Enhances the django admin with some automagic.

How to use it:

More power to admin tables
==========================

extend admin models from `admin_plus.ModelAdmin` and register through 
`admin_plus.register` in order to benefit from more powerful admin:
 * follow foreign keys to related admin UI



Models autodiscovery
====================

Automatically adds all models to the Admin through an autodiscovery (somehow similar to admin URLS autodiscovery)

Overall Example
===============

Don't forget to add `admin_plus` to your `INSTALLED_APPS`

Then in your `admin.py` file:

```
#!python
import admin_plus
from django.contrib import admin

from yourapp import models as yourapp_models

class MyModelAdmin(admin_plus.ModelAdmin):
    pass

admin_plus.register(admin.site, get_user_model(), MyModelAdmin)

admin_plus.auto_register(admin.site, yourapp_models)
```




V 0.9.0

Initial release out of previous kitchensink project
@TODO: try to improve with django 1.7 new apps config?!