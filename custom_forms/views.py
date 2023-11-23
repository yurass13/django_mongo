from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

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
    # NOTE Get candidates from db using chain filter
    # manager.filter(A).filter(B)...
    # djongo.ArrayField=$item -> $item in djongo.ArrayField
    candidates = CustomForm.objects
    for item in fields:
        candidates = candidates.filter(fields=item)
    # TODO optimise query with:
    #   candidates.annotate(fields_count=Func(F('fields'),
    #                              <func_name>,
    #                              <template>)).order_by('-fields_count').first()
    #   or etc.

    if 'DT2' in request.data:
        print('\n' + '\n'.join([
            str(request.data),
            str(fields),
            str(candidates),
            str(candidates.query)]))
    # Execute query
    if len(candidates) == 0:
        # No suitable form
        data = {item['f_name']: item['f_type']
                for item in serializer.validated_data['fields']}
    else:
        # --------------------------------Ordering------------------------------------

        # NOTE For my mind, the best method - do sort in query and get only first item,
        # but I didn't have any idea how to get length of array from MongoDB now.
        best_form = min(candidates, key=lambda x: len(x.fields))

        data = {'name': best_form.name}

    return Response(data=data, status=status.HTTP_200_OK)
