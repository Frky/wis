from wis.apps.gallery.models import Gallery


class GalleryManager:

    def __init__(self, slug, owner):
        self.slug = slug
        self.owner = owner

    def get_gallery(self):
        return Gallery.objects.get(slug_name=self.slug, owner=self.owner)

    def get_all_galleries(self):
        return Gallery.objects.get_galleries_with_slug()
