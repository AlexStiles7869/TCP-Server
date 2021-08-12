from typing import Tuple
from FileRequest import FileRequest, FileRequestIllegalMagicNumber, FileRequestIllegalType, FileRequestIllegalFileNameLength
from FileResponse import FileResponse, FileResponseStatus
import argparse
import socket
import sys
import time

class Server:

    BACKLOG_SIZE = 5
    ALLOWED_PORT_RANGE = (1024, 64000)

    def __init__(self, port : int):
        if (port < Server.ALLOWED_PORT_RANGE[0] or port > Server.ALLOWED_PORT_RANGE[1]):
            print("The port number provided is not in the allowed range of 1024 to 64000 (inclusive).")
            sys.exit()
        
        self.port = port
        
        print("---SERVER SETUP---\n")

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("SERVER SOCKET CREATION SUCCESSFUL")
        except socket.error as error:
            print(f"SERVER SOCKET CREATION UNSUCCESSFUL: {error}")
            sys.exit()

        self.socket.bind(("localhost", self.port))

    @staticmethod
    def get_time() -> str:
        server_time = time.localtime()
        current_time = time.strftime("%Y/%m/%d %H:%M:%S", server_time)
        return current_time

    def listen(self):
        try:
            self.socket.listen(Server.BACKLOG_SIZE)
            print("SOCKET IS LISTENING")
        except socket.error as err:
            print(f"OPENING SOCKET FAILED: {err}")
            sys.exit()

        while True:
            # Allow client socket to connect (blocking in thread)
            client_socket, addr = self.socket.accept()

            # Get the current time
            current_time = Server.get_time()

            # Print connection summary to terminal
            print(f"CONNECTION ACCEPTED (Server Confirmation) | Time: {current_time} | IP: {addr[0]} | Port: {addr[1]}")

            try:
                print("\n---ATTEMPTING TO RECEIVE FILE REQUEST---\n")
                # FILE REQUEST RECEIVING / HANDLING
                
                # Get the filename length -> throws exception if FileRequest is invalid or the socket timesout
                filename_length = Server.receive_file_request_header(client_socket)
                # Get the file data -> throws an exception if an incorrect amount of data is received or the socket timesout
                filename = Server.receive_file_request_data(client_socket, filename_length)

                print("\n---ATTEMPTING TO SEND FILE RESPONSE---\n")
                # FILE RESPONSE CREATION / SENDING

                # Create the appropriate file response record
                file_response_record = Server.create_file_response(filename)

                # Send the record
                Server.send_file_response(client_socket, file_response_record)

            except (FileRequestIllegalMagicNumber, FileRequestIllegalType, FileRequestIllegalFileNameLength) as error:
                print(error)
                sys.exit()
            finally:
                # Close the socket
                client_socket.close()
                # Get the current time
                current_time = Server.get_time()
                print("\n---ENDING COMMUNICATION---\n")
                print(f"CONNECTION TERMINATED (Server Confirmation) | Time : {current_time} | IP: {addr[0]} | Port: {addr[1]}")

    """ File Request Receiving / Handling """

    """ Receives the file request from the client. """
    @staticmethod
    def receive_file_request_header(client_socket : socket.socket) -> int:
        received_header_bytes = 0
        received_header_bytes_array = bytearray()

        while received_header_bytes < FileRequest.FIXED_HEADER_SIZE:
            received_bytes = client_socket.recv(FileRequest.FIXED_HEADER_SIZE)
            received_header_bytes_array += received_bytes
            received_header_bytes += len(received_bytes)

        # Check that the FileRequest header is valid -> throws exception
        FileRequest.check_record_validity(received_header_bytes_array)

        filename_length = FileRequest.get_filename_length(received_header_bytes_array)

        print(f"FILE REQUEST HEADER RECEIVED | Bytes: {received_header_bytes} | Magic Number: {FileRequest.get_magic_number(received_header_bytes_array)} | Type: {FileRequest.get_type(received_header_bytes_array)} | Filename Length: {FileRequest.get_filename_length(received_header_bytes_array)}")

        return filename_length
        
    @staticmethod
    def receive_file_request_data(client_socket : socket.socket, filename_length : int) -> str:
        received_data_bytes = 0
        received_data_bytes_array = bytearray()

        while (received_data_bytes < filename_length):
            received_bytes = client_socket.recv(filename_length)
            received_data_bytes_array += received_bytes
            received_data_bytes += len(received_bytes)

        filename = received_data_bytes_array.decode("utf-8")
        
        print(f"FILE REQUEST DATA RECEIVED | Bytes: {received_data_bytes} | Filename: {filename}")

        return filename

    """ File Response Creation / Handling """
    
    @staticmethod
    def get_file_data(filename : str) -> tuple([FileResponseStatus, bytearray]):
        try:
            with open(filename, "rb") as file:
                file_data = bytearray(file.read())
                status_code = FileResponseStatus.SUCCESS
                print(f"FILE DATA READ | Bytes: {len(file_data)}")
        except IOError:
            status_code = FileResponseStatus.FAIL
            file_data = bytearray()

        return status_code, file_data

    @staticmethod
    def create_file_response(filename : str) -> bytearray:

        status_code, file_data = Server.get_file_data(filename)

        file_response = FileResponse(status_code, file_data)
        file_response_record = file_response.create_record()

        return file_response_record

    @staticmethod
    def send_file_response(client_socket : socket.socket, file_response_record : bytearray):
        sent_file_repsonse_bytes = 0

        while sent_file_repsonse_bytes < len(file_response_record):
            sent_file_repsonse_bytes += client_socket.send(file_response_record[sent_file_repsonse_bytes:])

        print(f"FILE RESPONSE SENT | Bytes: {len(file_response_record)}")

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("port", metavar="P", type=int, nargs=1, help="Port number for server\n")

    # Initialise server class
    server = Server(12345)
    server.listen()

if __name__ == "__main__":
    main()