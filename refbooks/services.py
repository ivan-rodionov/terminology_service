from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import NotFound

from refbooks.models import Refbook, RefbookVersion


def get_selected_version(refbook: Refbook, version_number: str | None) -> RefbookVersion:
    versions = RefbookVersion.objects.filter(refbook=refbook)

    if version_number is not None:
        return get_object_or_404(versions, version=version_number)

    current_version = versions.filter(start_date__lte=timezone.localdate()).order_by('-start_date').first()

    if current_version is None:
        raise NotFound('У справочника нет действующей версии.')

    return current_version
