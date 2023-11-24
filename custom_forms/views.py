from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from django.db.models import F, Func
from .models import CustomForm
from .serializers import CustomFormSerializer
from .utils import type_caster


@api_view(['POST'])
def get_form(request) -> Response:
    """TODO doc"""
    # --------------------------------Data Format------------------------------------
    fields = [
            {
                'f_name': f_name,
                'f_type': type_caster(request.data.get(f_name))
            }
            for f_name in request.data
        ]
    # -------------------------------Validation---------------------------------------
    # NOTE in future we can get name from urls if it'll be needed
    serializer = CustomFormSerializer(data={'name': 'untitled', 'fields': fields})
    try:
        serializer.is_valid(raise_exception=True)
    except ValidationError as error:
        return Response(data={'error': error}, status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------Querying------------------------------------------
    candidates = CustomForm.objects.filter(fields__gte=fields)
    # TODO how annotate mongo functions
    # annotate(fields_count=Func(F('fields'),
    #                            function='$size',
    #                            template='{%(function)s: %(expressions)s}')).order_by('fields_count').first()

    # Execute query
    if len(candidates) == 0:
        # No suitable form
        data = {item['f_name']: item['f_type']
                for item in serializer.validated_data['fields']}
    else:
        # --------------------------------Ordering------------------------------------
        best_form = min(candidates, key=lambda x: len(x.fields))
        data = {'name': best_form.name}

    return Response(data=data, status=status.HTTP_200_OK)
