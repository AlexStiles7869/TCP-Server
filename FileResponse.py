from enum import IntEnum

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
            raise FileResponseIllegalMagicNumber(magic_number)

        # Check the type
        type_number = FileResponse.get_type(file_response_header_byte_array)
        if (type_number != FileResponse.TYPE):
            raise FileResponseIllegalType(type_number)

class FileResponseIllegalMagicNumber(Exception):
    def  __init__(self, magic_number : int, message = f"The magic number of the FileResponse is incorrect, it must be {FileResponse.MAGIC_NO}"):
        self.magic_number = magic_number
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"FileReponse Magic Number: {self.magic_number} -> {self.message}"

class FileResponseIllegalType(Exception):
    def  __init__(self, type_number : int, message = f"The type of the FileResponse is incorrect, it must be {FileResponse.TYPE}"):
        self.type_number = type_number
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"FileResponse Type: {self.type_number} -> {self.message}"