from enum import IntEnum

class FileResponseError(Exception):
    def  __init__(self, message : str):
        super().__init__(message)

class FileResponseStatus(IntEnum):
    FAIL = 0,
    SUCCESS = 1

class FileResponse:
    # Fixed Header Size
    FIXED_HEADER_SIZE = 8
    # Fixed Header Static Contents
    MAGIC_NO = 0x497E
    TYPE = 2

    def __init__(self, status_code : FileResponseStatus, file_data : bytearray = None):
        self.fixed_header = bytearray(FileResponse.FIXED_HEADER_SIZE)
        self.status_code = status_code
        self.data_length = len(file_data)
        self.file_data = file_data

    def create_record(self) -> bytearray:
        # Magic Number
        self.fixed_header[0] = (FileResponse.MAGIC_NO & 0xFF00) >> 8
        self.fixed_header[1] = (FileResponse.MAGIC_NO & 0x00FF)
        # Type
        self.fixed_header[2] = FileResponse.TYPE
        # Status Code
        self.fixed_header[3] = self.status_code
        # Data Length
        if (self.status_code == FileResponseStatus.SUCCESS):
            self.fixed_header[4] = (self.data_length & 0xFF000000) >> 24
            self.fixed_header[5] = (self.data_length & 0x00FF0000) >> 16
            self.fixed_header[6] = (self.data_length & 0x0000FF00) >> 8
            self.fixed_header[7] = (self.data_length & 0x000000FF)

            record = self.fixed_header + self.file_data
        else:
            record = self.fixed_header

        return record
    
    @staticmethod
    def get_magic_number(file_response_header_byte_array : bytearray) -> int:
        return int.from_bytes(file_response_header_byte_array[0 : 2], "big")

    @staticmethod
    def get_type(file_response_header_byte_array : bytearray) -> int:
        return int.from_bytes(file_response_header_byte_array[2 : 3], "big")

    @staticmethod
    def get_status_code(file_response_header_byte_array : bytearray) -> int:
        return int.from_bytes(file_response_header_byte_array[3 : 4], "big")

    @staticmethod
    def get_file_length(file_response_header_byte_array : bytearray) -> int:
        return int.from_bytes(file_response_header_byte_array[4 : 8], "big")

    @staticmethod
    def check_record_validity(file_response_header_byte_array : bytearray):
        # Check the magic number
        magic_number = FileResponse.get_magic_number(file_response_header_byte_array)
        if (magic_number != FileResponse.MAGIC_NO):
            raise FileResponseError(f"FILE REQUEST ERROR: The magic number is wrong ({magic_number} != {FileResponse.MAGIC_NO}).")

        # Check the type
        type_number = FileResponse.get_type(file_response_header_byte_array)
        if (type_number != FileResponse.TYPE):
            raise FileResponseError(f"FILE REQUEST ERROR: The type is wrong ({type_number} != {FileResponse.TYPE}).")
