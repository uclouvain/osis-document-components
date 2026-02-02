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
import os

from django.apps import AppConfig
from django.conf import settings
from rest_framework.serializers import ModelSerializer


class OsisDocumentComponentsConfig(AppConfig):
    name = 'osis_document_components'

    def ready(self):
        # Add FileFieldSerializer the default_serializer_mapping
        from osis_document_components.fields import FileField
        from osis_document_components.serializers import FileField as FileFieldSerializer
        ModelSerializer.serializer_field_mapping[FileField] = FileFieldSerializer

        settings.OSIS_DOCUMENT_COMPONENTS_SAVE_RAW_CONTENT_REMOTELY_TIMEOUT = int(
            os.environ.get('OSIS_DOCUMENT_COMPONENTS_SAVE_RAW_CONTENT_REMOTELY_TIMEOUT', 20)
        )
        settings.OSIS_DOCUMENT_COMPONENTS_GET_RAW_CONTENT_REMOTELY_TIMEOUT = int(
            os.environ.get('OSIS_DOCUMENT_COMPONENTS_GET_RAW_CONTENT_REMOTELY_TIMEOUT', 20)
        )
        settings.OSIS_DOCUMENT_COMPONENTS_GET_REMOTE_METADATA_TIMEOUT = int(
            os.environ.get('OSIS_DOCUMENT_COMPONENTS_GET_REMOTE_METADATA_TIMEOUT', 5)
        )
        settings.OSIS_DOCUMENT_COMPONENTS_GET_REMOTE_TOKEN_TIMEOUT = int(
            os.environ.get('OSIS_DOCUMENT_COMPONENTS_GET_REMOTE_TOKEN_TIMEOUT', 5)
        )
        settings.OSIS_DOCUMENT_COMPONENTS_DOCUMENTS_REMOTE_DUPLICATE_TIMEOUT = int(
            os.environ.get('OSIS_DOCUMENT_COMPONENTS_DOCUMENTS_REMOTE_DUPLICATE_TIMEOUT', 20)
        )
        settings.OSIS_DOCUMENT_COMPONENTS_CONFIRM_REMOTE_UPLOAD_TIMEOUT = int(
            os.environ.get('OSIS_DOCUMENT_COMPONENTS_CONFIRM_REMOTE_UPLOAD_TIMEOUT', 5)
        )
        settings.OSIS_DOCUMENT_COMPONENTS_LAUNCH_POST_PROCESSING_TIMEOUT = int(
            os.environ.get('OSIS_DOCUMENT_COMPONENTS_LAUNCH_POST_PROCESSING_TIMEOUT', 60)
        )
        settings.OSIS_DOCUMENT_COMPONENTS_DECLARE_REMOTE_FILES_AS_DELETED_TIMEOUT = int(
            os.environ.get('OSIS_DOCUMENT_COMPONENTS_DECLARE_REMOTE_FILES_AS_DELETED_TIMEOUT', 2)
        )
        settings.OSIS_DOCUMENT_COMPONENTS_GET_PROGRESS_ASYNC_POST_PROCESSING_TIMEOUT = int(
            os.environ.get('OSIS_DOCUMENT_COMPONENTS_GET_PROGRESS_ASYNC_POST_PROCESSING_TIMEOUT', 2)
        )
        settings.OSIS_DOCUMENT_COMPONENTS_CHANGE_REMOTE_METADATA_TIMEOUT = int(
            os.environ.get('OSIS_DOCUMENT_COMPONENTS_CHANGE_REMOTE_METADATA_TIMEOUT', 2)
        )
