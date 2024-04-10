import socket
import threading

def connect_to_irc_server(server: str, port: int, channel: str, nickname: str):
    
    # Conectarse al servidor IRC
    irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc_socket.connect((server, port))

    # Enviar comandos de usuario y nickname
    irc_socket.send(bytes("USER " + nickname + " 0 * :" + nickname + "\r\n", "UTF-8"))
    irc_socket.send(bytes("NICK " + nickname + "\r\n", "UTF-8"))

    # Unirse al canal
    irc_socket.send(bytes("JOIN " + channel + "\r\n", "UTF-8"))

    # Iniciar un nuevo hilo para manejar la entrada de la consola
    threading.Thread(target=handle_input, args=(irc_socket, channel)).start()

    # Recibir e imprimir mensajes del servidor
    while True:
        message = irc_socket.recv(4096).decode("UTF-8")
        print(message)

        # Responder a los mensajes PING para mantener la conexión activa
        if message.startswith("PING"):
            irc_socket.send(bytes("PONG " + message.split()[1] + "\r\n", "UTF-8"))

def send_message(msg):
        try:
            socket.sendall(f"{msg}\r\n".encode())
        except Exception as e:
            print("Error", e)

def rcv_messages():
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
            elif sections[1] in ["311", "319", "322", "323","324", "353", "366", "431", "432", "433"]:
                num_handler(sections)
            elif sections[1] == "JOIN":
                join_channel(sections)
            elif sections[1] == "PART":
                leave_channel(sections)

            print(message)

    except UnicodeDecodeError as e:
        print(f"Error de decodificación en la recepción de mensajes: {e}.")
    except Exception as e:
        print(f"Error al recibir mensaje: {e}.")
       
def change_nick(sections):
    old = sections[0][1:].split('!')[0]
    new = sections[2].lstrip(':')
    if old == new:
        nickname = new  
        print(f"Nuevo nickname: {new}.")
    else:
        print("Los nicks no coinciden")

def handle_input(irc_socket, target):
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

def num_handler(sections):
    code = sections[1]

    # Código 311: WHOIS - otorga información del usuario
    if code == "311":
        nickname = sections[3]
        username = sections[4]
        hostname = sections[5]
        realname = ' '.join(sections[7:])[1:]
        print(f"El usuario {nickname} ({realname}) está en: {hostname}")
    
    # Código 319: Muestra los canales a los que pertenece el usuario
    elif code == "319":
        nickname = sections[3]
        channels = ' '.join(sections[4:])[1:]
        print(f"{nickname} pertenece a los canales: {channels}")
    
    # Código 322: LIST
    elif code == "322":
        channel = sections[3]
        user_count = sections[4]
        topic = ' '.join(sections[5:])[1:]
        print(f"Canal: {channel}. Cantidad de usuarios: {user_count}. Tema: {topic}")
    
    # Código 323: Fin de la lista LIST
    elif code == "323":
        print("Fin de la lista de canales.")
    
    # Código 324: Respuesta de modo de canal
    elif code == "324":
        channel = sections[3]
        modes = ' '.join(sections[4:])
        print(f"Modos actuales para {channel}: {modes}")
    
    # Código 353: Respuesta a NAMES
    elif code == "353":
        channel = sections[4]
        names = ' '.join(sections[5:])[1:]
        print(f"Usuarios en {channel}: {names}")
    
    # Código 366: Fin de la lista NAMES
    elif code == "366":
        channel = sections[3]
        print(f"Fin de la lista de usuarios en {channel}.")
    
    # Código 431: Sin nickname dado
    elif code == "431":
        print("No se ha proporcionado un nickname.")
    
    # Código 432: Nickname erróneo
    elif code == "432":
        print("El nickname es inválido.")
    
    # Código 433: Nickname en uso/inválido
    elif code == "433":
        print("El nickname deseado está en uso o es inválido.")
        
def join_channel(sections):
        user_info = sections[0][1:]
        channel = sections[2].strip() if sections[2].startswith(':') else sections[2]
        print(f"El usuario {user_info} se ha unido al canal {channel}")

def leave_channel(sections):
    user_info = sections[0][1:]
    channel = sections[2].strip() if sections[2].startswith(':') else parts[2]
    print(f"El usuario {user_info} ha salido del canal {channel}")

connect_to_irc_server("irc.freenode.net", 6667, "#freenode", "marians002")