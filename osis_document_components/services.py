# ##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2026 Université catholique de Louvain (http://www.uclouvain.be)
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
from typing import Union, List, Dict, Iterable, Optional
from uuid import UUID

import requests
from django.conf import settings
from requests import HTTPError, Timeout

from osis_document_components.enums import DocumentExpirationPolicy
from osis_document_components.exceptions import SaveRawContentRemotelyException, FileInfectedException, \
    UploadInvalidException, OsisDocumentTimeout


HTTP_200_OK = 200
HTTP_204_NO_CONTENT = 204
HTTP_201_CREATED = 201
HTTP_404_NOT_FOUND = 404
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_206_PARTIAL_CONTENT = 206


def save_raw_content_remotely(content: bytes, name: str, mimetype: str):
    """Save a raw file by sending it over the network."""
    url = "{}request-upload".format(settings.OSIS_DOCUMENT_BASE_URL)
    data = {'file': (name, content, mimetype)}

    # Create the request
    try:
        response = requests.post(
            url,
            files=data,
            timeout=settings.OSIS_DOCUMENT_COMPONENTS_SAVE_RAW_CONTENT_REMOTELY_TIMEOUT
        )
    except Timeout as exc:
        raise OsisDocumentTimeout(str(exc)) from exc

    if response.status_code != 201:
        raise SaveRawContentRemotelyException(response)
    return response.json().get('token')


def get_raw_content_remotely(token: str):
    """Given a token, return the file raw."""
    try:
        response = requests.get(
            f"{settings.OSIS_DOCUMENT_BASE_URL}file/{token}",
            timeout=settings.OSIS_DOCUMENT_COMPONENTS_GET_RAW_CONTENT_REMOTELY_TIMEOUT
        )
    except Timeout as exc:
        raise OsisDocumentTimeout(str(exc)) from exc
    except HTTPError:
        return None

    if response.status_code is not HTTP_200_OK:
        return None
    return response.content


def get_remote_metadata(token: str) -> Union[dict, None]:
    """Given a token, return the remote metadata."""
    url = "{}metadata/{}".format(settings.OSIS_DOCUMENT_BASE_URL, token)
    try:
        response = requests.get(url, timeout=settings.OSIS_DOCUMENT_COMPONENTS_GET_REMOTE_METADATA_TIMEOUT)
    except Timeout as exc:
        raise OsisDocumentTimeout(str(exc)) from exc
    except HTTPError:
        return None

    if response.status_code is not HTTP_200_OK:
        return None
    return response.json()


def get_several_remote_metadata(tokens: List[str]) -> Dict[str, dict]:
    """Given a list of tokens, return a dictionary associating each token to upload metadata."""
    url = "{}metadata".format(settings.OSIS_DOCUMENT_BASE_URL)
    try:
        response = requests.post(
            url,
            json=tokens,
            headers={'X-Api-Key': settings.OSIS_DOCUMENT_API_SHARED_SECRET},
            timeout=settings.OSIS_DOCUMENT_COMPONENTS_GET_REMOTE_METADATA_TIMEOUT,
        )
        if response.status_code == HTTP_200_OK:
            return response.json()
    except Timeout as exc:
        raise OsisDocumentTimeout(str(exc)) from exc
    except HTTPError:
        pass
    return {}


def get_remote_token(
    uuid: Union[str, UUID],
    write_token: bool = False,
    wanted_post_process: str = None,
    custom_ttl=None,
    for_modified_upload: bool = False,
):
    """
    Given an uuid, return a writing or reading remote token.
    The custom_ttl parameter is used to define the validity period of the token
    The wanted_post_process parameter is used to specify which post-processing action you want the output files for
    (example : PostProcessingWanted.CONVERT.name)
    """
    is_valid_uuid = __stringify_uuid_and_check_uuid_validity(uuid_input=uuid)
    if not is_valid_uuid.get('uuid_valid'):
        return None
    else:
        validated_uuid = is_valid_uuid.get('uuid_stringify')
        url = "{base_url}{token_type}-token/{uuid}".format(
            base_url=settings.OSIS_DOCUMENT_BASE_URL,
            token_type='write' if write_token else 'read',
            uuid=validated_uuid,
        )
        try:
            response = requests.post(
                url,
                json={
                    'uuid': validated_uuid,
                    'wanted_post_process': wanted_post_process,
                    'custom_ttl': custom_ttl,
                    'for_modified_upload': for_modified_upload,
                },
                headers={'X-Api-Key': settings.OSIS_DOCUMENT_API_SHARED_SECRET},
                timeout=settings.OSIS_DOCUMENT_COMPONENTS_GET_REMOTE_TOKEN_TIMEOUT,
            )
            if response.status_code == HTTP_404_NOT_FOUND:
                return UploadInvalidException.__class__.__name__
            json = response.json()
            if (
                    response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
                    and json.get('detail', '') == FileInfectedException.error_code
            ):
                return FileInfectedException.__class__.__name__
            return json.get('token') or json
        except Timeout as exc:
            raise OsisDocumentTimeout(str(exc)) from exc
        except HTTPError:
            return None


def get_remote_tokens(
    uuids: List[str],
    wanted_post_process=None,
    custom_ttl=None,
    for_modified_upload: bool = False,
) -> Dict[str, str]:
    """Given a list of uuids, a type of post-processing and a custom TTL in second,
    return a dictionary associating each uuid to a reading token.
    The custom_ttl parameter is used to define the validity period of the token
    The wanted_post_process parameter is used to specify which post-processing action you want the output files for
    (example : PostProcessingWanted.CONVERT.name)
    """
    validated_uuids = []
    for uuid in uuids:
        is_valid_uuid = __stringify_uuid_and_check_uuid_validity(uuid_input=uuid)
        if is_valid_uuid.get('uuid_valid'):
            validated_uuids.append(is_valid_uuid.get('uuid_stringify'))
    if len(uuids) != len(validated_uuids):
        raise TypeError
    url = "{base_url}read-tokens".format(base_url=settings.OSIS_DOCUMENT_BASE_URL)
    try:
        data = {'uuids': validated_uuids, 'for_modified_upload': for_modified_upload}
        if wanted_post_process:
            data.update({'wanted_post_process': wanted_post_process})
        if custom_ttl:
            data.update({'custom_ttl': custom_ttl})
        response = requests.post(
            url,
            json=data,
            headers={'X-Api-Key': settings.OSIS_DOCUMENT_API_SHARED_SECRET},
            timeout=settings.OSIS_DOCUMENT_COMPONENTS_GET_REMOTE_TOKEN_TIMEOUT,
        )
        if response.status_code == HTTP_201_CREATED:
            return {uuid: item.get('token') for uuid, item in response.json().items() if 'error' not in item}
        if response.status_code in [HTTP_206_PARTIAL_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR]:
            return response.json()
    except Timeout as exc:
        raise OsisDocumentTimeout(str(exc)) from exc
    except HTTPError:
        pass
    return {}


def documents_remote_duplicate(
    uuids: List[str],
    with_modified_upload: bool = False,
    upload_path_by_uuid: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """
    Duplicate a list of documents.
    uuids: List of uuids of the documents to duplicate.
    with_modified_upload: boolean to know if the duplication is also necessary for the modified uploads. Note that
    the uuids of the modified uploads don't must be passed to the API and the duplicated ones are not returned (only
    the original uuids must be used).
    upload_path_by_uuid: dict {uuid: str} to specify for each uuid, where the duplicated file should be saved. If not
    specified for one file, the duplicated file will be saved in the same location as the original file.
    :return: dict {uuid: uuid} A dictionary associating each document uuid with the uuid of the duplicated document. If
    an error occurs for one specific document, the uuid of this document is not returned.
    """
    validated_uuids = []

    # Check the validity of the uuids
    for document_uuid in uuids:
        is_valid_uuid = __stringify_uuid_and_check_uuid_validity(uuid_input=document_uuid)
        if is_valid_uuid.get('uuid_valid'):
            validated_uuids.append(is_valid_uuid.get('uuid_stringify'))

    if len(uuids) != len(validated_uuids):
        raise TypeError

    url = "{base_url}duplicate".format(base_url=settings.OSIS_DOCUMENT_BASE_URL)
    try:
        response = requests.post(
            url,
            json={
                'uuids': validated_uuids,
                'with_modified_upload': with_modified_upload,
                'upload_path_by_uuid': upload_path_by_uuid,
            },
            headers={'X-Api-Key': settings.OSIS_DOCUMENT_API_SHARED_SECRET},
            timeout=settings.OSIS_DOCUMENT_COMPONENTS_DOCUMENTS_REMOTE_DUPLICATE_TIMEOUT
        )

        if response.status_code == HTTP_201_CREATED:
            return {
                original_uuid: item['upload_id']
                for original_uuid, item in response.json().items()
                if 'upload_id' in item
            }
    except Timeout as exc:
        raise OsisDocumentTimeout(str(exc)) from exc
    except HTTPError:
        pass
    return {}


def confirm_remote_upload(
    token,
    upload_to=None,
    metadata=None,
    document_expiration_policy=DocumentExpirationPolicy.NO_EXPIRATION.value,
    related_model=None,
    related_model_instance=None,
):
    url = "{}confirm-upload/{}".format(settings.OSIS_DOCUMENT_BASE_URL, token)
    data = {}
    # Add facultative params
    if upload_to:
        # The 'upload_to' property is explicitly defined as a string
        data['upload_to'] = upload_to
    elif related_model:
        # The 'upload_to' property will be automatically computed in api side
        instance_filter_fields = related_model.pop('instance_filter_fields', None)
        if instance_filter_fields and related_model_instance:
            # And will be based on a specific instance
            related_model['instance_filters'] = {
                key: getattr(related_model_instance, key, None) for key in instance_filter_fields
            }
        data['related_model'] = related_model

    if document_expiration_policy:
        data['document_expiration_policy'] = document_expiration_policy
    if metadata:
        data['metadata'] = metadata

    try:
        # Do the request
        response = requests.post(
            url,
            json=data,
            headers={'X-Api-Key': settings.OSIS_DOCUMENT_API_SHARED_SECRET},
            timeout=settings.OSIS_DOCUMENT_COMPONENTS_CONFIRM_REMOTE_UPLOAD_TIMEOUT,
        )
    except Timeout as exc:
        raise OsisDocumentTimeout(str(exc)) from exc
    return response.json().get('uuid')


def launch_post_processing(
    uuid_list: List,
    async_post_processing: bool,
    post_processing_types: List[str],
    post_process_params: Dict[str, Dict[str, str]],
):
    url = "{}post-processing".format(settings.OSIS_DOCUMENT_BASE_URL)
    data = {
        'async_post_processing': async_post_processing,
        'post_process_types': post_processing_types,
        'files_uuid': uuid_list,
        'post_process_params': post_process_params,
    }
    try:
        response = requests.post(
            url,
            json=data,
            headers={'X-Api-Key': settings.OSIS_DOCUMENT_API_SHARED_SECRET},
            timeout=settings.OSIS_DOCUMENT_COMPONENTS_LAUNCH_POST_PROCESSING_TIMEOUT,
        )
    except Timeout as exc:
        raise OsisDocumentTimeout(str(exc)) from exc
    return response.json() if not async_post_processing else response


def declare_remote_files_as_deleted(uuid_list: Iterable[UUID]):
    url = "{}declare-files-as-deleted".format(settings.OSIS_DOCUMENT_BASE_URL)
    data = {'files': [str(uuid) for uuid in uuid_list]}
    try:
        response = requests.post(
            url,
            json=data,
            headers={'X-Api-Key': settings.OSIS_DOCUMENT_API_SHARED_SECRET},
            timeout=settings.OSIS_DOCUMENT_COMPONENTS_DECLARE_REMOTE_FILES_AS_DELETED_TIMEOUT,
        )

        if response.status_code != HTTP_204_NO_CONTENT:
            import logging
            logger = logging.getLogger(settings.DEFAULT_LOGGER)
            logger.error("An error occured when calling declare-files-as-deleted: {}".format(response.text))
    except Timeout as exc:
        import logging
        logger = logging.getLogger(settings.DEFAULT_LOGGER)
        logger.error("Timeout occurred when calling declare-files-as-deleted: {}".format(str(exc)))


def get_progress_async_post_processing(uuid: str, wanted_post_process: str = None):
    """Given an uuid and a type of post-processing,
    returns an int corresponding to the post-processing progress percentage
    The wanted_post_process parameter is used to specify the post-processing action you want to get progress to.
    (example : PostProcessingType.CONVERT.name)
    """
    url = "{base_url}get-progress-async-post-processing/{uuid}".format(
        base_url=settings.OSIS_DOCUMENT_BASE_URL,
        uuid=uuid,
    )
    try:
        response = requests.post(
            url,
            json={'pk': uuid, 'wanted_post_process': wanted_post_process},
            headers={'X-Api-Key': settings.OSIS_DOCUMENT_API_SHARED_SECRET},
            timeout=settings.OSIS_DOCUMENT_COMPONENTS_GET_PROGRESS_ASYNC_POST_PROCESSING_TIMEOUT,
        )
    except Timeout as exc:
        raise OsisDocumentTimeout(str(exc)) from exc
    return response.json()


def change_remote_metadata(token, metadata):
    """Update metadata of a remote document and return the updated metadata if successful."""
    url = "{}change-metadata/{}".format(settings.OSIS_DOCUMENT_BASE_URL, token)

    try:
        response = requests.post(
            url=url,
            json=metadata,
            headers={'X-Api-Key': settings.OSIS_DOCUMENT_API_SHARED_SECRET},
            timeout=settings.OSIS_DOCUMENT_COMPONENTS_CHANGE_REMOTE_METADATA_TIMEOUT,
        )
    except Timeout as exc:
        raise OsisDocumentTimeout(str(exc)) from exc
    return response.json()


def __stringify_uuid_and_check_uuid_validity(uuid_input: Union[str, UUID]) -> Dict[str, Union[str, bool]]:
    """
    Checks the validity of an uuid and converts it to a string if necessary
    """
    results = {
        'uuid_valid': False,
        'uuid_stringify': '',
    }
    if isinstance(uuid_input, str):
        try:
            UUID(uuid_input)
            results['uuid_valid'] = True
            results['uuid_stringify'] = uuid_input
        except ValueError:
            results['valid'] = False
    elif isinstance(uuid_input, UUID):
        results['uuid_valid'] = True
        results['uuid_stringify'] = str(uuid_input)
    else:
        raise TypeError
    return results
