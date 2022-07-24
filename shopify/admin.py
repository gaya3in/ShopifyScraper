from django.contrib import admin
from shopify.models import Website, Endpoint

# Register your models here.
class EndpointAdmin(admin.TabularInline):
    model = Endpoint

class WebsiteAdmin(admin.ModelAdmin):
    inlines = [EndpointAdmin]
    list_display = ("title", "url", "webType", "switch", "status")
    class Meta:
        model = Website

admin.site.register(Website, WebsiteAdmin)
admin.site.register(Endpoint)