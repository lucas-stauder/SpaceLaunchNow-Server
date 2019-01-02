from django.db.models import Count
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from api.models import *
from api.v330.agencies.serializers import AgencySerializerDetailed, AgencySerializer
from api.permission import HasGroupPermission


# TODO docs
class AgencyViewSet(ModelViewSet):
    """
    API endpoint that allows Agencies to be viewed.

    GET:
    Return a list of all the existing users.

    FILTERS:
    Parameters - 'featured', 'launch_library_id', 'detailed',
    Example - /3.2.0/agencies/?featured=true&launch_library_id=44&detailed

    SEARCH EXAMPLE:
    /3.2.0/agencies/?search=nasa

    ORDERING:
    Fields - 'id', 'name', 'featured', 'launch_library_id'
    Example - /3.2.0/agencies/?ordering=featured

    """

    def get_queryset(self):
        spacecraft = self.request.query_params.get("spacecraft", False)
        if spacecraft:
            return Agency.objects.annotate(spacecraft_count=Count('spacecraft_list')).filter(spacecraft_count__gt=0)
        else:
            return Agency.objects.all()

    def get_serializer_class(self):
        mode = self.request.query_params.get("mode", "normal")
        spacecraft = self.request.query_params.get("spacecraft", False)
        if mode == "detailed" or self.action == 'retrieve' or spacecraft:
            return AgencySerializerDetailed
        else:
            return AgencySerializer

    permission_classes = [HasGroupPermission]
    permission_groups = {
        'retrieve': ['_Public'],  # retrieve can be accessed without credentials (GET 'site.com/api/foo/1')
        'list': ['_Public']
    }
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('featured',)
    search_fields = ('^name',)
    ordering_fields = ('id', 'name', 'featured')
