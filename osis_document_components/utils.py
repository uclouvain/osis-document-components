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
import datetime
import posixpath

from django.conf import settings


def is_uuid(value: Union[str, uuid.UUID]) -> bool:
    if isinstance(value, uuid.UUID):
        return True
    with contextlib.suppress(ValueError, AttributeError):
        uuid.UUID(hex=value)
        return True
    return False


def get_file_url(token: str) -> str:
    """Get the raw file url given a token"""
    # We can not use reverse because the potential prefix would be present twice
    return '{base_url}file/{token}'.format(
        base_url=settings.OSIS_DOCUMENT_BASE_URL,
        token=token,
    )

def generate_filename(instance, filename, upload_to):
    """
    Apply (if callable) or prepend (if a string) upload_to to the filename. If you specify a string value,
    it may contain strftime() formatting, which will be replaced by the date/time of the file upload.
    """
    if callable(upload_to):
        filename = upload_to(instance, filename)
    elif upload_to:
        dirname = datetime.datetime.now().strftime(upload_to)
        filename = posixpath.join(dirname, filename)
    return filename
