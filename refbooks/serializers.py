from rest_framework import serializers

from refbooks.models import Refbook, RefbookElement


class RefbookSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Refbook
        fields = ('id', 'code', 'name')


class RefbookListParamsSerializer(serializers.Serializer):
    date = serializers.DateField(required=False, help_text='Дата в формате ГГГГ-ММ-ДД')


class RefbookElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefbookElement
        fields = ('code', 'value')


class RefbookVersionParamsSerializer(serializers.Serializer):
    version = serializers.CharField(required=False, allow_blank=False, max_length=50)


class RefbookCheckElementParamsSerializer(RefbookVersionParamsSerializer):
    code = serializers.CharField(max_length=100, trim_whitespace=False)
    value = serializers.CharField(max_length=300, trim_whitespace=False)
