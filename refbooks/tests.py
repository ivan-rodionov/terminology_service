from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from refbooks.models import Refbook, RefbookElement, RefbookVersion


class RefbookAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        today = timezone.localdate()

        cls.refbook = Refbook.objects.create(code='SPEC', name='Специальности врачей')
        cls.future_refbook = Refbook.objects.create(code='FUTURE', name='Будущий справочник')
        cls.empty_refbook = Refbook.objects.create(code='EMPTY', name='Пустой справочник')

        cls.old_version = RefbookVersion.objects.create(
            refbook=cls.refbook, version='1.0', start_date=today - timedelta(days=365)
        )
        cls.current_version = RefbookVersion.objects.create(
            refbook=cls.refbook, version='2.0', start_date=today - timedelta(days=30)
        )
        cls.future_version = RefbookVersion.objects.create(
            refbook=cls.refbook, version='3.0', start_date=today + timedelta(days=365)
        )
        RefbookVersion.objects.create(refbook=cls.future_refbook, version='1.0', start_date=today + timedelta(days=365))

        RefbookElement.objects.create(version=cls.old_version, code='1', value='Терапевт')
        RefbookElement.objects.create(version=cls.current_version, code='1', value='Кардиолог')
        RefbookElement.objects.create(version=cls.current_version, code='2', value='Хирург')
        RefbookElement.objects.create(version=cls.future_version, code='1', value='Невролог')

    def test_list_refbooks(self) -> None:
        url = reverse('refbooks:refbook-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['refbooks']), 3)
        self.assertEqual(
            {item['code'] for item in response.data['refbooks']},
            {'SPEC', 'FUTURE', 'EMPTY'},
        )

    def test_list_refbooks_by_date(self) -> None:
        url = reverse('refbooks:refbook-list')
        response = self.client.get(url, {'date': timezone.localdate().isoformat()})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['refbooks']), 1)
        self.assertEqual(response.data['refbooks'][0]['code'], 'SPEC')

    def test_list_refbooks_date_inclusive(self) -> None:
        url = reverse('refbooks:refbook-list')
        response = self.client.get(url, {'date': self.old_version.start_date.isoformat()})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['refbooks'][0]['code'], 'SPEC')

    def test_list_refbooks_invalid_date(self) -> None:
        url = reverse('refbooks:refbook-list')
        response = self.client.get(url, {'date': 'invalid-date'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_elements_current_version(self) -> None:
        url = reverse('refbooks:refbook-elements', kwargs={'refbook_id': self.refbook.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['elements'],
            [
                {'code': '1', 'value': 'Кардиолог'},
                {'code': '2', 'value': 'Хирург'},
            ],
        )

    def test_elements_specific_version(self) -> None:
        url = reverse('refbooks:refbook-elements', kwargs={'refbook_id': self.refbook.pk})
        response = self.client.get(url, {'version': '1.0'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['elements'], [{'code': '1', 'value': 'Терапевт'}])

    def test_elements_future_version(self) -> None:
        url = reverse('refbooks:refbook-elements', kwargs={'refbook_id': self.refbook.pk})
        response = self.client.get(url, {'version': '3.0'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['elements'], [{'code': '1', 'value': 'Невролог'}])

    def test_elements_unknown_refbook(self) -> None:
        url = reverse('refbooks:refbook-elements', kwargs={'refbook_id': 999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_elements_unknown_version(self) -> None:
        url = reverse('refbooks:refbook-elements', kwargs={'refbook_id': self.refbook.pk})
        response = self.client.get(url, {'version': '99.0'})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_elements_no_current_version(self) -> None:
        url = reverse('refbooks:refbook-elements', kwargs={'refbook_id': self.future_refbook.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_check_element_valid(self) -> None:
        url = reverse('refbooks:refbook-check-element', kwargs={'refbook_id': self.refbook.pk})
        response = self.client.get(url, {'code': '1', 'value': 'Кардиолог'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'valid': True})

    def test_check_element_wrong_value(self) -> None:
        url = reverse('refbooks:refbook-check-element', kwargs={'refbook_id': self.refbook.pk})
        response = self.client.get(url, {'code': '1', 'value': 'Терапевт'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'valid': False})

    def test_check_element_wrong_code(self) -> None:
        url = reverse('refbooks:refbook-check-element', kwargs={'refbook_id': self.refbook.pk})
        response = self.client.get(url, {'code': '999', 'value': 'Кардиолог'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'valid': False})

    def test_check_element_specific_version(self) -> None:
        url = reverse('refbooks:refbook-check-element', kwargs={'refbook_id': self.refbook.pk})
        response = self.client.get(url, {'version': '1.0', 'code': '1', 'value': 'Терапевт'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'valid': True})

    def test_check_element_future_version(self) -> None:
        url = reverse('refbooks:refbook-check-element', kwargs={'refbook_id': self.refbook.pk})
        response = self.client.get(url, {'version': '3.0', 'code': '1', 'value': 'Невролог'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'valid': True})

    def test_check_element_missing_params(self) -> None:
        url = reverse('refbooks:refbook-check-element', kwargs={'refbook_id': self.refbook.pk})

        for params in ({}, {'code': '1'}, {'value': 'Кардиолог'}):
            with self.subTest(params=params):
                response = self.client.get(url, params)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_element_unknown_version(self) -> None:
        url = reverse('refbooks:refbook-check-element', kwargs={'refbook_id': self.refbook.pk})
        response = self.client.get(url, {'version': '99.0', 'code': '1', 'value': 'Кардиолог'})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_check_element_unknown_refbook(self) -> None:
        url = reverse('refbooks:refbook-check-element', kwargs={'refbook_id': 999})
        response = self.client.get(url, {'code': '1', 'value': 'Кардиолог'})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
