from django.conf.urls import patterns, url, include
from django.conf import settings
from gallery.views import home, register, search, auth, sign_out, create_gallery, \
    ajax_upload, edit_descriptions, check_user_availability, delete_obj


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$',
                           home,
                           name="wis_home"),

                       url(r'^gallery/', include('gallery.urls')),

                       # Register view
                       url(r'^register',
                           register,
                           name="wis_register"),

                       # Search view
                       url(r'^search$',
                           search,
                           name="wis_search"),

                       # Login view
                       url(r'^login$',
                           auth,
                           name="wis_login"),

                       # Logout view
                       url(r'^logout$',
                           sign_out,
                           name="wis_logout"),

                       # Upload view
                       # url(r'^upload$', "gallery.views.upload"),

                       # Creation of a new gallery view
                       url(r'^creation$',
                           create_gallery,
                           name="wis_create"),

                       # For the Django jQuery Upload
                       url(r'^upload$',
                           ajax_upload,
                           name="wis_upload"),

                       # Edit photos description
                       url(r'^edit$',
                           edit_descriptions,
                           name="wis_edit"),

                       # Delete a picture
                       url(r'^delete/(?P<obj_type>[-A-Za-z0-9_]+)/(?P<obj_id>[-A-Za-z0-9_]+)$',
                           delete_obj,
                           name="wis_delete"),

                       # Check username availability view
                       url(r'^checkUser/(?P<username>(.+))$$',
                           check_user_availability,
                           name="wis_check_user"),

                       # Examples:
                       # url(r'^$', 'wis.views.home', name='home'),
                       # url(r'^wis/', include('wis.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       # url(r'^admin/', include(admin.site.urls)),
                       )


if settings.DEBUG:
    urlpatterns += patterns('',
                            url(r'^data/(?P<path>.*)$', 'django.views.static.serve', {
                                'document_root': settings.MEDIA_ROOT,
                                }),
                            url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
                                'document_root': settings.STATIC_ROOT,
                                }),
                            )
