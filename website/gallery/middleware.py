#!/usr/bin/python
#-*- coding: utf8 -*-


class HistoryMiddleware(object):
    """ Middleware in charge of keeping the navigation history of
    the user """

    def process_request(self, request):
        if "history" not in request.session.keys():
            request.session['history'] = list()
        if request.get_full_path() not in ["/login", "/register"]:
            request.session['history'].append(request.get_full_path())
        if len(request.session['history']) > 10:
            request.session['history'].pop(0)
        return None
