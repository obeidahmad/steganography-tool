from encoders_decoders.least_significant_bit import EncodeType
from encoders_decoders_services import least_significant_bit_encode, least_significant_bit_decode
import os

project_path: str = os.path.abspath("")

least_significant_bit_encode(
    cover_path=os.path.join(project_path, "test_files", "clean.png"),
    data=os.path.join(project_path, "test_files", "data.txt"),
    stego_path=os.path.join(project_path, "test_files", "stego.png"),
    file=True,
    encode_type=EncodeType.EQUI_DISTRIBUTION,
)


least_significant_bit_decode(
    stego_path=os.path.join(project_path, "test_files", "stego.png"),
    encode_type=EncodeType.EQUI_DISTRIBUTION,
    result_file_path=os.path.join(project_path, "test_files", "result.txt"),
)
