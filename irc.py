import socket
import threading

def connect_to_irc_server(server: str, port: int, channel: str, nickname: str):
    """
    Connects to an IRC server, joins a channel, and sends messages from the console.

    Args:
        server (str): The address of the IRC server.
        port (int): The port number to connect to.
        channel (str): The channel to join.
        nickname (str): The nickname to use.

    Returns:
        None
    """
    # Connect to the IRC server
    irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc_socket.connect((server, port))

    # Send user and nickname commands
    irc_socket.send(bytes("USER " + nickname + " 0 * :" + nickname + "\r\n", "UTF-8"))
    irc_socket.send(bytes("NICK " + nickname + "\r\n", "UTF-8"))

    # Join the channel
    irc_socket.send(bytes("JOIN " + channel + "\r\n", "UTF-8"))

    # Start a new thread to handle console input
    threading.Thread(target=handle_console_input, args=(irc_socket, channel)).start()

    # Receive and print server messages
    while True:
        message = irc_socket.recv(2048).decode("UTF-8")
        print(message)

        # Respond to PING messages to keep the connection active
        if message.startswith("PING"):
            irc_socket.send(bytes("PONG " + message.split()[1] + "\r\n", "UTF-8"))

def handle_console_input(irc_socket, target):
    while True:
        message = input()
        handle_privmsg(irc_socket, target, message)

def handle_privmsg(msg):
    full_msg = " ".join(msg)
    # Extrae el remitente del mensaje
    prefix_end = full_msg.find('!')
    sender = full_msg[1:prefix_end]

    # Extrae el texto del mensaje
    # Busca el primer carácter ':' que indica el inicio del mensaje real
    message_start = full_msg.find(':', 1)
    message = full_msg[message_start + 1:]

    # Determina si el mensaje es para un canal o es un mensaje directo
    if msg[2].startswith('#'):
        # Mensaje de canal
        print(f"Mensaje de {sender} en {msg[2]}: {message}")
    else:
        # Mensaje directo
        print(f"Mensaje directo de {sender}: {message}")

def send_message(msg):
        try:
            socket.sendall(f"{msg}\r\n".encode())
        except Exception as e:
            print("Error", e)

def change_nick(sections):
    old = sections[0][1:].split('!')[0]
    new = sections[2].lstrip(':')
    if old == nickname:
        nickname = new  
        print(f"Nuevo nickname: {new}.")
    else:
        print("Los nicks no coinciden")


def receive_messages():
    buffer = ""  
    try:
        info = socket.recv(4096)  # 4096 bytes recibidos

        buffer += info.decode('utf-8', errors='replace')

        while "\r\n" in buffer:
            message, buffer = buffer.split("\r\n", 1)
            sections = message.split(" ")

            if sections[0] == "PING":
                socket.sendall(f"PONG {sections}\r\n".encode())
            elif sections[0].startswith(":") and sections[1] == "NICK":
                change_nick(sections)
            elif sections[1] == "PRIVMSG":
                handle_privmsg(sections)

            print(message)

    except UnicodeDecodeError as e:
        print(f"Error de decodificación en la recepción de mensajes: {e}.")
    except Exception as e:
        print(f"Error al recibir mensaje: {e}.")
       

connect_to_irc_server("irc.freenode.net", 6667, "#freenode", "marians002")