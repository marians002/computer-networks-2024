import socket
import threading


class IRCServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connections = []
        self.channels = {"General": []}
        # AF_INET: significa que la familia de direcciones sporotadas por el socket es IPv4
        # SOCK_STREAM: tipo de socket: TCP. Usa protocolo TCP para transimision de datos
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.bind((self.host, self.port))
        self.socket.listen(5) # Numero maximo de conexiones en cola
        print(f"Servidor IRC iniciado en {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.socket.accept()
            print(f"Nueva conexion desde {client_address}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            # Set the client handler thread to daemon mode
            # This means that the thread will not prevent the program from exiting
            # The thread will automatically terminate when the main program ends
            client_handler.daemon = True
            client_handler.start()

    def handle_client(self, client_socket):
        self.connections.append(client_socket)
        client_socket.sendall("Bienvenido al servidor IRC local\r\n".encode())

        self.channels["General"].append(client_socket)
        client_socket.sendall(f"Te has unido al canal General \r\n".encode())

        while True:

            data = client_socket.recv(4096)
            if not data:
                break
            message = data.decode().strip()
            print(f"Mensaje recibido: {message}")

            # Procesamiento de comandos

            # JOIN
            if message.startswith("JOIN"):
                channel = message.split(" ")[1]
                if channel not in self.channels:
                    self.channels[channel] = []
                self.channels[channel].append(client_socket)
                client_socket.sendall(f"Te has unido al canal {channel}\r\n".encode())
            # PART
            elif message.startswith("PART"):
                channel = message.split(" ")[1]
                self.channels[channel].remove(client_socket)
                client_socket.sendall(f"Has dejado el canal {channel}\r\n".encode())
            # MSG
            elif message.startswith("MSG"):
                parts = message.split(" ", 2)
                if len(parts) >= 3:
                    target = parts[1]
                    msg = parts[2]
                    self.send_msg_or_notice(client_socket, target, msg, False)
                else:
                    client_socket.sendall("Formato incorrecto. Uso: MSG <destino> <mensaje>\r\n".encode())
            # NOTICE
            elif message.startswith("NOTICE"):
                parts = message.split(" ", 2)
                if len(parts) >= 3:
                    target = parts[1]
                    notice = parts[2]
                    self.send_msg_or_notice(client_socket, target, notice, True)
                else:
                    client_socket.sendall("Formato incorrecto. Uso: NOTICE <destino> <mensaje>\r\n".encode())
            # LIST
            elif message.startswith("LIST"):
                self.list_channels(client_socket)
            # NAMES
            elif message.startswith("NAMES"):
                parts = message.split(" ", 1)
                if len(parts) > 1:
                    channel = parts[1]
                    self.list_users_in_channel(client_socket, channel)
                else:
                    self.list_users_in_channel(client_socket, "General")
            # WHOIS
            elif message.startswith("WHOIS"):
                parts = message.split(" ", 1)
                if len(parts) > 1:
                    target = parts[1]
                    self.handle_whois(client_socket, target)
                else:
                    client_socket.sendall("Formato incorrecto. Uso: WHOIS <usuario>\r\n".encode())
            # TOPIC
            elif message.startswith("TOPIC"):
                parts = message.split(" ", 1)
                if len(parts) > 1:
                    channel = parts[1]
                    client_socket.sendall(f"El topic del canal {channel} es: {self.channels[channel]}\r\n".encode())
                else:
                    client_socket.sendall("Formato incorrecto. Uso: TOPIC <canal>\r\n".encode())
            else:
                self.send_msg_or_notice(client_socket, "General", message, False)

        client_socket.close()
        self.connections.remove(client_socket)
        print("Cliente desconectado")

    def send_msg_or_notice(self, sender_socket, target, message_notice, msg_ntc: bool):
        for channel in self.channels:
            if target == channel:
                for client_socket in self.channels[channel]:
                    if client_socket != sender_socket:
                        if msg_ntc:
                            client_socket.sendall(
                                f"Notificacion de {sender_socket.getpeername()}: {message_notice}\r\n".encode())
                        else:
                            client_socket.sendall(
                                f"Mensaje de {sender_socket.getpeername()}: {message_notice}\r\n".encode())
                break
        else:
            sender_socket.sendall(f"No se encontro el canal {target}\r\n".encode())

    def list_channels(self, client_socket):
        client_socket.sendall("Lista de canales:\r\n".encode())
        for channel in self.channels:
            client_socket.sendall(f"- {channel}\r\n".encode())

    def list_users_in_channel(self, client_socket, channel):
        for ch, users in self.channels.items():
            if ch == channel:
                client_socket.sendall(f"Usuarios en el canal {channel}:\r\n".encode())
                for user_socket in users:
                    client_socket.sendall(f"- {user_socket.getpeername()}\r\n".encode())
                break
        else:
            client_socket.sendall(f"No se encontro el canal {channel}\r\n".encode())

    def handle_whois(self, client_socket, target):
        for channel in self.channels:
            for user_socket in self.channels[channel]:
                if user_socket.getpeername() == target:
                    client_socket.sendall(f"Usuario {target} en el canal {channel}\r\n".encode())
                    break
            else:
                continue
            break
        else:
            client_socket.sendall(f"Usuario {target} no encontrado\r\n".encode())

def main():
    host = input("Ingrese la direccion del host: ")
    port = int(input("Ingrese la direccion del puerto: "))
    IRCServer(host, port)


main()
