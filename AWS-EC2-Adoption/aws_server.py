# Import required modules
import socket
import _thread
import threading
import hashlib
import json
import sys


# Enable locking for a thread
print_lock = threading.Lock()

####################################################################
#################### Configuración de opciones #####################
####################################################################

def option_check():
    global args

    # Argumentos recibidos
    avail_options = ["-id", "-pp", "-listen", "-revproc"]

    #Recibe opciones y argumentos dados por el cliente
    options = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    #Error en caso de que las opciones no sean válidos
    for i in options:
        if i not in avail_options:
            raise SystemExit(f"Usage: {sys.argv[0]} (-id & -pp & -listen & -revproc) <argument>...")

    #Error en caso de que no todas las opciones o argumentos sean válidos
    if len(options) != 4 or len(args) != 4:
        raise SystemExit(f"Usage: {sys.argv[0]} (-id & -pp & -listen & -revproc) <argument>...")


####################################################################
######################## Funciones básicas #########################
####################################################################

# Establecer nueva conexión con proxy
# Después de recibir la petición del proxy
def on_new_client(clientsocket,addr):
    while True:
        #Petición recibida
        msg = clientsocket.recv(2048)
        #Evaluamos que la petición no esté vacía
        if not msg:
            # lock released on exit
            print_lock.release()
            break
        #La petición tiene formato JSON
        json_msg = json.loads(msg.decode())
        print("Received a message from client", json_msg["srcid"], "payload", json_msg["payload"])
        payload = json_msg["payload"]
        new_msg = hashlib.sha1()
        new_msg.update(payload.encode())
        hashed_payload = new_msg.hexdigest()
        #Creamos y envíamos nuevo JSON con información del servidor y la response que se entregará al cliente
        new_json_msg = {"type":"2", "srcid": str(args[0]), "destid": json_msg["srcid"],\
                        "payloadsize": len(hashed_payload), "payload": hashed_payload, "response": "Hola monda"}        
        print("Sending a message to the client", new_json_msg["destid"], "payload", new_json_msg["payload"], "response", new_json_msg["response"])
        clientsocket.send(json.dumps(new_json_msg).encode())
    #Cerramos conexión con proxy
    clientsocket.close()


# Abrir conexión con el proxy
def connect_reverse_proxy():
    new_json_msg = {"type":"1", "id": str(args[0]), "privPolyId": str(args[1]),\
                        "listenport": str(args[2])}
    rev_proxy_name = '172.31.21.133' # ip de la instancia donde corre el proxy
    #El puerto se recibe como argumento
    rev_proxy_port = int(args[3])

    #Establecemos la conexión
    rev_proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rev_proxy_socket.connect((rev_proxy_name, rev_proxy_port))
    #Enviamos JSON al proxy con toda la información del servidor
    rev_proxy_socket.send(json.dumps(new_json_msg).encode())
    #Cerramos conexión con proxy
    rev_proxy_socket.close()



####################################################################
########################## Main Function ###########################
####################################################################

if __name__ == "__main__":
    option_check()
    s = socket.socket()         # Create a socket object
    host = '172.31.21.234'      # Get local machine name
    port = int(args[2])              # Reserve a port for your service.


    print ("Server running with id", args[0])
    print ("Server serving privacy policy", args[1])
    print ("Listening on port", args[2])
    
    # Broadcast "Alive" status to the Reverse Proxy first
    connect_reverse_proxy()
    print ("Connecting to the reverse proxy on port", args[3])

    # Binds to the port
    s.bind((host, port))     
    # Allow 10 clients to connect
    s.listen(10)                 

    # Receive/Process each client connection in a seperate thread
    while True:
        c, addr = s.accept()     # Establish connection with client.
        # lock acquired by client
        print_lock.acquire()
        print ('Received a message from client', addr, "payload")
        _thread.start_new_thread(on_new_client,(c,addr))
        
    s.close()