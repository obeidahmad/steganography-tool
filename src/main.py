from encoders_services import least_significant_bit_encode, least_significant_bit_decode

least_significant_bit_encode(
    cover_path="image cover path",
    data="data path or message as string",
    stego_path="image stego path",
    file=True
)


least_significant_bit_decode(
    stego_path="image stego path",
    result_file_path="result path if file"
)
