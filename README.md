# Proxy Inverso + Balanceador de Carga (PIBL)
## Proyecto I - Telemática
## Introducción
La siguiente es la implementación de un proxy inverso (reverse proxy) que cuenta con balanceador de cargas, 
es decir, distribuiye las peticiones entrantes hacia varios servidores.
Esta distribución se hace en base al principop Round Robin.

En este sentido, un proxy inverso se entiende como aquel que recibe (intercepta) cada
una de las peticiones del cliente y la envía a un servidor con la capacidad de procesar la
petición para finalmente enviar la respuesta al cliente.

Foto PILB

## Desarrollo
Los códigos se despliegan en la nube de Amazon Web Services empleando instancias EC2 (Amazon Linux).
Necesitaremos una instancia para el proxy inverso y tantas instancias como servidores se quieran.
Una vez se haya realizado la conexión con las instancia ec2, se puede clonar el repo utilizando el siguiente comando en el bash de AWS.

* Clonar repositorio
    ```sh
    $ git clone https://github.com/jmcastrom/PILB.git
    ```
Lo pertinente es correr la aplicación dentro de un entorno virtual.

* Creamos y activamos un venv en la carpeta `AWS-EC2-Adoption`

    ```sh
    $ cd PILB/AWS-EC2-Adoption/
    ```
    
    ```sh
    $ python3 -m venv venv
    ```
    
    ```sh
    $ source venv/bin/activate
    ```
   
Esto deberá ser realizado para cada una de las instancias que tengamos.

### Ejecución

* Correr proxy inverso en el puerto 8080 (desde la instancia proxy)

    ```sh
    $ python3 aws_rproxy.py -port 8080
    ```
* Correr servidor en el puerto 8080 (desde la instancia proxy)

    ```sh
    $ python3 aws_server.py -id 100 -pp 111 -listen 5000 -revproc 8080
    ```
    
Los valores (id/pp/listen/revproc) son argumentos de entrada, por lo que se pueden cambiar a conveniencia.

Una vez se esté ejecutando el proxy en el puerto deseado, y los servidores estén sincronizados con este, se le podrán realizar peticiones HTTP/1.1, ya sea desde un navegador, untilizando el comando `curl`, etc. Para esto necesitaremos la dirección ip pública de la instancia donde se ejecuta el proxy y el puerto en el que está corriendo.
El proxy recibirá la petición, se la enviará a uno de los servidores que tenga disponibles (basándose en el Round Robin), recibirá la respuesta de el servidor y se la retornará al cliente el formato texto

* Ejemplo de petición HTTP/1.1 utilizando `curl` desde el cmd

    ```sh
    > curl 127.00.000:8080
    ```

## Agradecimientos/Referencias

* [Stack Overflow](https://stackoverflow.com/)
* [Github](https://github.com)
* [Shanto Roy](https://shantoroy.com/network/write-a-reverse-proxy-server-in-python/)
* [João Ventura](https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842) 
* Al profe

