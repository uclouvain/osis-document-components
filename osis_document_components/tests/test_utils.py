# ##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2025 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
# ##############################################################################
from django.test import TestCase
from osis_document_components.tests.factories import TokenFactory

from osis_document_components.utils import is_uuid, generate_filename

class IsUuidTestCase(TestCase):
    def test_is_uuid_case_token_format_assert_false(self):
        self.assertFalse(is_uuid(TokenFactory.token()))

    def test_is_uuid_case_integer_assert_false(self):
        self.assertFalse(is_uuid(1))

    def test_is_uuid_case_uuid_in_str_format_assert_true(self):
        self.assertTrue(is_uuid('a91c3af8-91eb-4b68-96fc-0769a28a95c3'))

    def test_is_uuid_case_uuid_class_assert_true(self):
        self.assertTrue(is_uuid(uuid.UUID('a91c3af8-91eb-4b68-96fc-0769a28a95c3')))


class GenerateFilenameTestCase(TestCase):
    def test_with_callable_upload_to_without_instance(self):
        generated_filename = generate_filename(
            instance=None,
            filename='my_file.txt',
            upload_to=(lambda _, filename: 'path/{}'.format(filename)),
        )
        self.assertEqual(generated_filename, 'path/my_file.txt')

    def test_with_callable_upload_to_with_instance(self):
        generated_filename = generate_filename(
            instance=Mock(attr_a=10),
            filename='my_file.txt',
            upload_to=(lambda instance, filename: 'path/{}/{}'.format(instance.attr_a, filename)),
        )
        self.assertEqual(generated_filename, 'path/10/my_file.txt')

    def test_with_string_upload_to(self):
        generated_filename = generate_filename(
            instance=None,
            filename='my_file.txt',
            upload_to='my-path/',
        )
        self.assertEqual(generated_filename, 'my-path/my_file.txt')

    def test_with_date_string_upload_to(self):
        with patch('osis_document.utils.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value = date(2022, 1, 10)
            mock_datetime.side_effect = lambda *args, **kw: date(*args, **kw)

            generated_filename = generate_filename(
                instance=None,
                filename='my_file.txt',
                upload_to='%Y/%m/%d',
            )
            self.assertEqual(generated_filename, '2022/01/10/my_file.txt')

    def test_with_undefined_upload(self):
        generated_filename = generate_filename(
            instance=None,
            filename='my_file.txt',
            upload_to=None,
        )
        self.assertEqual(generated_filename, 'my_file.txt')
