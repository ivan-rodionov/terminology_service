from django.db import models


class Refbook(models.Model):
    code = models.CharField('код', max_length=100, unique=True)
    name = models.CharField('наименование', max_length=300)
    description = models.TextField('описание', blank=True)

    class Meta:
        verbose_name = 'справочник'
        verbose_name_plural = 'справочники'

    def __str__(self) -> str:
        return f'{self.code} — {self.name}'


class RefbookVersion(models.Model):
    refbook = models.ForeignKey(Refbook, verbose_name='справочник', on_delete=models.CASCADE, related_name='versions')
    version = models.CharField('версия', max_length=50)
    start_date = models.DateField('дата начала действия', null=True, blank=True)

    class Meta:
        verbose_name = 'версия справочника'
        verbose_name_plural = 'версии справочников'
        constraints = [
            models.UniqueConstraint(fields=['refbook', 'version'], name='unique_refbook_version'),
            models.UniqueConstraint(fields=['refbook', 'start_date'], name='unique_refbook_start_date'),
        ]

    def __str__(self) -> str:
        return f'{self.refbook.code} — {self.version}'


class RefbookElement(models.Model):
    version = models.ForeignKey(
        RefbookVersion, verbose_name='версия справочника', on_delete=models.CASCADE, related_name='elements'
    )
    code = models.CharField('код элемента', max_length=100)
    value = models.CharField('значение элемента', max_length=300)

    class Meta:
        verbose_name = 'элемент справочника'
        verbose_name_plural = 'элементы справочников'
        constraints = [
            models.UniqueConstraint(fields=['version', 'code'], name='unique_version_element_code'),
        ]

    def __str__(self) -> str:
        return f'{self.code} — {self.value}'
