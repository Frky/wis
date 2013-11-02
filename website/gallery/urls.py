from django.conf.urls import patterns, url

from gallery import views


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<question_id>\d+)/$', views.detail, name='details'),
    url(r'^(?P<question_id>\d+)/results$', views.results, name='results'),
    url(r'^(?P<question_id>\d+)/vote$', views.vote, name='vote'),
)
