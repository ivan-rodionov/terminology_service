from datetime import date

from django.contrib import admin
from django.contrib.auth.models import Group
from django.db.models import OuterRef, QuerySet, Subquery
from django.http import HttpRequest
from django.utils import timezone

from refbooks.models import Refbook, RefbookElement, RefbookVersion


class RefbookVersionInline(admin.TabularInline):
    model = RefbookVersion
    extra = 0
    show_change_link = True


class RefbookElementInline(admin.TabularInline):
    model = RefbookElement
    extra = 0


@admin.register(Refbook)
class RefbookAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'current_version', 'current_version_start_date')
    search_fields = ('code', 'name')
    inlines = (RefbookVersionInline,)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        queryset = super().get_queryset(request)

        current_versions = RefbookVersion.objects.filter(
            refbook_id=OuterRef('pk'), start_date__lte=timezone.localdate()
        ).order_by('-start_date')

        return queryset.annotate(
            current_version_number=Subquery(current_versions.values('version')[:1]),
            current_version_date=Subquery(current_versions.values('start_date')[:1]),
        )

    @admin.display(description='Текущая версия')
    def current_version(self, obj: Refbook) -> str:
        return obj.current_version_number or '—'

    @admin.display(description='Дата начала действия версии')
    def current_version_start_date(self, obj: Refbook) -> date | str:
        return obj.current_version_date or '—'


@admin.register(RefbookVersion)
class RefbookVersionAdmin(admin.ModelAdmin):
    list_display = ('refbook_code', 'refbook_name', 'version', 'start_date')
    list_select_related = ('refbook',)
    search_fields = ('refbook__code', 'refbook__name', 'version')
    inlines = (RefbookElementInline,)

    @admin.display(description='Код справочника', ordering='refbook__code')
    def refbook_code(self, obj: RefbookVersion) -> str:
        return obj.refbook.code

    @admin.display(description='Наименование справочника', ordering='refbook__name')
    def refbook_name(self, obj: RefbookVersion) -> str:
        return obj.refbook.name


@admin.register(RefbookElement)
class RefbookElementAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'code', 'value')
    search_fields = ('code', 'value')
    list_select_related = ('version', 'version__refbook')


admin.site.unregister(Group)
