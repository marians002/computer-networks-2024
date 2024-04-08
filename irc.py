import socket

def connect_to_irc_server(server: str, port: int, channel: str, nickname: str):

    # Conectarse al servidor IRC
    irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc_socket.connect((server, port))

    # Enviar comandos de usuario y apodo
    irc_socket.send(bytes("USER " + nickname + " 0 * :" + nickname + "\r\n", "UTF-8"))
    irc_socket.send(bytes("NICK " + nickname + "\r\n", "UTF-8"))

    # Unirse al canal
    irc_socket.send(bytes("JOIN " + channel + "\r\n", "UTF-8"))

    # Recibir e imprimir los mensajes del servidor
    while True:
        message = irc_socket.recv(2048).decode("UTF-8")
        print(message)

        # Responder a los mensajes PING para mantener la conexión activa
        if message.startswith("PING"):
            irc_socket.send(bytes("PONG " + message.split()[1] + "\r\n", "UTF-8"))


def handle_privmsg(irc_socket, target, message):
    # Enviar el comando PRIVMSG con el destinatario y el mensaje, seguido de un retorno de carro y nueva línea
    irc_socket.send(bytes("PRIVMSG " + target + " :" + message + "\r\n", "UTF-8"))
