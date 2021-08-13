import argparse
import socket
from FileRequest import FileRequest
from FileResponse import FileResponse, FileResponseError, FileResponseStatus
import os
import sys
import time

class FileNameConflictException(Exception):
    def  __init__(self, filename : int, message = f"The file already exists. Please delete / move it and restart the client."):
        self.filename = filename
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Filename: {self.filename} -> {self.message}"

class Client:
    def __init__(self, ip : str, port : int):
        self.ip = socket.gethostbyname(ip)
        self.port = port

        print("---CLIENT SETUP---\n")

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("CLIENT SOCKET CREATION SUCCESSFUL")
        except socket.error as error:
            print(f"CLIENT SOCKET CREATION UNSUCCESSFUL: {error}")
    
    @staticmethod
    def get_time() -> str:
        client_time = time.localtime()
        current_time = time.strftime("%Y/%m/%d %H:%M:%S", client_time)
        return current_time

    def establish_connection(self):
        # Attempt to connect to the server
        try:
            self.socket.connect((self.ip, self.port))
            print(f"CONNECTION ACCEPTED (Client Confirmation) | Time: {Client.get_time()} | IP: {self.ip} | Port: {self.port}")
        except socket.error as err:
            raise SystemExit(f"CONNECTION FAILED: {err}")

    @staticmethod
    def create_file_request(filename : str) -> bytearray:
        file_request = FileRequest(filename)
        file_request_record = file_request.create_record()

        return file_request_record

    # Send the FileRequest to the server
    def send_file_request(self, filename : str, destination_file_name : str):

        try:
            if (os.path.isfile(destination_file_name)):
                raise FileNameConflictException(destination_file_name)
        except FileNameConflictException as error:
            raise SystemExit(error)

        self.establish_connection()

        print("\n---ATTEMPTING TO SEND FILE REQUEST---\n")

        file_request_record = self.create_file_request(filename)

        sent_file_request_bytes = 0

        while (sent_file_request_bytes < len(file_request_record)):
            sent_file_request_bytes += self.socket.send(file_request_record[sent_file_request_bytes:])

        print(f"FILE REQUEST SENT | Bytes: {len(file_request_record)}")

        self.handle_file_response(filename, destination_file_name)

        self.end_connection()

    def receive_file_response_header(self) -> bytearray:
        print("\n---ATTEMPTING TO RECEIVE FILE RESPONSE---\n")
        
        received_header_bytes = 0
        received_header_bytes_array = bytearray() 

        while received_header_bytes < FileResponse.FIXED_HEADER_SIZE:
            received_bytes = self.socket.recv(FileResponse.FIXED_HEADER_SIZE)
            received_header_bytes_array += received_bytes
            received_header_bytes += len(received_bytes)

        print(f"FILE RESPONSE HEADER RECEIVED | Bytes: {received_header_bytes} | Magic Number: {FileResponse.get_magic_number(received_header_bytes_array)} | Type: {FileResponse.get_type(received_header_bytes_array)} | Status Code: {FileResponse.get_status_code(received_header_bytes_array)} | Data Length: {FileResponse.get_file_length(received_header_bytes_array)}")

        return received_header_bytes_array

    def receive_file_response_data(self, file_data_length : int) -> bytearray:
        # Get the file data from the server
        received_data_bytes = 0
        receieved_data_bytes_array = bytearray()

        while received_data_bytes < file_data_length:
            received_bytes = self.socket.recv(file_data_length)
            receieved_data_bytes_array += received_bytes
            received_data_bytes += len(received_bytes)

        print(f"FILE RESPONSE DATA RECEIVED | Bytes: {received_data_bytes}")

        return receieved_data_bytes_array

    def handle_file_response(self, filename : str, destination_file_name : str):

        file_response_header = self.receive_file_response_header()

        try:
            FileResponse.check_record_validity(file_response_header)

            if (FileResponse.get_status_code(file_response_header) == FileResponseStatus.SUCCESS):
                # Get the file data length
                file_data_length = FileResponse.get_file_length(file_response_header)

                # Receive the file response data
                file_response_data = self.receive_file_response_data(file_data_length)

                # Write the data to the specified file
                self.write_response_to_file(file_response_data, destination_file_name)

            else:
                print(f"SERVER CANNOT FILE: The file '{filename}' cannot be found.")
        except FileResponseError as error:
            print(error)

    def write_response_to_file(self, file_response_data : bytearray, destination_file_name : str):
        with open(destination_file_name, "w") as file:
            file.write(file_response_data.decode("utf-8"))
            print(f"FILE DATA WRITTEN | Bytes: {len(file_response_data)} | Destination Filename: {destination_file_name}")

    def end_connection(self):
        print("\n---ENDING COMMUNICATION---\n")
        print(f"CONNECTION TERMINATED (Client Confirmation) | Time: {Client.get_time()} | IP: {self.ip} | Port: {self.port}")
        self.socket.close()

def main():
    os.chdir(os.path.dirname(sys.argv[0]))

    # Setup argument parser
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("port", metavar="P", type=int, nargs=1, help="Port number for client")

    # Initialise client class

    ip = "localhost"
    port = 12345
    file_name = "client.txt"
    destination_file_name = "server.txt"

    client = Client(ip, port)
    client.send_file_request(file_name, destination_file_name)

if __name__ == "__main__":
    main()