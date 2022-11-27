# Proxy inverso con balanceador de cargas
# Python 3


# Modulos requeridos
import socket
import _thread
import threading
import sys

# Habilitar bloqueo para un thread
print_lock = threading.Lock()

####################################################################
#################### Configuración de opciones #####################
####################################################################

def option_check():
    #Argumentos recibidos
    avail_options = ["-port"]

    #Recibe opciones y argumentos dados por el cliente
    options = [opt for opt in sys.argv[1:] if opt.startswith("-")]    
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    #Error en caso de que las opciones no sean válidos
    for i in options:
        if i not in avail_options:
            raise SystemExit(f"Usage: {sys.argv[0]} -port <argument>...")

    #Error en caso de que los argumentos no sean válidos
    if len(options) != 1 or len(args) != 1:
        raise SystemExit(f"Usage: {sys.argv[0]} -port <argument>...")

    return args

####################################################################
######################## Funciones básicas #########################
####################################################################

#Caché
cacheDict={}

#Funcíon que guarda el caché en diccionario
def save_cache(id, response):
    if not id in cacheDict:
        print("Guardado en caché")
        cacheDict[id]=response
        print("Cache: ", cacheDict)
        
#Función que retorna el caché del diccionario        
def return_cache(id):
    if id in cacheDict:
        return cacheDict[id]
    else:
        return "Hubo un fallo en el servidor y no se encontr+o registro de caché"    
    
    
#Lista de servidores disponibles y sus puertos
servers=[['172.31.21.234', '5000'], ['google.com', '80']]
n = -1
#Función que servirá para iterar entre los servidores disponibles
def round_rob_server():
  global n
  n = n + 1
  if n == len(servers):
     n = 0
  return servers[n]
    
# Establecer nueva conexión (cliente o servidor)
def on_new_client(clientsocket,addr):
    while True:
        #Petición recibida
        request = clientsocket.recv(1024).decode()
        print("**************************************")
        print("Nueva petición de recibida")  
        #Evaluamos que la petición no esté vacía
        if not request:
            print_lock.release()
            break
        print("request: ", request)
        
        #Guardamos la petición enarchivo txt
        with open("log.txt", "a") as text_file:
            text_file.write(request + "\n")
        #Obtener datos del cliente (ip y puerto)
        ip, port = clientsocket.getpeername()
        print ('Mensaje recibido del cliente: ', ip, \
                                            "port ", port)  
        #Obtenemos el servidor a contactar
        contact_server = round_rob_server()
        #La ip y el puerto de los server se toma de la lista de servidores en base a Round Robin
        server_name = contact_server[0]
        print(server_name)
        server_port = int(contact_server[1])
        print(server_port)
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((server_name,server_port))        
            print("Reenviando datos a servidor con ip", server_name, \
                                                    "port", server_port)
            #La petición es enviada al servidor
            server_socket.send(request.encode())
            #La respuesta del servidor se devuelve al cliente
            response = server_socket.recv(2048).decode()
            save_cache(server_name, response)
            print("Response recibida", response)
            print("")
            #Cerramos conexión con el server
            server_socket.close()
        except:
            print("Hubo un problema en la conexión, respuesta entregada desde caché")
            response = return_cache(server_name)
        print("Enviando response", response,)
        clientsocket.sendall(response.encode())
        print("Response se ha envíado al cliente correctamente")
        break
    #Cerramos conexión con el cliente
    clientsocket.close()
               
####################################################################
########################## Función Main ############################
####################################################################

if __name__ == "__main__":
    args = option_check()
    #Creamos objeto socket
    s = socket.socket()  
    host = '172.31.21.133' # ip de la instancia donde corre el proxy
    #El puerto se recibe como argumento
    port = int(args[0])              
    print("Ejecutando PILB en puerto", port)
    s.bind((host, port))     
    #Se permite tener hasta 10 clientes conectados
    s.listen(100)

    while True:
        c, addr = s.accept()     # Establecemos conexión con el cliente
        print_lock.acquire(blocking=False)
        _thread.start_new_thread(on_new_client,(c,addr))        
    s.close()
