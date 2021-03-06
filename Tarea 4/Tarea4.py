import threading
from threading import Thread
from threading import Semaphore
from threading import Event
from datetime import datetime
import time
import math

cant_bandejas = input("Cantidad de bandejas: ")
cant_clientes = input("Cantidad de clientes: ")
bandejas = [] # Lista de bandejas de la fila
bandejasSucias = [] # Lista de bandejas usadas del bandejero
maxCapacidadBandejero = math.ceil(int(cant_bandejas)/2)

numeroCliente = 1

# Semáforo para que solo una persona use el recurso
s_usarBandejeroFila = Semaphore(1)
s_usarBandejero = Semaphore(1)
s_usarMesa = Semaphore(1)
s_JuanSirviendo = Semaphore(0)
s_clienteAyudando = Semaphore(1)
s_sentarseParaAlmorzar = Semaphore(1)
s_sacarNumero = Semaphore(1)

# Semáforo para que Juan y los clientes se coordinen
s_hayEspacioBandejero = Semaphore(maxCapacidadBandejero)
s_cantidadBandejasFila = Semaphore(int(cant_bandejas))
s_boletero = Semaphore(1)
s_boleteroDejarBandeja = Semaphore(1)

# Eventos de coordinación de los clientes
end = Event()
e_hayCliente = Event()
e_almuerzoServido = Event()
e_estoyAlmorzando = Event()
e_yaAlmorce = Event()
e_hayAyudante = Event()
e_estoyAyudando = Event()
e_ayudanteTieneBandeja = Event()

# Eventos de coordinación de las bandejas
e_HayBandejasFila = Event()
e_hayBandejasBandejero = Event()
e_bandejeroLleno = Event()
e_JuanRepusoBandejas = Event()
e_JuanVacioBandejero = Event()

"""
Nombre: mesaAuxiliar
Parametros: ninguno
Descripcion: Simula al cliente que ayuda a otro cliente a comer, siendo la mesa auxiliar sus manos que mantienen la bandeja.
"""
class mesaAuxiliar:
    def __init__(self):
        self.bandeja = None
        self.cliente = None
    
    def sostener_bandeja(self, b, c):
        self.bandeja = b
        self.cliente = c

    def release_bandeja(self):
        self.bandeja = None

    def get_bandeja(self):
        return self.bandeja
    
    def get_idCliente(self):
        return self.cliente

"""
Nombre: bandeja
Parametros: ninguno
Descripcion: Bandeja en donde se pondrá el almuerzo.
"""
class bandeja:
    def __init__(self):
        self.comida = False

    def hayComida(self):
        return self.comida

    def comer(self):
        self.comida = False

    def llenar(self):
        self.comida = True

"""
Nombre: cocina
Parametros: ninguno
Descripcion: Cocina es donde se dejará la bandeja para que Juan sirva el almuerzo.
"""
class cocina:
    def __init__(self):
        self.bandeja = None
        self.cliente = None
    
    def insert_bandeja(self, b, c):
        self.bandeja = b
        self.cliente = c

    def release_bandeja(self):
        self.bandeja = None

    def get_bandeja(self):
        return self.bandeja
    
    def get_idCliente(self):
        return self.cliente

mesa = cocina()
mesaAlmuerzo = cocina()

"""
Nombre: Acompanante
Parametros: ninguno
Descripcion: Acompañante de un cliente que se crea cuando no hay otro cliente disponible para ayudar. Se encarga de afirmar
    la bandeja del cliente y luego dejarla en el bandejero.
"""
class Acompanante(Thread):
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        global s_clienteAyudando, e_estoyAyudando, e_yaAlmorce, e_estoyAlmorzando, e_hayAyudante, e_bandejeroLleno, s_usarBandejero
        global mesaAlmuerzo, bandejasSucias, maxCapacidadBandejero, s_boletero
        s_clienteAyudando.acquire()
        e_hayAyudante.set()
        #Limpio los eventos de comer y después ayudo
        e_estoyAlmorzando.clear()
        e_yaAlmorce.clear()
        e_ayudanteTieneBandeja.clear()
        e_estoyAyudando.set()
        if(e_estoyAlmorzando.wait(8)):
            e_yaAlmorce.wait()
            bandeja = mesaAlmuerzo.get_bandeja()
            mesaAlmuerzo.release_bandeja()
            e_ayudanteTieneBandeja.set()
            e_estoyAyudando.clear()

            # DEJAR BANDEJA
            s_hayEspacioBandejero.acquire()
            s_usarBandejero.acquire()
            now = datetime.now()
            f_clientes = open("clientes.txt", "a")
            f_clientes.write("Companero dejando bandeja en el bandejero, hora: " + now.strftime("%H:%M:%S") + "\n")
            f_clientes.close()
            bandejasSucias.append(bandeja)
            e_hayBandejasBandejero.set()
            s_usarBandejero.release()
        else:
            e_estoyAyudando.clear()
            e_hayAyudante.clear()
        s_clienteAyudando.release()

"""
Nombre: Cliente
Parametros: ninguno
Descripcion: Cliente que quiere almorzar y ayudar a otros a comer. Primero se le asigna un número, luego saca una bandeja, espera
    a que Juan le sirva el almuerzo, pide a un cliente o acompañante que le ayude a almorzar, después se ofrece para ayudar a otro
    cliente a almorzar, lo ayuda y por último, deja la bandeja en el bandejero.
"""
class Cliente(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global s_usarBandejeroFila, e_almuerzoServido, e_bandejeroLleno, e_JuanRepusoBandejas, s_sacarNumero
        global bandejas, mesa, mesaAlmuerzo, existeClienteAyudando, maxCapacidadBandejeron, numeroCliente
        id_cliente = threading.get_ident()

        # SACAR UN NUMERO
        s_sacarNumero.acquire()
        id_cliente = numeroCliente
        numeroCliente +=1
        s_sacarNumero.release() 

        # SACAR BANDEJAS
        s_boletero.acquire()
        # Si no hay bandejas en la fila, llama a Juan
        if (s_cantidadBandejasFila.acquire(0) == False):
            e_HayBandejasFila.clear() # Llamando a Juan para que traiga bandejas
            s_cantidadBandejasFila.acquire()
        s_boletero.release()
        s_usarBandejeroFila.acquire()
        now = datetime.now()
        f_clientes = open("clientes.txt", "a")
        f_clientes.write("Cliente " + str(id_cliente) + " sacando bandeja en la fila, hora: " + now.strftime("%H:%M:%S") + "\n")
        f_clientes.close()
        bandeja = bandejas.pop(0)
        s_usarBandejeroFila.release()

        # BUSCAR ALMUERZO
        s_usarMesa.acquire()
        e_almuerzoServido.clear()
        mesa.insert_bandeja(bandeja, id_cliente)
        e_hayCliente.set()
        now = datetime.now()
        f_clientes = open("clientes.txt", "a")
        f_clientes.write("Cliente " + str(id_cliente) + " esperando a que Juan le sirva almuerzo, hora: " + now.strftime("%H:%M:%S") + "\n")
        f_clientes.close()
        e_almuerzoServido.wait()
        s_usarMesa.release()

        # COMER ALMUERZO
        s_sentarseParaAlmorzar.acquire()
        # Si hay quien pueda ayudarme, almuerzo. Si no, traigo un acompañante
        if(not(e_hayAyudante.is_set())):
            Acomp = Acompanante()
            Acomp.start()
        e_estoyAyudando.wait()
        e_estoyAlmorzando.set()
        mesaAlmuerzo.insert_bandeja(bandeja, id_cliente)
        time.sleep(5) # Cliente come su almuerzo
        bandeja.comer()
        e_yaAlmorce.set()
        now = datetime.now()
        f_clientes = open("clientes.txt", "a")
        f_clientes.write("Cliente " + str(id_cliente) + " termino de comer, hora: " + now.strftime("%H:%M:%S") + "\n")
        f_clientes.close()
        e_ayudanteTieneBandeja.wait()
        s_sentarseParaAlmorzar.release()

        # AYUDAR AL SIGUIENTE CLIENTE
        s_clienteAyudando.acquire()
        # Limpio los eventos de comer y después ayudo
        e_estoyAlmorzando.clear()
        e_yaAlmorce.clear()
        e_ayudanteTieneBandeja.clear()
        e_estoyAyudando.set()
        if(e_estoyAlmorzando.wait(30)): # Espera 30 segundos a que aparezca otro cliente para ayudar
            e_yaAlmorce.wait()
            bandeja = mesaAlmuerzo.get_bandeja()
            mesaAlmuerzo.release_bandeja()
            e_ayudanteTieneBandeja.set()
            e_estoyAyudando.clear()

            # DEJAR BANDEJA
            s_boleteroDejarBandeja.acquire()
            if(s_hayEspacioBandejero.acquire(0) == False):
                e_bandejeroLleno.set()
                s_hayEspacioBandejero.acquire()
            s_boleteroDejarBandeja.release()
            s_usarBandejero.acquire()
            # Si el bandejero esta lleno, llama a Juan para que lo vacie
            if (len(bandejasSucias) >= maxCapacidadBandejero):
                e_JuanVacioBandejero.clear()
                e_bandejeroLleno.set()
                e_JuanVacioBandejero.wait()
            now = datetime.now()
            f_clientes = open("clientes.txt", "a")
            f_clientes.write("Cliente " + str(id_cliente) + " dejando bandeja en el bandejero, hora: " + now.strftime("%H:%M:%S") + "\n")
            f_clientes.close()
            bandejasSucias.append(bandeja)
            if (e_hayBandejasBandejero.is_set() == False):
                e_hayBandejasBandejero.set()
            s_usarBandejero.release()
        else:
            e_estoyAyudando.clear()
            e_hayAyudante.clear()
            now = datetime.now()
            f_clientes = open("clientes.txt", "a")
            f_clientes.write("Cliente " + str(id_cliente) + " se retira, hora: " + now.strftime("%H:%M:%S") + "\n")
            f_clientes.close()
        s_clienteAyudando.release()

"""
Nombre: Juan
Parametros: ninguno
Descripcion: Juan, el encargado de servir almuerzos. Sirve almuerzos hasta que no hayan clientes a los que pueda servir almuerzo,
    luego de esto revisa si el bandejero de la fila está vacío y después revisa si el bandejero de las bandejas sucias está lleno.
    Una vez hecho esto, vuelve a servir almuerzos hasta que se le avise que se puede retirar.
"""
class Juan(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global s_JuanSirviendo, e_hayCliente, e_almuerzoServido, e_bandejeroLleno, s_usarBandejero
        global mesa, end

        while (end.is_set() != True):
            # SERVIR ALMUERZOS
            sirviendo_almuerzos = True
            while (sirviendo_almuerzos):
                if (e_hayCliente.wait(8)):
                    cliente_servir = mesa.get_idCliente()
                    f_juan = open("juan.txt", "a")
                    now = datetime.now()
                    f_juan.write("Sirviendo al cliente " + str(cliente_servir) + ", hora: " + now.strftime("%H:%M:%S") + "\n")
                    f_juan.close()
                    time.sleep(3) # Juan sirve almuerzo
                    mesa.get_bandeja().llenar()
                    mesa.release_bandeja()
                    e_hayCliente.clear()
                    e_almuerzoServido.set()
                else:
                    sirviendo_almuerzos = False
                    
            # RELLENAR BANDEJERO FILA
            if (e_HayBandejasFila.is_set() == False):
                e_hayBandejasBandejero.wait()
                s_usarBandejero.acquire()
                now = datetime.now()
                f_juan = open("juan.txt", "a")
                f_juan.write("Rellenando bandejero de la fila, hora: " + now.strftime("%H:%M:%S") + "\n")
                f_juan.close()
                while(len(bandejasSucias) > 0):
                    bandejas.append(bandejasSucias.pop(0))
                    s_hayEspacioBandejero.release()
                    s_cantidadBandejasFila.release()
                e_HayBandejasFila.set()
                e_JuanRepusoBandejas.set()
                e_hayBandejasBandejero.clear()
                s_usarBandejero.release()

            # VACIAR BANDEJERO
            if (e_bandejeroLleno.is_set()):
                s_usarBandejeroFila.acquire()
                while(len(bandejasSucias) > 0):
                    bandejas.append(bandejasSucias.pop(0))
                    s_cantidadBandejasFila.release()
                    s_hayEspacioBandejero.release()
                now = datetime.now()
                f_juan = open("juan.txt", "a")
                f_juan.write("Vaciando bandejero, hora: " + now.strftime("%H:%M:%S") + "\n")
                f_juan.close()
                e_bandejeroLleno.clear()
                e_JuanVacioBandejero.set()
                s_usarBandejeroFila.release()
         
def main(): 
    global cant_bandejas, cant_clientes, bandejas, mesa, e_hayBandejasBandejero, end, e_bandejeroLleno
    
    e_bandejeroLleno.clear()
    end.clear()

    for b in range(int(cant_bandejas)):
        bandejas.append(bandeja())

    f_Juan = open("juan.txt", "w")
    f_Clientes = open("clientes.txt", "w")
    f_Juan.close()
    f_Clientes.close()

    thread_juan = Juan()
    thread_juan.start()
    
    for cliente in range(int(cant_clientes)):
        thread = Cliente()
        thread.start()

    while (end.is_set() != True):
        input_ = input("Ingrese 1 para añadir más clientes, ingrese 0 para terminar el programa.\n")
        if (input_ == '1'):
            thread = Cliente()
            thread.start()
        elif (input_ == '0'):
            now = datetime.now()
            f_juan = open("juan.txt", "a")
            f_juan.write("Juan se retira del casino" + ", hora: " + now.strftime("%H:%M:%S") + "\n")
            f_juan.close()
            end.set()

if __name__ == '__main__':
    main()