from typing import TypeVar, Generic
from EHR import OriginalVersion  # Replace with the actual import for OriginalVersion

I = TypeVar('I')
O = TypeVar('O')

class OriginalVersionUtil:
    """
    Utility class for creating copies of OriginalVersion objects with new output data.
    """

    @staticmethod
    def original_version_copy_with_data(input_version: 'OriginalVersion[I]', output_data: O) -> 'OriginalVersion[O]':
        """
        Creates a copy of the given input_version with the given outputData.

        :param input_version: OriginalVersion to create a copy of
        :param output_data: used as the output OriginalVersion.get_data()
        :return: OriginalVersion with output_data
        """
        return OriginalVersion(
            uid=input_version.uid,
            preceding_version_uid=input_version.preceding_version_uid,
            data=output_data,
            lifecycle_state=input_version.lifecycle_state,
            commit_audit=input_version.commit_audit,
            contribution=input_version.contribution,
            signature=input_version.signature,
            other_input_version_uids=input_version.other_input_version_uids,
            attestations=input_version.attestations
        )
