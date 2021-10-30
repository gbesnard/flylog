from django.http import HttpResponse

from .models import Flight, Image, Video

import json
import os
from datetime import datetime
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from django.utils.timezone import make_aware
from overview.igc_lib import igc_lib
import os.path
from os import path


class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        information = GeneralInfo()
        context = {
            'flight_list': Flight.objects.all(),
            'information': information
        }
        return render(request, 'overview/flight_list.html', context)


class ReliefView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'overview/relief.html')


class PhotosView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'flight_list': Flight.objects.all(),
        }
        return render(request, 'overview/photos.html', context)


class FlightDetailView(LoginRequiredMixin, DetailView):
    model = Flight

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        coordinates = []
        cartographic_degrees = []
        properties = [] # TODO: add timestamp inside ?
        i = 0

        if context['flight'].igc:
            if os.path.isfile(context['flight'].igc.path):
                flight = igc_lib.Flight.create_from_file(context['flight'].igc.path)

                if flight.valid:
                    # handle date : TODO: string is not in UTC (as the ZULU will let you think), but in Paris timezone
                    takeoff_timestamp = datetime.fromtimestamp(flight.takeoff_fix.timestamp)
                    landing_timestamp = datetime.fromtimestamp(flight.landing_fix.timestamp)
                    takeoff_time_str = takeoff_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
                    landing_time_str = landing_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
                    interval_time_str = takeoff_time_str + "/" + landing_time_str

                    for fix in flight.fixes:
                        coordinates.append([fix.lon, fix.lat, fix.gnss_alt])
                        cartographic_degrees.append(i)
                        cartographic_degrees.append(fix.lon)
                        cartographic_degrees.append(fix.lat)
                        cartographic_degrees.append(fix.gnss_alt)
                        i = i + 1

                    geojson = {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "geometry": {
                                    "type": "LineString",
                                    "coordinates": coordinates,
                                },
                                "properties": {
                                    "prop0": "foo",
                                    "prop1": {"foo": "bar"}
                                }
                            }
                        ]
                    }

                    czml = [
                        {
                            "id": "document",
                            "name": "CZML Path",
                            "version": "1.0",
                            "clock": {
                                "interval": interval_time_str,
                                "currentTime": takeoff_time_str,
                                "multiplier": 4,
                            },
                        },
                        {
                            "id": "path",
                            "name": "path with GPS flight data",
                            "description": "<p>Paragliding flight log data from Guillaume Besnard</p>",
                            "availability": interval_time_str,
                            "path": {
                                "material": {
                                    "polylineOutline": {
                                        "color": {
                                            "rgba": [255, 0, 0, 255],
                                        },
                                        "outlineColor": {
                                            "rgba": [0, 0, 0, 255],
                                        },
                                        "outlineWidth": 1,
                                    },
                                },
                                "width": 3,
                                "leadTime": 0,
                                "trailTime": 1000000000,
                                "resolution": 100,
                            },
                            "billboard": {
                                "image":
                                    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAfCAYAAACVgY94AAAACXBIWXMAAC4jAAAuIwF4pT92AAAKT2lDQ1BQaG90b3Nob3AgSUNDIHByb2ZpbGUAAHjanVNnVFPpFj333vRCS4iAlEtvUhUIIFJCi4AUkSYqIQkQSoghodkVUcERRUUEG8igiAOOjoCMFVEsDIoK2AfkIaKOg6OIisr74Xuja9a89+bN/rXXPues852zzwfACAyWSDNRNYAMqUIeEeCDx8TG4eQuQIEKJHAAEAizZCFz/SMBAPh+PDwrIsAHvgABeNMLCADATZvAMByH/w/qQplcAYCEAcB0kThLCIAUAEB6jkKmAEBGAYCdmCZTAKAEAGDLY2LjAFAtAGAnf+bTAICd+Jl7AQBblCEVAaCRACATZYhEAGg7AKzPVopFAFgwABRmS8Q5ANgtADBJV2ZIALC3AMDOEAuyAAgMADBRiIUpAAR7AGDIIyN4AISZABRG8lc88SuuEOcqAAB4mbI8uSQ5RYFbCC1xB1dXLh4ozkkXKxQ2YQJhmkAuwnmZGTKBNA/g88wAAKCRFRHgg/P9eM4Ors7ONo62Dl8t6r8G/yJiYuP+5c+rcEAAAOF0ftH+LC+zGoA7BoBt/qIl7gRoXgugdfeLZrIPQLUAoOnaV/Nw+H48PEWhkLnZ2eXk5NhKxEJbYcpXff5nwl/AV/1s+X48/Pf14L7iJIEyXYFHBPjgwsz0TKUcz5IJhGLc5o9H/LcL//wd0yLESWK5WCoU41EScY5EmozzMqUiiUKSKcUl0v9k4t8s+wM+3zUAsGo+AXuRLahdYwP2SycQWHTA4vcAAPK7b8HUKAgDgGiD4c93/+8//UegJQCAZkmScQAAXkQkLlTKsz/HCAAARKCBKrBBG/TBGCzABhzBBdzBC/xgNoRCJMTCQhBCCmSAHHJgKayCQiiGzbAdKmAv1EAdNMBRaIaTcA4uwlW4Dj1wD/phCJ7BKLyBCQRByAgTYSHaiAFiilgjjggXmYX4IcFIBBKLJCDJiBRRIkuRNUgxUopUIFVIHfI9cgI5h1xGupE7yAAygvyGvEcxlIGyUT3UDLVDuag3GoRGogvQZHQxmo8WoJvQcrQaPYw2oefQq2gP2o8+Q8cwwOgYBzPEbDAuxsNCsTgsCZNjy7EirAyrxhqwVqwDu4n1Y8+xdwQSgUXACTYEd0IgYR5BSFhMWE7YSKggHCQ0EdoJNwkDhFHCJyKTqEu0JroR+cQYYjIxh1hILCPWEo8TLxB7iEPENyQSiUMyJ7mQAkmxpFTSEtJG0m5SI+ksqZs0SBojk8naZGuyBzmULCAryIXkneTD5DPkG+Qh8lsKnWJAcaT4U+IoUspqShnlEOU05QZlmDJBVaOaUt2ooVQRNY9aQq2htlKvUYeoEzR1mjnNgxZJS6WtopXTGmgXaPdpr+h0uhHdlR5Ol9BX0svpR+iX6AP0dwwNhhWDx4hnKBmbGAcYZxl3GK+YTKYZ04sZx1QwNzHrmOeZD5lvVVgqtip8FZHKCpVKlSaVGyovVKmqpqreqgtV81XLVI+pXlN9rkZVM1PjqQnUlqtVqp1Q61MbU2epO6iHqmeob1Q/pH5Z/YkGWcNMw09DpFGgsV/jvMYgC2MZs3gsIWsNq4Z1gTXEJrHN2Xx2KruY/R27iz2qqaE5QzNKM1ezUvOUZj8H45hx+Jx0TgnnKKeX836K3hTvKeIpG6Y0TLkxZVxrqpaXllirSKtRq0frvTau7aedpr1Fu1n7gQ5Bx0onXCdHZ4/OBZ3nU9lT3acKpxZNPTr1ri6qa6UbobtEd79up+6Ynr5egJ5Mb6feeb3n+hx9L/1U/W36p/VHDFgGswwkBtsMzhg8xTVxbzwdL8fb8VFDXcNAQ6VhlWGX4YSRudE8o9VGjUYPjGnGXOMk423GbcajJgYmISZLTepN7ppSTbmmKaY7TDtMx83MzaLN1pk1mz0x1zLnm+eb15vft2BaeFostqi2uGVJsuRaplnutrxuhVo5WaVYVVpds0atna0l1rutu6cRp7lOk06rntZnw7Dxtsm2qbcZsOXYBtuutm22fWFnYhdnt8Wuw+6TvZN9un2N/T0HDYfZDqsdWh1+c7RyFDpWOt6azpzuP33F9JbpL2dYzxDP2DPjthPLKcRpnVOb00dnF2e5c4PziIuJS4LLLpc+Lpsbxt3IveRKdPVxXeF60vWdm7Obwu2o26/uNu5p7ofcn8w0nymeWTNz0MPIQ+BR5dE/C5+VMGvfrH5PQ0+BZ7XnIy9jL5FXrdewt6V3qvdh7xc+9j5yn+M+4zw33jLeWV/MN8C3yLfLT8Nvnl+F30N/I/9k/3r/0QCngCUBZwOJgUGBWwL7+Hp8Ib+OPzrbZfay2e1BjKC5QRVBj4KtguXBrSFoyOyQrSH355jOkc5pDoVQfujW0Adh5mGLw34MJ4WHhVeGP45wiFga0TGXNXfR3ENz30T6RJZE3ptnMU85ry1KNSo+qi5qPNo3ujS6P8YuZlnM1VidWElsSxw5LiquNm5svt/87fOH4p3iC+N7F5gvyF1weaHOwvSFpxapLhIsOpZATIhOOJTwQRAqqBaMJfITdyWOCnnCHcJnIi/RNtGI2ENcKh5O8kgqTXqS7JG8NXkkxTOlLOW5hCepkLxMDUzdmzqeFpp2IG0yPTq9MYOSkZBxQqohTZO2Z+pn5mZ2y6xlhbL+xW6Lty8elQfJa7OQrAVZLQq2QqboVFoo1yoHsmdlV2a/zYnKOZarnivN7cyzytuQN5zvn//tEsIS4ZK2pYZLVy0dWOa9rGo5sjxxedsK4xUFK4ZWBqw8uIq2Km3VT6vtV5eufr0mek1rgV7ByoLBtQFr6wtVCuWFfevc1+1dT1gvWd+1YfqGnRs+FYmKrhTbF5cVf9go3HjlG4dvyr+Z3JS0qavEuWTPZtJm6ebeLZ5bDpaql+aXDm4N2dq0Dd9WtO319kXbL5fNKNu7g7ZDuaO/PLi8ZafJzs07P1SkVPRU+lQ27tLdtWHX+G7R7ht7vPY07NXbW7z3/T7JvttVAVVN1WbVZftJ+7P3P66Jqun4lvttXa1ObXHtxwPSA/0HIw6217nU1R3SPVRSj9Yr60cOxx++/p3vdy0NNg1VjZzG4iNwRHnk6fcJ3/ceDTradox7rOEH0x92HWcdL2pCmvKaRptTmvtbYlu6T8w+0dbq3nr8R9sfD5w0PFl5SvNUyWna6YLTk2fyz4ydlZ19fi753GDborZ752PO32oPb++6EHTh0kX/i+c7vDvOXPK4dPKy2+UTV7hXmq86X23qdOo8/pPTT8e7nLuarrlca7nuer21e2b36RueN87d9L158Rb/1tWeOT3dvfN6b/fF9/XfFt1+cif9zsu72Xcn7q28T7xf9EDtQdlD3YfVP1v+3Njv3H9qwHeg89HcR/cGhYPP/pH1jw9DBY+Zj8uGDYbrnjg+OTniP3L96fynQ89kzyaeF/6i/suuFxYvfvjV69fO0ZjRoZfyl5O/bXyl/erA6xmv28bCxh6+yXgzMV70VvvtwXfcdx3vo98PT+R8IH8o/2j5sfVT0Kf7kxmTk/8EA5jz/GMzLdsAAAAgY0hSTQAAeiUAAICDAAD5/wAAgOkAAHUwAADqYAAAOpgAABdvkl/FRgAAA7VJREFUeNrEl2uIlWUQx39nXUu0m2uQbZYrbabdLKMs/VBkmHQjioqFIhBS+hKEQpQRgVAf2u5RQkGBRUllRH4I2e5ZUBJlEZVt5i0tTfHStrZ6fn35L70d9n7Obg88vOedmWfmf2bmmZkXlRrtq9V16mZ1iVqqhd5agXvQf1c5zw/V8dXqrqO6dQKwBrgdWApsCb0VqAc2AnOrMVANwIsD4BLgTOBPYB2wHJgEzAG+ANqAu4ZsZYiuX5QwfqI2hvaNulA9J7zLQn8o76vUuuHOwXHqSzH4aIF+TWjnBkSH+nCBf716SP1KPWO4AJ6ltgfIjRW8p9U/1KPz/ry6RT2mIDNF3Zjz19Ya4G1R/J16dgWvQd2pPlXhMdVZPUTgxfCW1wJgXUJpQlvfg8zs8K8r0Caom9QHetG7NGfa1ElDBThRXRtFd/Qh16puKIS3e7+clBjdy7kL1b3q4fzJQQGck5z6Nb97kxujblWf64HXov7Vl/E4YXWccP9AAd6dAx+ox/WTArNzY1t64B0f8K0DyLXuUvRGZfcpCo1VX4tg6wB76WMB0dALf526foAX8cqUot2pGP8B2Kz+krBeNYjS8636dh/8Beo2deoA9TWp76pd6g0q9cDNwKvAD8A84EfglLRBe2g+JWAfcEF68bPABOCoAl/gIPA5MA64FVgGnNhP292W3r0SeB1YVlJXAjcBP8XwyQUj9AKwAzg2+/fQSsBhoJxBAaALaIzenZGnD911wA7gEDAD2FFSpwOzgDHZ5T7+ZSlGd2d6AXgi5+qAn+O5U0PbBVwKtAD3AHuB8f3YGBUdncCGoQ4LE9XtGRqK9LnduVPRIu2BPqwD65IYbS7Qpql7Ql9YoJcy9bwzkgPrfOCj5G33+h54E/g0PAr5thq4ApgyEgNrc27aWwVaPTA1QJ4BjgTGFvhteV40EgPrgvTP7qlmZqFnl9WD+b2posN83E/NrEkOjlI/U1fkfUYa/pe5IE3qZPW8jFOqiyN7p3pAPX04c7AxYSoDDcAjKT2LgLXA6IR2M3Bviv59wDTgQGTPH84Qd8+HXfHcoUws2zM0HMjuUPep+xP2PWpnwtw0GJsldbBpewQwE/gbeDyt7H1gcW53O7AC+A3Yn6+/W+Ld9SnWA15DAVhc8xK2TuA9YHrCuhV4EngFuBx4YagG6qv8cF+T52kB2Zy+e1I8taUacNV+uBdXO7ABmJwJpwx8XQvF9TUCWM64tiQhbq/oMv+7BwFWpQzNT8vbVQul/wwAGzzdmXU1xuUAAAAASUVORK5CYII=",
                                "scale": 1,
                                "eyeOffset": {
                                    "cartesian": [0.0, 0.0, 0],
                                },
                            },
                            "position": {
                                "epoch": takeoff_time_str,
                                "cartographicDegrees": cartographic_degrees,
                            },
                        },
                    ];

                    context['igc_geojson'] = json.dumps(geojson)
                    context['igc_czml'] = json.dumps(czml)
                    context['cesium_key'] = "\"" + settings.CESIUM_KEY + "\""

        return context

class FlightCreateView(LoginRequiredMixin, CreateView):
    model = Flight
    fields = ['date', 'site', 'duration', 'wing', 'context', 'comment', 'igc']

    def get_success_url(self):
        return '/' + str(self.object.id) + '/detail/'


class FlightCreateFromIGCView(LoginRequiredMixin, CreateView):
    model = Flight
    fields = ['site', 'wing', 'comment', 'igc']

    def get_success_url(self):
        return '/' + str(self.object.id) + '/detail/'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()

        # Add missing info to new flight using IGC info
        if os.path.isfile(post.igc.path):
            flight = igc_lib.Flight.create_from_file(post.igc.path)
            if flight.valid:
                # handle date : TODO: string is not in UTC (as the ZULU will let you think), but in Paris timezone
                takeoff_timestamp = datetime.fromtimestamp(flight.takeoff_fix.timestamp)
                landing_timestamp = datetime.fromtimestamp(flight.landing_fix.timestamp)
                post.duration = (landing_timestamp - takeoff_timestamp).total_seconds() / 60.0
                post.date = make_aware(takeoff_timestamp)

        return super().form_valid(form)


class FlightAddImageView(LoginRequiredMixin, CreateView):
    model = Image
    fields = ['img_path']

    def get_initial(self):
        self.success_url = "/" + self.kwargs['pk'] + "/detail/"
        return super().get_initial()

    def form_valid(self, form):
        form.instance.flight = Flight.objects.get(pk=self.kwargs['pk'])
        post = form.save(commit=False)
        post.save()
        return super().form_valid(form)


class FlightAddVideoView(LoginRequiredMixin, CreateView):
    model = Video
    fields = ['video_path']

    def get_initial(self):
        self.success_url = "/" + self.kwargs['pk'] + "/detail/"
        return super().get_initial()

    def form_valid(self, form):
        form.instance.flight = Flight.objects.get(pk=self.kwargs['pk'])
        post = form.save(commit=False)
        post.save()
        return super().form_valid(form)


class FlightDeleteImageView(LoginRequiredMixin, DeleteView):
    model = Image

    def get_success_url(self):
        return '/' + str(self.object.flight.id) + '/detail/'


class FlightDeleteVideoView(LoginRequiredMixin, DeleteView):
    model = Video

    def get_success_url(self):
        return '/' + str(self.object.flight.id) + '/detail/'


class FlightUpdateView(LoginRequiredMixin, UpdateView):
    model = Flight
    success_url = "/"
    fields = ['date', 'site', 'duration', 'wing', 'context', 'comment', 'igc']
    template_name_suffix = '_update_form'

    def get_initial(self):
        self.success_url = "/" + self.kwargs['pk'] + "/detail/"
        return super().get_initial()


class FlightDeleteView(LoginRequiredMixin, DeleteView):
    model = Flight
    success_url = "/"


class GeneralInfo:
    def __init__(self):
        self.information_per_year = {}
        self.duration_sum = {}

        self.flights_number = 0

        flights_number_per_year = {}
        duration_sum_per_year_tmp = {}
        duration_sum_tmp = 0

        for flight in Flight.objects.all():
            year = flight.date.year.__str__();
            if year not in duration_sum_per_year_tmp:
                duration_sum_per_year_tmp[year] = flight.duration
                flights_number_per_year[year] = 1
            else:
                duration_sum_per_year_tmp[year] += flight.duration
                flights_number_per_year[year] += 1
            duration_sum_tmp += flight.duration
            self.flights_number += 1

        for year, dur in duration_sum_per_year_tmp.items():
            self.information_per_year[year] = {
                'duration': str(round(dur / 60, 1)),
                'flights_number_per_year': flights_number_per_year[year]
            }

        self.duration_sum = str(round(duration_sum_tmp / 60, 1))

@login_required
def export_json(request):
    data_to_encode = []

    for flight in Flight.objects.all():
        data_to_encode.append(flight.to_dictionary())

    with open("tmp.json", 'wb') as outfile:
        data_json = json.dumps(data_to_encode, indent=4, ensure_ascii=False)
        outfile.write(data_json.encode('utf-8'))

        # safety : use a tmp file until the end
        os.rename("tmp.json", "flylog.json")
        return HttpResponse(data_json)

@login_required
def import_json(request):
    with open("flylog_import.json", 'r') as infile:
        json_str = infile.read()
        data = json.loads(json_str)
        for row in data:
            flight = Flight(
                date=datetime.strptime(row["date"], '%d/%m/%y %H:%M'),
                site=row["site"],
                duration=row["duration"],
                wing=row["wing"],
                context=row["context"],
                comment=row["comment"]
            )
            flight.save()

            if "videos" in row:
                for video_dict in row["videos"]:
                    video = Video(url=video_dict["url"], flight=flight)
                    video.save()

            if "images" in row:
                for image_dict in row["images"]:
                    image = Image(url=image_dict["url"], flight=flight)
                    image.save()

    return HttpResponse("JSON import done.")
