from django.contrib import admin
from models import Photo, Gallery


class PhotoAdmin(admin.ModelAdmin):
    list_display = ["id", "thumbnail", "description", "owner", "large_path", "gallery", "place",
                    "uploaded", "created", ]
    list_filter = ["owner", "gallery", "place"]

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()


class GalleryAdmin(admin.ModelAdmin):
    list_display = ["__unicode__", "title", "owner", "description", "public", "place", "created",
                    "slug_name", "count", ]
    list_filter = ["owner", "public", "place", ]

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

admin.site.register(Photo, PhotoAdmin)
admin.site.register(Gallery, GalleryAdmin)