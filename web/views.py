# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import datetime
import datetime as dt
from uuid import UUID

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django import forms

# Create your views here.
from django_filters.views import FilterView
from django_ical.views import ICalFeed
from django_tables2 import RequestConfig, LazyPaginator, SingleTableMixin

from api.models import Agency, Launch, Astronaut, Launcher, SpaceStation, SpacecraftConfiguration, LauncherConfig, \
    Events
from bot.models import NewsItem
from web.filters import LauncherConfigListFilter
from web.tables import LaunchVehicleTable, LauncherConfigTable


def get_youtube_url(launch):
    for url in launch.vid_urls.all():
        if 'youtube' in url.vid_url:
            return url.vid_url


def index(request):
    news = NewsItem.objects.all().order_by('-created_at')[:6]
    event = Events.objects.all().filter(date__gte=datetime.utcnow()).order_by('date').first()
    previous_launches = Launch.objects.filter(net__lte=datetime.utcnow()).order_by('-net')[:10]
    _launches = Launch.objects.filter(net__gte=datetime.utcnow()).filter(Q(status__id=1) | Q(status__id=2)).order_by(
        'net')[:3]

    in_flight_launch = Launch.objects.filter(status__id=6).order_by('-net').first()
    recently_launched = Launch.objects.filter(net__gte=datetime.utcnow() - dt.timedelta(hours=2),
                                              net__lte=datetime.utcnow()).order_by('-net').first()
    _next_launch = Launch.objects.filter(net__gte=datetime.utcnow()).order_by('net').first()

    if in_flight_launch:
        launch = in_flight_launch
        _launches = _launches[:2]
    elif recently_launched:
        launch = recently_launched
        _launches = _launches[1:3]
    else:
        launch = _next_launch
        _launches = _launches[1:3]

    return render(request, 'web/index.html', {'launch': launch,
                                              'upcoming_launches': _launches,
                                              'youtube_url': get_youtube_url(_next_launch),
                                              'news': news,
                                              'previous_launches': previous_launches,
                                              'event': event})


def app(request):
    in_flight_launch = Launch.objects.filter(status__id=6).order_by('-net').first()
    if in_flight_launch:
        return render(request, 'web/app.html', {'launch': in_flight_launch,
                                                'youtube_url': get_youtube_url(in_flight_launch)})

    recently_launched = Launch.objects.filter(net__gte=datetime.utcnow() - dt.timedelta(hours=2),
                                              net__lte=datetime.utcnow()).order_by('-net').first()
    if recently_launched:
        return render(request, 'web/app.html', {'launch': recently_launched,
                                                'youtube_url': get_youtube_url(recently_launched)})
    else:
        _next_launch = Launch.objects.filter(net__gte=datetime.utcnow()).order_by('net').first()
        return render(request, 'web/app.html', {'launch': _next_launch,
                                                'youtube_url': get_youtube_url(_next_launch)})


# Create your views here.
def next_launch(request):
    in_flight_launch = Launch.objects.filter(status__id=6).order_by('-net').first()
    if in_flight_launch:
        return redirect('launch_by_slug', slug=in_flight_launch.slug)
    recently_launched = Launch.objects.filter(net__gte=datetime.utcnow() - dt.timedelta(hours=6),
                                              net__lte=datetime.utcnow()).order_by('-net').first()
    if recently_launched:
        return redirect('launch_by_slug', slug=recently_launched.slug)
    else:
        _next_launch = Launch.objects.filter(net__gte=datetime.utcnow()).order_by('net').first()
        return redirect('launch_by_slug', slug=_next_launch.slug)


# Create your views here.
def launch_by_slug(request, slug):
    try:
        val = UUID(slug, version=4)
        try:
            launch = Launch.objects.get(id=slug)
            return redirect('launch_by_slug', slug=launch.slug)
        except ObjectDoesNotExist:
            raise Http404
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        try:
            return create_launch_view(request, Launch.objects.get(slug=slug))
        except ObjectDoesNotExist:
            raise Http404


# Create your views here.
def launch_by_id(request, id):
    try:
        return redirect('launch_by_slug', slug=Launch.objects.get(launch_library_id=id).slug)
    except ObjectDoesNotExist:
        raise Http404


def get_launch_status(launch):
    return {
        1: 'Go for Launch',
        2: 'Launch is NO-GO',
        3: 'Successful Launch',
        4: 'Launch Failed',
        5: 'Unplanned Hold',
        6: 'In Flight',
        7: 'Partial Failure',
    }[launch.status.id]


def create_launch_view(request, launch):
    youtube_urls = []
    vids = launch.vid_urls.all()
    status = get_launch_status(launch)
    agency = launch.rocket.configuration.launch_agency
    launches_good = Launch.objects.filter(rocket__configuration__launch_agency=agency, status=3)
    launches_bad = Launch.objects.filter(Q(rocket__configuration__launch_agency=agency) & Q(Q(status=4) | Q(status=7)))
    launches_pending = Launch.objects.filter(
        Q(rocket__configuration__launch_agency=agency) & Q(Q(status=1) | Q(status=2) | Q(status=5)))
    launches = {'good': launches_good, 'bad': launches_bad, 'pending': launches_pending}
    for url in vids:
        if 'youtube' in url.vid_url:
            youtube_urls.append(url.vid_url)
    previous_launches = Launch.objects.filter(net__lte=datetime.utcnow()).order_by('-net')[:10]
    return render(request, 'web/launch_page.html', {'launch': launch, 'youtube_urls': youtube_urls, 'status': status,
                                                    'agency': agency, 'launches': launches,
                                                    'previous_launches': previous_launches})


# Create your views here.
def launches(request, ):
    query = request.GET.get('q')

    if query is not None and query != "None":
        _launches = Launch.objects.filter(net__gte=datetime.utcnow()).order_by('net')
        _launches = _launches.filter(Q(rocket__configuration__launch_agency__abbrev__contains=query) |
                                     Q(pad__location__name__contains=query) |
                                     Q(rocket__configuration__name__contains=query))
    else:
        _launches = Launch.objects.filter(net__gte=datetime.utcnow()).order_by('net')

    page = request.GET.get('page', 1)
    paginator = Paginator(_launches, 10)

    try:
        launches = paginator.page(page)
    except PageNotAnInteger:
        launches = paginator.page(1)
    except EmptyPage:
        launches = paginator.page(paginator.num_pages)

    previous_launches = Launch.objects.filter(net__lte=datetime.utcnow()).order_by('-net')[:10]

    return render(request, 'web/launches.html', {'launches': launches,
                                                 'query': query,
                                                 'previous_launches': previous_launches})


def astronaut(request, id):
    try:
        return redirect('astronaut_by_slug', slug=Astronaut.objects.get(pk=id).slug)
    except ObjectDoesNotExist:
        raise Http404


def vehicle_root(request):
    news = NewsItem.objects.all().order_by('created_at')[:6]
    previous_launches = Launch.objects.filter(net__lte=datetime.utcnow()).order_by('-net')[:15]
    return render(request, 'web/vehicles/index.html', {'previous_launches': previous_launches,
                                                       'news': news})


def spacecraft_list(request):
    spacecraft = SpacecraftConfiguration.objects.all()
    return render(request, 'web/vehicles/spacecraft/spacecraft_list.html', {'vehicles': spacecraft})


def spacecraft_by_id(request, id):
    spacecraft = SpacecraftConfiguration.objects.get(pk=id)
    previous_launches = Launch.objects.filter(net__lte=datetime.utcnow()).order_by('-net')[:10]
    return render(request, 'web/vehicles/spacecraft/spacecraft_detail.html', {'previous_launches': previous_launches,
                                                                              'vehicle': spacecraft})


def booster_reuse(request):
    status = request.GET.get('status')
    if status is None:
        status = 'active'

    _vehicles = Launcher.objects.filter(status__icontains=status)
    page = request.GET.get('page', 1)
    paginator = Paginator(_vehicles, 20)

    try:
        vehicles = paginator.page(page)
    except PageNotAnInteger:
        vehicles = paginator.page(1)
    except EmptyPage:
        vehicles = paginator.page(paginator.num_pages)

    previous_launches = Launch.objects.filter(net__lte=datetime.utcnow()).order_by('-net')[:10]
    return render(request, 'web/vehicles/boosters/booster_list.html', {'previous_launches': previous_launches,
                                                                       'status': status,
                                                                       'vehicles': vehicles})


def booster_reuse_search(request):
    query = request.GET.get('q')

    if query is not None:
        _vehicles = Launcher.objects.filter(
            Q(launcher_config__name__icontains=query) | Q(serial_number__icontains=query))
        previous_launches = Launch.objects.filter(net__lte=datetime.utcnow()).order_by('-net')[:5]
        return render(request, 'web/vehicles/boosters/boosters_search.html', {'vehicles': _vehicles,
                                                                              'query': query,
                                                                              'previous_launches': previous_launches})
    else:
        return redirect('booster_reuse')


def booster_reuse_id(request, id):
    if id is not None:
        vehicle = Launcher.objects.get(pk=id)
        upcoming_vehicle_launches = Launch.objects.filter(rocket__firststage__launcher_id=vehicle.id).filter(
            net__gte=datetime.utcnow()).order_by('net')
        previous_vehicle_launches = Launch.objects.filter(rocket__firststage__launcher_id=vehicle.id).filter(
            net__lte=datetime.utcnow()).order_by('-net')
        previous_launches = Launch.objects.filter(net__lte=datetime.utcnow()).order_by('-net')[:5]
        return render(request, 'web/vehicles/boosters/booster_detail.html', {'vehicle': vehicle,
                                                                             'previous_launches': previous_launches,
                                                                             'upcoming_vehicle_launches': upcoming_vehicle_launches,
                                                                             'previous_vehicle_launches': previous_vehicle_launches})
    else:
        return redirect('booster_reuse')


class LauncherConfigListView(SingleTableMixin, FilterView):
    table_class = LaunchVehicleTable
    model = LauncherConfig
    template_name = 'web/vehicles/launch_vehicle/launch_vehicles_list.html'

    filterset_class = LauncherConfigListFilter


def launch_vehicle_id(request, id):
    if id is not None:
        vehicle = LauncherConfig.objects.get(pk=id)
        previous_launches = Launch.objects.filter(net__lte=datetime.utcnow()).order_by('-net')[:5]
        upcoming_vehicle_launches = Launch.objects.filter(rocket__configuration=vehicle.id).filter(
            net__gte=datetime.utcnow()).order_by('net')
        previous_vehicle_launches = Launch.objects.filter(rocket__configuration=vehicle.id).filter(
            net__lte=datetime.utcnow()).order_by('-net')

        return render(request, 'web/vehicles/launch_vehicle/launch_vehicle_detail.html',
                      {'vehicle': vehicle, 'previous_launches': previous_launches,
                       'upcoming_vehicle_launches': upcoming_vehicle_launches,
                       'previous_vehicle_launches': previous_vehicle_launches})
    else:
        return redirect('booster_reuse')


def spacestation_list(request):
    spacestations = SpaceStation.objects.all().order_by('status')
    return render(request, 'web/vehicles/spacestations/spacestations_list.html',
                  {'spacestations': spacestations})


def spacestation_by_id(request, id):
    if id is not None:
        spacestation = SpaceStation.objects.get(pk=id)
        previous_launches = Launch.objects.filter(net__lte=datetime.utcnow()).order_by('-net')[:5]
        return render(request, 'web/vehicles/spacestations/spacestations_details.html', {'vehicle': spacestation,
                                                                                         'previous_launches': previous_launches})
    else:
        return redirect('booster_reuse')


def astronaut_by_slug(request, slug):
    try:
        _astronaut = Astronaut.objects.get(slug=slug)
        previous_list = list(
            (Launch.objects.filter(Q(rocket__spacecraftflight__launch_crew__astronaut__id=_astronaut.pk) |
                                   Q(rocket__spacecraftflight__onboard_crew__astronaut__id=_astronaut.pk) |
                                   Q(rocket__spacecraftflight__landing_crew__astronaut__id=_astronaut.pk))
             .filter(net__lte=datetime.utcnow())
             .values_list('pk', flat=True)
             .distinct()))
        upcoming_list = list(
            (Launch.objects.filter(Q(rocket__spacecraftflight__launch_crew__astronaut__id=_astronaut.pk) |
                                   Q(rocket__spacecraftflight__onboard_crew__astronaut__id=_astronaut.pk) |
                                   Q(rocket__spacecraftflight__landing_crew__astronaut__id=_astronaut.pk))
             .filter(net__gte=datetime.utcnow())
             .values_list('pk', flat=True)
             .distinct()))
        _launches = Launch.objects.filter(pk__in=previous_list).order_by('net')
        _upcoming_launches = Launch.objects.filter(pk__in=upcoming_list).order_by('net')
        previous_launches = Launch.objects.filter(net__lte=datetime.utcnow()).order_by('-net')[:5]
        return render(request, 'web/astronaut/astronaut_detail.html', {'astronaut': _astronaut,
                                                                       'previous_astronaut_launches': _launches,
                                                                       'upcoming_launches': _upcoming_launches,
                                                                       'previous_launches': previous_launches})
    except ObjectDoesNotExist:
        raise Http404


def astronaut_list(request, ):
    query = request.GET.get('status')
    if query is None:
        query = 1
    else:
        query = int(query)

    nationality = request.GET.get('nationality')

    if nationality == "American":
        astronaut_list = Astronaut.objects.only("name", "nationality", "twitter", "instagram", "wiki", "bio",
                                                "profile_image", "slug").filter(nationality="American").filter(
            status=query).order_by('name')
    elif nationality == "Russian":
        astronaut_list = Astronaut.objects.only("name", "nationality", "twitter", "instagram", "wiki", "bio",
                                                "profile_image", "slug").filter(
            Q(nationality="Russian") | Q(nationality="Soviet")).filter(status=query).order_by('name')
    elif nationality == "European":
        astronaut_list = Astronaut.objects.only("name", "nationality", "twitter", "instagram", "wiki", "bio",
                                                "profile_image", "slug").filter(
            Q(nationality="Austrain") | Q(nationality="Belarusian") | Q(nationality="Belgian")
            | Q(nationality="British") | Q(nationality="Danish") | Q(nationality="Dutch")
            | Q(nationality="French") | Q(nationality="German") | Q(nationality="Italian")
            | Q(nationality="Polish") | Q(nationality="Spanish") | Q(nationality="Swedish")
            | Q(nationality="Swiss")).filter(status=query).order_by('name')
    elif nationality == "Other":
        astronaut_list = Astronaut.objects.only("name", "nationality", "twitter", "instagram", "wiki", "bio",
                                                "profile_image", "slug").exclude(nationality="Austrain").exclude(
            nationality="Belarusian").exclude(nationality="Belgian").exclude(nationality="British").exclude(
            nationality="Danish").exclude(nationality="Dutch") \
            .exclude(nationality="French").exclude(nationality="German") \
            .exclude(nationality="Italian").exclude(nationality="Polish") \
            .exclude(nationality="Spanish").exclude(nationality="Swedish") \
            .exclude(nationality="Swiss").exclude(nationality="American").exclude(nationality="Russian").exclude(
            nationality="Soviet").filter(status=query).order_by('name')
    else:
        astronaut_list = Astronaut.objects.only("name", "nationality", "twitter", "instagram", "wiki", "bio",
                                                "profile_image", "slug").filter(status=query).order_by('name')

    previous_launches = Launch.objects.only("slug", "net", "name", "status__name", "mission__name",
                                            "mission__description", "rocket__configuration__name").prefetch_related(
        'info_urls').prefetch_related('vid_urls').select_related('rocket').prefetch_related('mission').prefetch_related(
        'rocket__configuration').prefetch_related('rocket__configuration__launch_agency').prefetch_related(
        'mission__mission_type').prefetch_related('status').filter(net__lte=datetime.utcnow()).order_by('-net')[:10]

    page = request.GET.get('page', 1)

    paginator = Paginator(astronaut_list, 9)

    try:
        astronauts = paginator.page(page)
    except PageNotAnInteger:
        astronauts = paginator.page(1)
    except EmptyPage:
        astronauts = paginator.page(paginator.num_pages)

    return render(request, 'web/astronaut/astronaut_list.html', {'astronauts': astronauts,
                                                                 'previous_launches': previous_launches,
                                                                 'status': query,
                                                                 'nationality': nationality})


def handler404(request):
    return render(request, 'web/404.html', status=404)


def handler500(request):
    return render(request, 'web/500.html', status=500)


def launches_redirect(request, ):
    return redirect('launches')


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        for fieldname in ['password1']:
            self.fields[fieldname].help_text = None

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)
        help_texts = {
            'password1': None,
        }


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/admin/')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def astronaut_search(request):
    query = request.GET.get('q')

    if query is not None:
        _astronauts = Astronaut.objects.filter(name__icontains=query).order_by('name')
        previous_launches = Launch.objects.filter(net__lte=datetime.utcnow()).order_by('-net')[:5]
        return render(request, 'web/astronaut/astronaut_search.html', {'astronauts': _astronauts,
                                                                       'query': query,
                                                                       'previous_launches': previous_launches})
    else:
        return redirect('astronauts')


def astronaut_search_ajax(request):
    query = request.GET.get('q')

    if not query:
        return HttpResponse(json.dumps([{}]), content_type='application/json')
    majors = Astronaut.objects.filter(name__icontains=query)
    return HttpResponse(
        json.dumps(majors),
        content_type='application/json',
    )


class LaunchFeed(ICalFeed):
    """
    A simple Launch event calender.
    """
    product_id = '-//spacelaunchnow.me//launch//calendar//EN'
    timezone = 'UTC'
    file_name = "launches.ics"

    def items(self):
        return Launch.objects.filter(net__gte=datetime.utcnow()).order_by('net')

    def item_guid(self, item):
        return "{}{}".format(item.id, "@spacelaunchnow")

    def item_title(self, item):
        return "{}".format(item.name)

    def item_description(self, item):
        description = ""
        if item.mission is not None and item.mission.description is not None:
            description = item.mission.description
        urls = "\n\nWatch Live: " + item.get_full_absolute_url()
        description = description + urls + "\n\n===============\nSpace Launch Now\nID: " + str(item.id) + "\n==============="
        return description

    def item_start_datetime(self, item):
        if item.window_start is not None:
            return item.window_start
        else:
            return item.net

    def item_end_datetime(self, item):
        if item.window_end is not None and item.window_start is not None and item.window_start.date() != item.window_end.date():
            return item.window_end
        else:
            return None

    def item_updateddate(self, item):
        if item.last_updated is not None:
            return item.last_updated

    def item_location(self, item):
        if item.pad is not None and item.pad.location is not None:
            return item.pad.location.name

    def item_link(self, item):
        return item.get_full_absolute_url()


class EventFeed(ICalFeed):
    """
    A simple Launch event calender.
    """
    product_id = '-//spacelaunchnow.me//event//calendar//EN'
    timezone = 'UTC'
    file_name = "events.ics"

    def items(self):
        return Events.objects.filter(date__gte=datetime.utcnow()).order_by('date')

    def item_guid(self, item):
        return "{}{}".format(item.id, "@spacelaunchnow")

    def item_title(self, item):
        return "{}".format(item.name)

    def item_description(self, item):
        description = ""
        if item.description is not None:
            description = item.description
        if item.news_url is not None:
            description = description + "\nRead More:\n" + item.news_url
        if item.video_url is not None:
            description = description + "\nWatch Here:\n" + item.video_url

        description = description + "\n\n===============\nSpace Launch Now\nID: " + str(item.id) + "\n==============="
        return description

    def item_start_datetime(self, item):
        return item.date

    def item_location(self, item):
            return item.location

    def item_link(self, item):
        if item.news_url is not None:
            return item.news_url
        elif item.video_url is not None:
            return item.video_url
        else:
            return "https://spacelaunchnow.me"
