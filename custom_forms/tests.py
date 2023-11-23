from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from django.core.validators import validate_email
from .validators import validate_phone_number, validate_date
from .utils import type_caster
from django.core.exceptions import ValidationError

from .models import CustomForm


class ValidationTest(TestCase):
    """Data Validation test."""

    def test_email_validation(self):
        """Default django email_validation. Now we know handled email formats."""
        email_templates = [
            'simple@example.com',
            'very.common@example.com',
            'x@example.com',
            'long.email-address-with-hyphens@and.subdomains.example.com',
            'user.name+tag+sorting@example.com',
            'name/surname@example.com',
            'example@s.example',
            '"john..doe"@example.org',
            'mailhost!username@example.org',
            'user%example.com@example.org',
            'user-@example.org',
            'postmaster@[123.123.123.123]',
        ]
        fails = []

        for template in email_templates:
            try:
                validate_email(template)
            except ValidationError as msg:
                fails.append((template, msg))

        if len(fails) > 0:
            fails_repr = ',\n'.join([f'On template:{template} with message:{msg}'
                                     for template, msg in fails])

            self.fail("Unexpected raise ValidationError on some email templates:\n" + fails_repr)

    def test_phone_number_validation_errors(self):
        """Only Russian phone numbers with format: '+7 xxx xxx xx xx'"""

        # KZ number starts from +77
        self.assertRaises(ValidationError, validate_phone_number, '+77 342 234 51 23')

        # Other single number country code
        self.assertRaises(ValidationError, validate_phone_number, '+9 342 234 51 23')

        # first triade
        self.assertRaises(ValidationError, validate_phone_number, '+7 34  234 51 23')
        self.assertRaises(ValidationError, validate_phone_number, '+7 3 2 234 51 23')
        self.assertRaises(ValidationError, validate_phone_number, '+7 3222 234 51 23')
        self.assertRaises(ValidationError, validate_phone_number, '+7 e22 234 51 23')

        # second triade
        self.assertRaises(ValidationError, validate_phone_number, '+7 342 23  51 23')
        self.assertRaises(ValidationError, validate_phone_number, '+7 342 2 4 51 23')
        self.assertRaises(ValidationError, validate_phone_number, '+7 342 2342 51 23')
        self.assertRaises(ValidationError, validate_phone_number, '+7 342 2k4 51 23')

        # first double
        self.assertRaises(ValidationError, validate_phone_number, '+7 342 234 5  23')
        self.assertRaises(ValidationError, validate_phone_number, '+7 342 234 512 23')
        self.assertRaises(ValidationError, validate_phone_number, '+7 342 234 5a 23')

        # first double
        self.assertRaises(ValidationError, validate_phone_number, '+7 342 234 51  3')
        self.assertRaises(ValidationError, validate_phone_number, '+7 342 234 51 231')
        self.assertRaises(ValidationError, validate_phone_number, '+7 342 234 51 2I')

        # spaces
        self.assertRaises(ValidationError, validate_phone_number, '+7342 234 51 21')
        self.assertRaises(ValidationError, validate_phone_number, '+7 342234 51 21')
        self.assertRaises(ValidationError, validate_phone_number, '+7 342 23451 21')
        self.assertRaises(ValidationError, validate_phone_number, '+7 342 234 5121')
        self.assertRaises(ValidationError, validate_phone_number, '+7  342 234 51 21')
        self.assertRaises(ValidationError, validate_phone_number, '+7 342  234 51 21')
        self.assertRaises(ValidationError, validate_phone_number, '+7  342 234  51 21')
        self.assertRaises(ValidationError, validate_phone_number, '+7 342 234 51  21')
        self.assertRaises(ValidationError, validate_phone_number, ' +7 342 234 51 21')
        self.assertRaises(ValidationError, validate_phone_number, '+7 342 234 51 21 ')

    def test_phone_number_validation_pass(self):
        """Must be OK"""
        try:
            validate_phone_number('+7 543 234 98 32')
        except ValidationError as error:
            self.fail(error)

    def test_date_validation_errors(self):
        """Two available formats: 'yyyy-mm-dd' and 'dd.mm.yyyy' should be able to cast as date()."""
        # text
        self.assertRaises(ValidationError, validate_date, 'randomtx')

        # digits
        self.assertRaises(TypeError, validate_date, 54523422)

        # digit string in right format (not able to cast date)
        self.assertRaises(ValidationError, validate_date, '5452-34-22')
        self.assertRaises(ValidationError, validate_date, '54.52.3422')

        # shorter then expected
        self.assertRaises(ValidationError, validate_date, '00-10-22')
        self.assertRaises(ValidationError, validate_date, '2000-1-22')
        self.assertRaises(ValidationError, validate_date, '2000-12-2')
        self.assertRaises(ValidationError, validate_date, '2000-1-2')
        self.assertRaises(ValidationError, validate_date, '00-1-2')
        self.assertRaises(ValidationError, validate_date, '1.1.20')
        self.assertRaises(ValidationError, validate_date, '1.1.2000')
        self.assertRaises(ValidationError, validate_date, '1.12.2000')
        self.assertRaises(ValidationError, validate_date, '12.1.2000')

    def test_date_validation_pass_dots(self):
        """Must be OK"""
        try:
            validate_date('21.11.2023')
        except ValidationError as error:
            self.fail(error)

    def test_date_validation_pass_kebab(self):
        """Must be OK"""
        try:
            validate_date('2023-11-21')
        except ValidationError as error:
            self.fail(error)


class TypeCasterTest(TestCase):
    """Date: DT, email: EM, phone number: PN and another data TX."""
    def test_date_type(self):
        self.assertEquals(type_caster('21.11.2023'), 'DT')
        self.assertEquals(type_caster('2023-11-21'), 'DT')

    def test_email_type(self):
        self.assertEquals(type_caster('some@example.domain'), 'EM')

    def test_phone_number_type(self):
        self.assertEquals(type_caster('+7 632 635 23 32'), 'PN')

    def test_text_type(self):
        self.assertEquals(type_caster('Some text'), 'TX')
        self.assertEquals(type_caster('36256'), 'TX')
        self.assertEquals(type_caster('{"str": ["data", "in", "json"]}'), 'TX')

    def test_type_error(self):
        self.assertRaises(TypeError, type_caster, 32)
        self.assertRaises(TypeError, type_caster, 3.2)
        self.assertRaises(TypeError, type_caster, ['a', 'b', 'c'])
        self.assertRaises(TypeError, type_caster, object)


class GetFormHttpMethodsTest(TestCase):
    """Test available HTTP methods for custom_form:get_form (should be only post)."""
    def setUpTestData(cls):
        cls._client = Client()

    def test_get(self):
        response = self._client.get(reverse('custom_forms:get_form'),
                                    data={'list_field': [1, 'text']})
        self.assertEquals(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_post(self):
        response = self._client.post(reverse('custom_forms:get_form'),
                                     data={'list_field': [1, 'text']})
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def test_put(self):
        response = self._client.put(reverse('custom_forms:get_form'),
                                    data={'list_field': [1, 'text']})
        self.assertEquals(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        response = self._client.delete(reverse('custom_forms:get_form'),
                                       data={'list_field': [1, 'text']})
        self.assertEquals(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class GetFormPostTypesTest(TestCase):
    """Testing 'custom_form:get_form' endpoint with form fields that doesn't exist in DB."""
    def setUpTestData(cls):
        cls._client = Client()

    def test_text(self):
        response = self._client.post(reverse('custom_forms:get_form'),
                                     data={'list_field': [1, 'text']})
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, {'list_field': 'TX'})

    def test_date(self):
        response = self._client.post(reverse('custom_forms:get_form'),
                                     data={'start_date': '12.09.1997',
                                           'end_date': '2023-01-01'})
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, {'start_date': 'DT',
                                          'end_date': 'DT'})

    def test_date_value_error(self):
        """On ValueError in validation should set type as Text(TX)"""
        response = self._client.post(reverse('custom_forms:get_form'),
                                     data={'start_date': '32.09.1997',
                                           'end_date': '2023-01-00'})
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, {'start_date': 'TX',
                                          'end_date': 'TX'})

    def test_email(self):
        response = self._client.post(reverse('custom_forms:get_form'),
                                     data={'email': 'some@example.ml'})
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, {'email': 'EM'})

    def test_phone_number(self):
        response = self._client.post(reverse('custom_forms:get_form'),
                                     data={'phone': '+7 476 324 23 23'})
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, {'phone': 'PN'})


class GetFormPostDBTest(TestCase):
    """Testing that 'custom_form:get_form' returns expected data from DB."""
    def setUpTestData(cls):
        cls._samples = {
            'TX1': {'f_name': 'TX1',
                    'f_type': 'TX'},
            'TX2': {'f_name': 'TX2',
                    'f_type': 'TX'},
            'DT1': {'f_name': 'DT1',
                    'f_type': 'DT'},
            'DT2': {'f_name': 'DT2',
                    'f_type': 'DT'},
            'PN': {'f_name': 'PN',
                   'f_type': 'PN'},
            'EM': {'f_name': 'EM',
                   'f_type': 'EM'},
        }

        cls._client = Client()
        CustomForm.objects.create(
            name="First text with date",
            fields=[cls._samples['TX1'],
                    cls._samples['DT1']]
        )
        CustomForm.objects.create(
            name="All field types",
            fields=[cls._samples['TX1'],
                    cls._samples['DT1'],
                    cls._samples['PN'],
                    cls._samples['EM']]
        )
        CustomForm.objects.create(
            name="Second text with date",
            fields=[cls._samples['TX1'],
                    cls._samples['DT1']]
        )
        CustomForm.objects.create(
            name="Text with date1 and date2",
            fields=[cls._samples['TX1'],
                    cls._samples['DT1'],
                    cls._samples['DT2']]
        )

    def test_unknown_field(self):
        """Returns {f_name: f_type} reflection when didn't find form that contains each field."""
        response = self._client.post(reverse('custom_forms:get_form'),
                                     data={'unknown_field': 'Any data'})
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, {'unknown_field': 'TX'})

    def test_single_text_field(self):
        response = self._client.post(reverse('custom_forms:get_form'),
                                     data={'TX1': 'Any text data'})
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, {'name': 'First text with date'})

    def test_all_field_types(self):
        response = self._client.post(reverse('custom_forms:get_form'),
                                     data={'TX1': 'Any text data',
                                           'DT1': '21.11.2023',
                                           'PN': '+7 324 234 23 45',
                                           'EM': 'some@example.domain'})
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, {'name': 'All field types'})

    def test_with_date_ordering(self):
        """
        Returns {'name': 'First text with date'}:
            1. first record
            2. minimal count of fields
            3. contains all sent data.
        """
        response = self._client.post(reverse('custom_forms:get_form'),
                                     data={'TX1': 'Any text data',
                                           'DT1': '21.11.2023'})
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, {'name': 'First text with date'})

    def test_partial_existing(self):
        """Returns form prototype."""
        response = self._client.post(reverse('custom_forms:get_form'),
                                     data={'TX1': 'Any text data',
                                           'DT1': '21.11.2023',
                                           'new_field': 'some text'})
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, {'TX1': 'TX', 'DT1': 'DT', 'new_field': 'TX'})

    def test_text_n_double_dates(self):
        response = self._client.post(reverse('custom_forms:get_form'),
                                     data={'TX1': 'text data',
                                           'DT1': '2023-11-21',
                                           'DT2': '21.11.2023'})
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, {'name': 'Text with date1 and date2'})

    def test_names_exists_but_wrong_types(self):
        """Returns from prototype.
            BUG In query or DB response:
                1. Type of DT1 is TX
                    get_form:$fields= [
                        {'f_name': 'TX1', 'f_type': 'TX'},
                        {'f_name': 'DT1', 'f_type': 'TX'},
                        {'f_name': 'DT2', 'f_type': 'DT'}
                    ]
                2. In query prototype we see that f_type of DT1 is TX:
                    get_form:$candidates.query = '''
                        SELECT
                            "custom_forms_customform"."name",
                            "custom_forms_customform"."fields"
                        FROM "custom_forms_customform"
                        WHERE (
                            "custom_forms_customform"."fields" = {'f_name': 'TX1', 'f_type': 'TX'} AND
                            "custom_forms_customform"."fields" = {'f_name': 'DT1', 'f_type': 'TX'} AND
                            "custom_forms_customform"."fields" = {'f_name': 'DT2', 'f_type': 'DT'}
                        )
                3. But QuerySet is not empty:
                    len(get_form:$candidates)=1
                    get_form:$best_form = <QuerySet [<CustomForm: CustomForm object (Text with date1 and date2)>]>

                May mongo ignore f_type after find f_name?
                    '''
        """

        response = self._client.post(reverse('custom_forms:get_form'),
                                     data={'TX1': 'text data',
                                           'DT1': '2023-11-35', # <------- Error here: can't cast to date when day=35
                                           'DT2': '21.11.2023'})
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.data, {'TX1': 'TX',
                                          'DT1': 'TX', # <-------------- Must be Text
                                          'DT2': 'DT'})
