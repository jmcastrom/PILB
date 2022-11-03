# Import required modules
import socket
import _thread
import threading
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
    avail_options = ["-id", "-listen"]

    #Recibe opciones y argumentos dados por el cliente
    options = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    #Error en caso de que las opciones no sean válidos
    for i in options:
        if i not in avail_options:
            raise SystemExit(f"Usage: {sys.argv[0]} (-id & -listen) <argument>...")

    #Error en caso de que no todas las opciones o argumentos sean válidos
    if len(options) != 2 or len(args) != 2:
        raise SystemExit(f"Usage: {sys.argv[0]} (-id & -listen) <argument>...")


####################################################################
######################## Funciones básicas #########################
####################################################################

# Establecer nueva conexión con proxy
# Después de recibir la petición del proxy
def on_new_client(clientsocket,addr):
    while True:
        #Petición recibida
        msg = clientsocket.recv(2048).decode()
        #Obtener datos del cliente (ip y puerto)
        ip, port = clientsocket.getpeername()
        #Evaluamos que la petición no esté vacía
        if not msg:
            print_lock.release()
            break
        #Response a enviar
        response='HTTP/1.0 200 OK\n\nConexión establecida con el servidor' 
        print("Mensaje recibido del cliente: ", ip, "port", port, "response", response)
        clientsocket.send(response.encode())
    #Cerramos conexión con proxy
    clientsocket.close()



####################################################################
########################## Función Main ############################
####################################################################

if __name__ == "__main__":
    option_check()
    #Creamos objeto socket
    s = socket.socket()
    host = '172.31.21.234'      # ip de la instancia donde corre el server
    #El puerto se recibe como argumento
    port = int(args[2])

    print ("Server corriendo con id", args[0])
    print ("Esperando en puerto", args[1])
        
    s.bind((host, port))     
    #Se permite tener hasta 10 clientes conectados
    s.listen(10)                 

    #Recibe cada conexión en un hilo diferente
    while True:
        c, addr = s.accept()     # Establecemos conexión con el proxy
        print_lock.acquire()
        print ('Mensaje recibido del cliente con ip', addr)
        _thread.start_new_thread(on_new_client,(c,addr))
        
    s.close()
