# Proxy inverso con balanceador de cargas
# Python 3


# Modulos requeridos
import socket
import _thread
import threading
import sys
import json
import pandas as pd
import itertools

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

#Función que servirá para iterar entre los servidores disponibles
def round_robin(iterable):
    return next(iterable)

# Definimos la tabla donde se almacenaran los servidores disponibles
column_names = ["type", "id", "privPolyId", "listenport", "ip_addr"]
updated_available_server_table = pd.DataFrame(columns = column_names)

# Creación de tabla que contiene los servidores disponibles
def available_server(msg):
    global updated_available_server_table
    global policy_table

    updated_available_server_table = updated_available_server_table.append(msg, ignore_index = True)
    policy_list = set(updated_available_server_table["privPolyId"].tolist())    
    policy_table = {}
    for policy in policy_list:
        policy_table[policy] = itertools.cycle(set(updated_available_server_table\
                [updated_available_server_table["privPolyId"]==policy]["id"].tolist()))


    
# Establecer nueva conexión (cliente o servidor)
def on_new_client(clientsocket,addr):
    n=0
    while True:
        #Petición recibida 
        #La petición tiene formato json si es una petición de un servidor y formato HTTP/1.1 si es una petición de un cliente
        request = clientsocket.recv(1024).decode()        
        requestjson={}
        print("**************************************")
        try:
            #En caso de ser una petición de un server se almacena como un archivo json
            requestjson=json.loads(request)
            print("Nueva conexión")
            print("requestjson: ", requestjson)
            print(type(requestjson))
        except:
            pass    
        
        #Evaluamos que la petición no esté vacía
        if not request:
            print_lock.release()
            break

        #En caso de que la conexión sea proveniente de un servidor, este se almacena en la tabla de servidores disponibles.
        if  "type" in requestjson and requestjson["type"] == "1":
            print("Nueva petición de servidor recibida")
            ip, port = clientsocket.getpeername()
            requestjson["ip_addr"] = ip
            print ("Mensaje recibido de servidor con id", requestjson["id"], "ip", requestjson["ip_addr"],\
                    "privacy policy", requestjson["privPolyId"], "port", requestjson["listenport"])
            available_server(requestjson)

        #En caso de que la conexión sea proveniente de un cliente, su petición es enviada a los servidores disponibles.
        #La respuesta de los servers se le entrega dal cliente.
        elif request != "":
            print("Nueva conexión")
            print("request: ", request)
            print("Nueva petición de cliente recibida")
            #Obtener datos del cliente (ip y puerto)
            ip, port = clientsocket.getpeername()
            print ('Mensaje recibido del cliente: ', ip, \
                                                "port ", port)
            #Generamos diccionario con el que el proxy se comunicará con los servidores
            msg = json.dumps({"type": "0", "srcid": "proxyPILB420", "privPoliId": "111", "payload": "xyz1"})
            #Convertimos el diccionario a archivo JSON
            new_json_msg = json.loads(msg)
            policy = new_json_msg["privPoliId"]

            #Se escoge un servidor de los disponibles en la tabla creada en base al método Round Robin
            target_host_id = round_robin(policy_table[policy])
            server_name = updated_available_server_table.loc\
                            [updated_available_server_table["id"]==target_host_id, "ip_addr"].values[0]
            server_port = int(updated_available_server_table.loc\
                            [updated_available_server_table["id"]==target_host_id, "listenport"].values[0])
            #Iniciamos un nuevo socket y realizamos la conexión
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.connect((server_name,server_port))        
            print("Reenviando datos a servidor con id", target_host_id, "server ip", server_name, \
                                                    "port", server_port)
            #Enviamos al servidor elegido el archivo JSON generado
            server_socket.send(json.dumps(new_json_msg).encode())
            #Recibimos archivo JSON por parte del servidor
            recv_msg = server_socket.recv(2048)
            recv_json_msg = json.loads(recv_msg.decode())
            #Extraemos la response del JSON recibido
            response=recv_json_msg["response"]
            print("Response recibida", response)
            print ("Mensaje recibido de servidor con id", recv_json_msg["srcid"],\
                                                    "payload", recv_json_msg["payload"])
            print("")
            #Cerramos conexión con el server
            server_socket.close()
            #Enviamos HTTP response al cliente
            response = 'HTTP/1.0 200 OK\n\n'+response
            print("Enviando response", response,)
            clientsocket.sendall(response.encode())
            print("Response se ha envíado al cliente correctamente")
            n=1
        else:
            pass
        if n!=0:
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