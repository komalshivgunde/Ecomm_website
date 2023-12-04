from django.contrib import admin
from ecomm_app.models import product

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display=['id','name','price','cat','is_active','pimage']
    list_filter=['cat','is_active']


#admin.site.register(product)
admin.site.register(product,ProductAdmin)
