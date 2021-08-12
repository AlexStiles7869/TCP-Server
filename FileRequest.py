class FileRequest:
    # Fixed Header Size
    FIXED_HEADER_SIZE = 5
    # Fixed Header Static Contents
    MAGIC_NO = 0x497E
    TYPE = 1
    MAX_FILENAME_LENGTH = 1024

    def __init__(self, filename : str):
        self.fixed_header = bytearray(FileRequest.FIXED_HEADER_SIZE)
        self.filename = filename.encode("utf-8")
        self.filename_length = len(self.filename)

        if (self.filename_length > FileRequest.MAX_FILENAME_LENGTH):
            raise FileRequestIllegalFileNameLength(self.filename_length)

    def create_record(self) -> bytearray:
        # Magic Number
        self.fixed_header[0] = (FileRequest.MAGIC_NO & 0xFF00) >> 8
        self.fixed_header[1] = (FileRequest.MAGIC_NO & 0x00FF)
        # Type
        self.fixed_header[2] = FileRequest.TYPE
        # Filename Length
        self.fixed_header[3] = (self.filename_length & 0xFF00) >> 8
        self.fixed_header[4] = (self.filename_length & 0x00FF)

        return self.fixed_header + self.filename

    @staticmethod
    def check_record_validity(file_request_header_byte_array : bytearray):
        # Check the magic number
        magic_number = int.from_bytes(file_request_header_byte_array[0 : 2], "big")
        if (magic_number != FileRequest.MAGIC_NO):
            raise FileRequestIllegalMagicNumber(magic_number)

        # Check the type
        type_number = int.from_bytes(file_request_header_byte_array[2 : 3], "big")
        if (type_number != FileRequest.TYPE):
            raise FileRequestIllegalType(type_number)
        
        # Check the file name length
        filename_length = int.from_bytes(file_request_header_byte_array[3 : 5], "big")
        if (filename_length > FileRequest.MAX_FILENAME_LENGTH):
            raise FileRequestIllegalFileNameLength(filename_length)
    
    @staticmethod
    def get_magic_number(file_response_header_byte_array : bytearray) -> int:
        return int.from_bytes(file_response_header_byte_array[0 : 2], "big")

    @staticmethod
    def get_type(file_response_header_byte_array : bytearray) -> int:
        return int.from_bytes(file_response_header_byte_array[2 : 3], "big")

    @staticmethod
    def get_filename_length(file_request_header_byte_array : bytearray):
        return int.from_bytes(file_request_header_byte_array[3 : 5], "big")

class FileRequestIllegalMagicNumber(Exception):
    def  __init__(self, magic_number : int, message = f"The magic number of the FileRequest is incorrect, it must be {FileRequest.MAGIC_NO}"):
        self.magic_number = magic_number
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"FileRequest Magic Number: {self.magic_number} -> {self.message}"

class FileRequestIllegalType(Exception):
    def  __init__(self, type_number : int, message = f"The type of the FileRequest is incorrect, it must be {FileRequest.TYPE}"):
        self.type_number = type_number
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"FileRequest Type: {self.type_number} -> {self.message}"

class FileRequestIllegalFileNameLength(Exception):
    def  __init__(self, filename_length : int, message = f"The filename of the FileRequest has a length in bytes that is larger than the maximum allowed, {FileRequest.MAX_FILENAME_LENGTH} bytes"):
        self.filename_length = filename_length
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"FileRequest Filename Size: {self.filename_length} bytes -> {self.message}"