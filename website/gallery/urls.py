from django.conf.urls import patterns, url
from gallery.views import *


urlpatterns = patterns('wis.apps.gallery.views',
                       # User galleries
                       url(r'^(?P<user>[-A-Za-z0-9_]+)$',
                           user_galleries,
                           name="wis_user_gallery"),
                       )

                       # Galleries url
                       url(r'^(?P<user>[-A-Za-z0-9_]+)/(?P<gallery_slug>(.+))$',
                           gallery_home,
                           name="wis_gallery_home"),

