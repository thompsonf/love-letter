import socket

HOST_dflt = "199.87.127.48"
PORT_dflt = 8888

HOST = input("Connect to which IP? (leave empty for default): ")
PORT = input("Connect to which port? (leave empty for default): ")

if not HOST:
    HOST = HOST_dflt
if PORT:
    PORT = int(PORT)
else:
    PORT = PORT_dflt

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("Connected to", HOST, "on port", PORT)

while True:
    msgstr = s.recv(1024).decode()
    if msgstr == "":
        print("Disconnected from server")
        exit()
    print(msgstr)
    msglist = msgstr.split()
    #process the msg
    x = msglist[-1].lower()
    if(x == "name:" or
       x == "players?" or
       x == "4:" or
       x == "play?" or
       x == "hands?" or
       x == "card." or
       x == "with?" or
       x == "at?" or
       x == "guess?"):
        reply = input()
        s.send(reply.encode())