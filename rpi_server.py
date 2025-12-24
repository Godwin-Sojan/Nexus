import socket
import subprocess
import threading

# Configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000

def handle_client(client_socket, addr):
    print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
    
    try:
        while True:
            # Receive data
            request = client_socket.recv(1024).decode('utf-8')
            
            if not request:
                break
                
            print(f"[*] Received: {request}")
            
            # Check for greetings
            greetings = ["hi", "hello", "hey", "greetings", "hola"]
            if request.lower().strip() in greetings:
                response = "Greetings! How can I help you today?"
                client_socket.send(response.encode('utf-8'))
                continue
            
            # Check for help
            if request.lower().strip() == "help":
                response = "Available commands: help, <shell commands>\nType any shell command to execute it."
                client_socket.send(response.encode('utf-8'))
                continue

            # Execute command
            try:
                # Run command and capture output
                # shell=True allows using pipes and shell features, but be careful with security
                output = subprocess.check_output(request, shell=True, stderr=subprocess.STDOUT)
                response = output.decode('utf-8')
            except subprocess.CalledProcessError as e:
                # If the command was not found or failed
                response = "unable to fetch command, please type help for instructions"
            except Exception as e:
                response = f"Error executing command: {str(e)}"
            
            # Send response back
            if not response:
                response = "(Command executed with no output)"
                
            client_socket.send(response.encode('utf-8'))
            
    except Exception as e:
        print(f"[!] Error handling client: {e}")
    finally:
        print(f"[*] Closing connection from {addr[0]}:{addr[1]}")
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Listening on {HOST}:{PORT}")
    
    try:
        while True:
            client, addr = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client, addr))
            client_handler.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down server")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
