import json
import os
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

from gallery.models import *
from gallery.forms import *
from gallery.messages import ERROR_PERM, ERROR_AUTH, SUCCESS_AUTH, SUCCESS_LOGOUT, SUCCESS_GALLERY_CREATION, \
    ERROR_ACCESS_GALLERY, SUCCESS_ACCESS_GALLERY, SUCCESS_EDIT

context = dict()
context['loginForm'] = UserForm()


def edit_descriptions(request):

    # Verification of permissions
    if not request.user.is_authenticated or str(request.user) == "AnonymousUser":
        return HttpResponseBadRequest(ERROR_PERM)
    elif request.user.username != request.session["gallery_owner"]:
        return HttpResponseBadRequest(ERROR_PERM)

    template_name = "gallery/edit_descriptions.html"

    gallery_slug = request.session['gallery']
    context['gallery_owner'] = request.user
    context["gallery_slug"] = gallery_slug
    context["photos"] = Photo.objects.filter(gallery=Gallery.objects.get(owner=User.objects.get(
        username=request.session["gallery_owner"]),
        slug_name=gallery_slug))

    return render(request, template_name, context)


def delete_obj(request, obj_type, obj_id):
    if ContentType.objects.get(model=obj_type) == ContentType.objects.get_for_model(Photo):
        photo = Photo.objects.get(pk=obj_id)
        photo.remove()

    return HttpResponse('')


def gallery_home(request, user, gallery_slug):

    template_name = "gallery/gallery.html"

    request.session['gallery'] = gallery_slug
    request.session['gallery_owner'] = user

    owner = User.objects.get(username=user)
    gallery = Gallery.objects.get(slug_name=gallery_slug, owner=owner)

    context["gallery"] = gallery
    context['gallery_owner'] = user
    context["gallery_slug"] = request.session['gallery']
    context["photos"] = Photo.objects.filter(gallery=gallery)

    if user + gallery_slug not in request.session.keys():
        request.session[user + gallery_slug] = False

    if owner == request.user:
        context['isOwner'] = True
        request.session[user + gallery_slug] = True
    else:
        context['isOwner'] = False

    if gallery.public:
        request.session[user + gallery_slug] = True

    context['canView'] = request.session[user + gallery_slug]

    # if true, the gallery has been edited
    if request.method == "POST":

        if request.POST['type'] == "edit":
            if request.user != owner:
                messages.error(request, ERROR_PERM)
            else:
                # Editing gallery name
                setattr(gallery, 'title', request.POST['gallery_name'])
                gallery.save()

                # Editing image description and place
                for input, val in request.POST.items():
                    if input.endswith(".desc"):
                        photo_id = input.replace(".desc", "")
                        photo = Photo.objects.get(pk=photo_id)
                        if photo.description != val:
                            setattr(photo, 'description', val)
                            photo.save()
                    elif input.endswith(".place"):
                        photo_id = input.replace(".place", "")
                        photo = Photo.objects.get(pk=photo_id)
                        if photo.place != val:
                            setattr(photo, 'place', val)
                            photo.save()
                messages.success(request, SUCCESS_EDIT)
        elif request.POST['type'] == "password":
            if request.POST['password'] == gallery.password:
                request.session[user + gallery_slug] = True
                messages.success(request, SUCCESS_ACCESS_GALLERY)
            else:
                messages.error(request, ERROR_ACCESS_GALLERY)

        return redirect("wis_gallery_home", user, gallery.slug_name)

    return render(request, template_name, context)


def user_galleries(request, user):
    template_name = "gallery/user_galleries.html"

    context['isOwner'] = (user == str(request.user))

    context['galleries'] = Gallery.objects.filter(owner=User.objects.get(username=user))

    return render(request, template_name, context)


def home(request):
    template_name = "gallery/home.html"

    context["title"] = "WIS - Welcome"
    context["searchForm"] = SearchForm(json.dumps(Gallery.objects.get_galleries_with_slug()))

    return render(request, template_name, context)


@csrf_exempt
def search(request):
    gallery_to_go = dict(request.POST)

    data = {'redirect': "/gallery/{}/{}".format(gallery_to_go['owner'].pop(), gallery_to_go['slug'].pop())}

    return HttpResponse(json.dumps(data), mimetype='application/json')


def create_gallery(request):
    template_name = "gallery/create_gallery.html"

    form = GalleryForm(request.POST or None)

    if form.is_valid():
        data = form.cleaned_data
        new_gallery = Gallery(title=data['title'],
                              description=data['description'],
                              public=data['public'],
                              password=data['password'],
                              owner=request.user,
                              place=data['place'])
        new_gallery.save()
        messages.success(request, SUCCESS_GALLERY_CREATION)
        return redirect("wis_user_gallery", request.user.username)
    else:
        context['form'] = form

    return render(request, template_name, context)


def auth(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                context['auth'] = True
                messages.success(request, SUCCESS_AUTH)
            else:
                context['auth'] = False
                messages.error(request, ERROR_AUTH)
        else:
            context['auth'] = False
            messages.error(request, ERROR_AUTH)
        context['username'] = username

        # META['HTTP_REFERER'].replace(request.META["HTTP_ORIGIN"], ""))
        # return redirect(request.session['history'][-1])
        return redirect("wis_home")

    else:
        return HttpResponse(status=404)


def sign_out(request):

    logout(request)

    messages.success(request, SUCCESS_LOGOUT)

    return redirect("wis_home")


def register(request):

    template_name = "gallery/register.html"

    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        new_user = form.save()
        user = authenticate(username=request.POST['username'], password=request.POST['password1'])
        login(request, user)
        messages.success(request, SUCCESS_AUTH)
        # return redirect(request.session['history'][-1])
        return redirect("wis_home")
    # request.session['redirect'])
    else:
        context['form'] = form
        return render(request, template_name, context)


def upload(request):

    template_name = "gallery/upload.html"
    context['canUpload'] = False

    if str(request.user) == "AnonymousUser":
        messages.error(request, ERROR_PERM)
    elif request.session['gallery_owner'] != str(request.user):
        context['msg'] = ERROR_PERM
    else:
        context['canUpload'] = True
        if request.method == "POST":
            form = UploadImage(request.POST, request.FILES)
            if form.is_valid():
                data = form.cleaned_data
                new_img = Photo(large_path=request.FILES['img'],
                                description=data['description'],
                                place=data['place'],
                                gallery=Gallery.objects.get(slug_name=data['gallery_slug'],
                                                            owner=request.user),
                                owner=request.user)
                new_img.save()
            else:
                context['msg'] = "ERROR"
        else:
            if request.session['gallery'] is None:
                context['msg'] = "Error : no gallery"
            else:
                context['form'] = UploadImage(initial={'gallery_slug': request.session['gallery']})

    return render(request, template_name, context)


def ajax_upload(request):
    """
    ## View for file uploads ##

    It does the following actions:
        - displays a template if no action have been specified
        - upload a file into unique temporary directory
                unique directory for an upload session
                    meaning when user opens up an upload page, all upload actions
                    while being on that page will be uploaded to unique directory.
                    as soon as user will reload, files will be uploaded to a different
                    unique directory
        - delete an uploaded file

    ## How Single View Multi-functions ##

    If the user just goes to a the upload url (e.g. '/upload/'), the request.method will be "GET"
        Or you can think of it as request.method will NOT be "POST"
    Therefore the view will always return the upload template

    If on the other side the method is POST, that means some sort of upload action
    has to be done. That could be either uploading a file or deleting a file

    For deleting files, there is the same url (e.g. '/upload/'), except it has an
    extra query parameter. Meaning the url will have '?' in it.
    In this implementation the query will simply be '?f=filename_of_the_file_to_be_removed'

    If the request has no query parameters, file is being uploaded.

    """

    # used to generate random unique id
    import uuid

    # settings for the file upload
    #   you can define other parameters here
    #   and check validity late in the code
    options = {
        # the maximum file size (must be in bytes)
        "maxfilesize": 2 * 2 ** 60,  # 6 Mb
        # the minimum file size (must be in bytes)
        "minfilesize": 1 * 2 ** 10,  # 1 Kb
        # the file types which are going to be allowed for upload
        #   must be a mimetype
        "acceptedformats": (
            "image/jpeg",
            "image/png",
            )
    }

    if not request.user.is_authenticated or str(request.user) == "AnonymousUser":
        messages.error(request, ERROR_PERM)
        # return redirect(request.session['history'][-2])
        return redirect("wis_home")
    elif request.user.username != request.session["gallery_owner"]:
        messages.error(request, ERROR_PERM)
        # return redirect(request.session['history'][-2])
        return redirect("wis_home")

    # POST request
    #   meaning user has triggered an upload action
    if request.method == 'POST':
        # figure out the path where files will be uploaded to
        # PROJECT_ROOT is from the settings file
        temp_path = "data/upload"

        # if 'f' query parameter is not specified
        # file is being uploaded
        if not ("f" in request.GET.keys()):  # upload file

            # make sure some files have been uploaded
            if not request.FILES:
                return HttpResponseBadRequest('Must upload a file')

            # make sure unique id is specified - VERY IMPORTANT
            # this is necessary because of the following:
            #       we want users to upload to a unique directory
            #       however the uploader will make independent requests to the server
            #       to upload each file, so there has to be a method for all these files
            #       to be recognized as a single batch of files
            #       a unique id for each session will do the job
            if not request.POST[u"uid"]:
                return HttpResponseBadRequest("UID not specified.")
                # if here, uid has been specified, so record it
            uid = request.POST[u"uid"]

            # update the temporary path by creating a sub-folder within
            # the upload folder with the uid name
            temp_path = os.path.join(temp_path, request.user.username)

            # get the uploaded file
            file = request.FILES[u'files[]']

            # initialize the error
            # If error occurs, this will have the string error message so
            # uploader can display the appropriate message
            error = False

            # check against options for errors

            # file size
            if file.size > options["maxfilesize"]:
                error = "maxFileSize"
            if file.size < options["minfilesize"]:
                error = "minFileSize"
                # allowed file type
            if file.content_type not in options["acceptedformats"]:
                error = "acceptFileTypes"

            # the response data which will be returned to the uploader as json
            response_data = {
                "name": file.name,
                "size": file.size,
                "type": file.content_type
            }

            # if there was an error, add error message to response_data and return
            if error:
                # append error message
                response_data["error"] = error
                # generate json
                response_data = json.dumps([response_data])
                # return response to uploader with error
                # so it can display error message
                return HttpResponse(response_data, mimetype='application/json')

            # make temporary dir if not exists already
            if not os.path.exists(temp_path):
                os.makedirs(temp_path)

            # get the absolute path of where the uploaded file will be saved
            # all add some random data to the filename in order to avoid conflicts
            # when user tries to upload two files with same filename
            filename = os.path.join(temp_path, str(uuid.uuid4()) + file.name)
            # open the file handler with write binary mode
            destination = open(filename, "wb+")
            # save file data into the disk
            # use the chunk method in case the file is too big
            # in order not to clutter the system memory
            # for chunk in file.chunks():
            #    destination.write(chunk)
                # close the file
            destination.close()

            new_img = Photo(large_path=file,
                            gallery=Gallery.objects.get(slug_name=request.POST['gallery_slug'],
                                                        owner=request.user),
                            owner=request.user)
            new_img.save()

            # here you can add the file to a database,
            #                           move it around,
            #                           do anything,
            #                           or do nothing and enjoy the demo
            # just make sure if you do move the file around,
            # then make sure to update the delete_url which will be send to the server
            # or not include that information at all in the response...

            # allows to generate properly formatted and escaped url queries
            import urllib

            # url for deleting the file in case user decides to delete it
            response_data["delete_url"] = request.path + "?" + urllib.urlencode(
                {"f": uid + "/" + os.path.split(filename)[1]})
            # specify the delete type - must be POST for csrf
            response_data["delete_type"] = "POST"

            # generate the json data
            response_data = json.dumps([response_data])
            # response type
            response_type = "application/json"

            # QUIRK HERE
            # in jQuey uploader, when it falls back to uploading using iFrames
            # the response content type has to be text/html
            # if json will be send, error will occur
            # if iframe is sending the request, it's headers are a little different compared
            # to the jQuery ajax request
            # they have different set of HTTP_ACCEPT values
            # so if the text/html is present, file was uploaded using jFrame because
            # that value is not in the set when uploaded by XHR
            if "text/html" in request.META["HTTP_ACCEPT"]:
                response_type = "text/html"

            # return the data to the uploading plugin
            return HttpResponse(response_data, mimetype=response_type)

        else:  # file has to be deleted

            # get the file path by getting it from the query (e.g. '?f=filename.here')
            filepath = os.path.join(temp_path, request.GET["f"])

            # make sure file exists
            # if not return error
            if not os.path.isfile(filepath):
                return HttpResponseBadRequest("File does not exist")

            # delete the file
            # this step might not be a secure method so extra
            # security precautions might have to be taken
            os.remove(filepath)

            # generate true json result
            # in this case is it a json True value
            # if true is not returned, the file will not be removed from the upload queue
            response_data = json.dumps(True)

            # return the result data
            # here it always has to be json
            return HttpResponse(response_data, mimetype="application/json")

    else:  # GET
        template_name = "gallery/ajax.html"
        context['uid'] = uuid.uuid4()
        context['open_tv'] = u'{{'
        context['close_tv'] = u'}}'
        context['maxfilesize'] = options['maxfilesize']
        context['minfilesize'] = options['minfilesize']
        context["gallery_slug"] = request.session['gallery']
        return render(request, template_name, context)


def check_user_availability(request, username):
    if username in [u['username'] for u in User.objects.values('username')]:
        return HttpResponse(False)
    else:
        return HttpResponse(True)
