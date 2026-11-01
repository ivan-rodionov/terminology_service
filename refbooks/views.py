from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from refbooks.models import Refbook
from refbooks.serializers import (
    RefbookCheckElementParamsSerializer,
    RefbookElementSerializer,
    RefbookListParamsSerializer,
    RefbookSerializer,
    RefbookVersionParamsSerializer,
)
from refbooks.services import get_selected_version


class RefbookListView(APIView):
    @extend_schema(
        summary='Получение списка справочников',
        description='Возвращает все справочники или справочники с версиями,'
        'начавшими действовать не позже указанной даты.',
        parameters=[RefbookListParamsSerializer],
        responses=inline_serializer(name='RefbookListResponse', fields={'refbooks': RefbookSerializer(many=True)}),
        examples=[
            OpenApiExample(
                name='Список справочников',
                value={
                    'refbooks': [
                        {'id': '1', 'code': 'SPEC', 'name': 'Специальности врачей'},
                        {'id': '2', 'code': 'ICD-10', 'name': 'Классификация болезней'},
                    ],
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
    )
    def get(self, request: Request) -> Response:
        params = RefbookListParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)

        refbooks = Refbook.objects.all().order_by('id')

        date = params.validated_data.get('date')
        if date is not None:
            refbooks = refbooks.filter(versions__start_date__lte=date).distinct()

        serializer = RefbookSerializer(refbooks, many=True)

        return Response({'refbooks': serializer.data})


class RefbookElementsView(APIView):
    @extend_schema(
        summary='Получение элементов справочника',
        description='Возвращает элементы указанной версии справочника'
        'или текущей версии, если параметр version не передан.',
        parameters=[RefbookVersionParamsSerializer],
        responses=inline_serializer(
            name='RefbookElementsResponse',
            fields={'elements': RefbookElementSerializer(many=True)},
        ),
        examples=[
            OpenApiExample(
                name='Элементы справочника',
                value={
                    'elements': [
                        {'code': '1', 'value': 'Терапевт'},
                        {'code': '2', 'value': 'Хирург'},
                        {'code': '3', 'value': 'Кардиолог'},
                    ],
                },
                response_only=True,
                status_codes=['200'],
            ),
        ],
    )
    def get(self, request: Request, refbook_id: int) -> Response:
        params = RefbookVersionParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)

        refbook = get_object_or_404(Refbook, pk=refbook_id)
        selected_version = get_selected_version(refbook=refbook, version_number=params.validated_data.get('version'))

        elements = selected_version.elements.all().order_by('id')
        serializer = RefbookElementSerializer(elements, many=True)

        return Response({'elements': serializer.data})


class RefbookCheckElementView(APIView):
    @extend_schema(
        summary='Проверка элемента справочника',
        description='Проверяет соответствие кода и значения элемента в указанной или текущей версии справочника.',
        parameters=[RefbookCheckElementParamsSerializer],
        responses=inline_serializer(
            name='RefbookCheckElementResponse',
            fields={'valid': serializers.BooleanField()},
        ),
        examples=[
            OpenApiExample(name='Элемент существует', value={'valid': True}, response_only=True, status_codes=['200']),
            OpenApiExample(
                name='Элемент не существует', value={'valid': False}, response_only=True, status_codes=['200']
            ),
        ],
    )
    def get(self, request: Request, refbook_id: int) -> Response:
        params = RefbookCheckElementParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)

        refbook = get_object_or_404(Refbook, pk=refbook_id)
        selected_version = get_selected_version(refbook=refbook, version_number=params.validated_data.get('version'))

        is_valid = selected_version.elements.filter(
            code=params.validated_data['code'],
            value=params.validated_data['value'],
        ).exists()

        return Response({'valid': is_valid})
