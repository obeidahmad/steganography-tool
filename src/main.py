from encoders_services import least_significant_bit_encode, least_significant_bit_decode
import os

project_path: str = os.path.abspath("")

least_significant_bit_encode(
    cover_path=os.path.join(project_path, "test_files", "clean.png"),
    data=os.path.join(project_path, "test_files", "data.txt"),
    stego_path=os.path.join(project_path, "test_files", "stego.png"),
    file=True
)


least_significant_bit_decode(
    stego_path=os.path.join(project_path, "test_files", "stego.png"),
    result_file_path=os.path.join(project_path, "test_files", "result.txt")
)
