import socket
import threading
import os
import ssl
import hashlib

# Define constants
HOST = 'localhost'
PORT = 5001
ADMIN_PASSWORD_HASH = hashlib.sha256("admin".encode()).hexdigest()  # Hash the password
UPLOAD_DIR = "uploaded_files"  # Directory for uploaded files

# Create the upload directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def handle_client(client_socket):
    while True:
        try:
            command = client_socket.recv(1024)
            if not command:
                break

            try:
                command = command.decode('utf-8')
            except UnicodeDecodeError:
                client_socket.send(b'ERROR: Invalid command received')
                continue

            parts = command.split()
            action = parts[0].lower()

            if action == 'upload':
                # Extract the filename and filesize
                filename = os.path.join(UPLOAD_DIR, parts[1])  # Save to the upload directory
                filesize = int(parts[2])
                received_bytes = 0

                # Open the file for writing
                with open(filename, 'wb') as f:
                    while received_bytes < filesize:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        f.write(data)
                        received_bytes += len(data)

                # Wait for EOF signal
                eof_signal = client_socket.recv(1024)
                if eof_signal == b'EOF':
                    client_socket.send(b'ACK: Upload complete')

            elif action == 'download':
                filename = os.path.join(UPLOAD_DIR, parts[1])
                if os.path.exists(filename):
                    client_socket.send(b'EXISTS ' + str(os.path.getsize(filename)).encode())
                    with open(filename, 'rb') as f:
                        data = f.read(1024)
                        while data:
                            client_socket.send(data)
                            data = f.read(1024)
                else:
                    client_socket.send(b'NOT EXISTS')

            elif action == 'delete':
                if len(parts) > 2 and hashlib.sha256(parts[1].encode()).hexdigest() == ADMIN_PASSWORD_HASH:
                    filename = os.path.join(UPLOAD_DIR, parts[2])
                    if os.path.exists(filename):
                        os.remove(filename)
                        client_socket.send(b'Delete complete')
                    else:
                        client_socket.send(b'File does not exist')
                else:
                    client_socket.send(b'Permission denied')

            elif action == 'list':
                files = os.listdir(UPLOAD_DIR)
                file_list = '\n'.join(files) if files else 'No files available.'
                client_socket.send(file_list.encode())

            else:
                client_socket.send(b'Invalid command')

        except Exception as e:
            client_socket.send(f'ERROR: {str(e)}'.encode())
            break

    client_socket.close()

def start_server():
    # Create the socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f'Server listening on {HOST}:{PORT}')

    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='/home/reuben/cert.pem', keyfile='/home/reuben/key.pem')

    # Load the self-signed certificate to allow client authentication
    context.load_verify_locations(cafile='/home/reuben/cert.pem')
    context.verify_mode = ssl.CERT_OPTIONAL  # Change to CERT_REQUIRED to enforce client cert verification

    while True:
        client_socket, addr = server.accept()
        print(f'Accepted connection from {addr}')
        
        # Wrap the accepted socket with SSL
        secure_socket = context.wrap_socket(client_socket, server_side=True)
        
        client_handler = threading.Thread(target=handle_client, args=(secure_socket,))
        client_handler.start()

if __name__ == '__main__':
    start_server()
