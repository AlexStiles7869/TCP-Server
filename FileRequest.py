class FileRequestError(Exception):
    def  __init__(self, message : str):
        super().__init__(message)

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
            raise FileRequestError(f"FILE REQUEST ERROR: The file name length is larger than the maximum allowed ({self.filename_length} bytes > {FileRequest.MAX_FILENAME_LENGTH} bytes).")

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
            raise FileRequestError(f"FILE REQUEST ERROR: The magic number is wrong ({magic_number} != {FileRequest.MAGIC_NO}).")

        # Check the type
        type_number = int.from_bytes(file_request_header_byte_array[2 : 3], "big")
        if (type_number != FileRequest.TYPE):
            raise FileRequestError(f"FILE REQUEST ERROR: The type is wrong ({type_number} != {FileRequest.TYPE}).")
        
        # Check the file name length
        filename_length = int.from_bytes(file_request_header_byte_array[3 : 5], "big")
        if (filename_length > FileRequest.MAX_FILENAME_LENGTH):
            raise FileRequestError(f"FILE REQUEST ERROR: The file name length is larger than the maximum allowed ({filename_length} bytes > {FileRequest.MAX_FILENAME_LENGTH} bytes).")
    
    @staticmethod
    def get_magic_number(file_response_header_byte_array : bytearray) -> int:
        return int.from_bytes(file_response_header_byte_array[0 : 2], "big")

    @staticmethod
    def get_type(file_response_header_byte_array : bytearray) -> int:
        return int.from_bytes(file_response_header_byte_array[2 : 3], "big")

    @staticmethod
    def get_filename_length(file_request_header_byte_array : bytearray):
        return int.from_bytes(file_request_header_byte_array[3 : 5], "big")