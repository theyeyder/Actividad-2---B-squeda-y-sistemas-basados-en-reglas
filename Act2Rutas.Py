import heapq
import tkinter as tk


# ==========================================
# CLASE VAG脫N
# ==========================================

class Vagon:
    def __init__(self, tipo, carga=0, capacidad=100):
        self.tipo = tipo
        self.carga = carga
        self.capacidad = capacidad

    def cargar(self, cantidad):
        espacio = self.capacidad - self.carga
        cantidad_cargada = min(cantidad, espacio)
        self.carga += cantidad_cargada
        return cantidad_cargada

    def descargar(self, cantidad):
        cantidad_descargada = min(cantidad, self.carga)
        self.carga -= cantidad_descargada
        return cantidad_descargada

    def __str__(self):
        return f"[{self.tipo}: {self.carga}/{self.capacidad}]"


# ==========================================
# CLASE TREN
# ==========================================

class Tren:
    def __init__(self, nombre):
        self.nombre = nombre
        self.vagones = []
        self.locomotora = "馃殏"

    def agregar_vagon(self, vagon):
        self.vagones.append(vagon)

    def quitar_vagon(self):
        if self.vagones:
            return self.vagones.pop()

    def carga_total(self):
        return sum(v.carga for v in self.vagones)

    def capacidad_total(self):
        return sum(v.capacidad for v in self.vagones)

    def dibujo(self):
        cuerpos = "-".join(str(v) for v in self.vagones)
        return f"{self.locomotora}-{cuerpos}"

    def __str__(self):
        return f"{self.nombre}: {self.dibujo()}"

    def __len__(self):
        return len(self.vagones)


# ==========================================
# CREAR TREN
# ==========================================

tren = Tren("Ruta Inteligente")

tren.agregar_vagon(
    Vagon("Pasajeros 1", carga=45, capacidad=80)
)

tren.agregar_vagon(
    Vagon("Pasajeros 2", carga=35, capacidad=80)
)

tren.agregar_vagon(
    Vagon("Equipaje", carga=90, capacidad=200)
)


# ==========================================
# BASE DE CONOCIMIENTO
# ==========================================

grafo = {
    "Terminal Norte": [
        ("Universidad", 5, "Linea A"),
        ("Centro", 12, "Linea B")
    ],

    "Universidad": [
        ("Terminal Norte", 5, "Linea A"),
        ("Hospital", 6, "Linea A")
    ],

    "Hospital": [
        ("Universidad", 6, "Linea A"),
        ("Centro", 4, "Linea A"),
        ("Estadio", 7, "Linea C")
    ],

    "Centro": [
        ("Terminal Norte", 12, "Linea B"),
        ("Hospital", 4, "Linea A"),
        ("Terminal Sur", 8, "Linea B")
    ],

    "Estadio": [
        ("Hospital", 7, "Linea C"),
        ("Terminal Sur", 5, "Linea C")
    ],

    "Terminal Sur": [
        ("Centro", 8, "Linea B"),
        ("Estadio", 5, "Linea C")
    ]
}


# ==========================================
# ESTACIONES
# ==========================================

estaciones = {
    1: "Terminal Norte",
    2: "Universidad",
    3: "Hospital",
    4: "Centro",
    5: "Estadio",
    6: "Terminal Sur"
}


# ==========================================
# PRECIOS POR DESTINO
# ==========================================

precios_destino = {
    "Terminal Norte": 5000,
    "Universidad": 3500,
    "Hospital": 4000,
    "Centro": 3000,
    "Estadio": 4500,
    "Terminal Sur": 5500
}


# ==========================================
# CONEXIONES TEMPORALMENTE BLOQUEADAS
# ==========================================

conexiones_bloqueadas = [
    # Ejemplo:
    # ("Hospital", "Centro")
]


# ==========================================
# REGLAS DEL SISTEMA
# ==========================================

def conexion_disponible(origen, destino):
    """
    REGLA 1:
    Si existe conexi贸n entre dos estaciones
    y no est谩 bloqueada,
    entonces el desplazamiento est谩 permitido.
    """

    if (origen, destino) in conexiones_bloqueadas:
        return False

    if (destino, origen) in conexiones_bloqueadas:
        return False

    return True


def costo_transferencia(linea_actual, nueva_linea):
    """
    REGLA 2:
    Si el usuario cambia de l铆nea,
    se agregan 3 minutos al recorrido.
    """

    if linea_actual is None:
        return 0

    if linea_actual != nueva_linea:
        return 3

    return 0


def es_destino(estacion_actual, destino):
    """
    REGLA 3:
    Si la estaci贸n actual es igual
    a la estaci贸n destino,
    el objetivo ha sido alcanzado.
    """

    return estacion_actual == destino


# ==========================================
# HEUR脥STICA
# ==========================================

def calcular_heuristica(destino):
    """
    Calcula una estimaci贸n del tiempo m铆nimo
    desde cada estaci贸n hasta el destino.
    """

    distancias = {
        estacion: float("inf")
        for estacion in grafo
    }

    distancias[destino] = 0
    cola = [(0, destino)]

    while cola:

        distancia_actual, estacion_actual = heapq.heappop(
            cola
        )

        if distancia_actual > distancias[estacion_actual]:
            continue

        for vecino, tiempo, linea in grafo[estacion_actual]:

            nueva_distancia = distancia_actual + tiempo

            if nueva_distancia < distancias[vecino]:

                distancias[vecino] = nueva_distancia

                heapq.heappush(
                    cola,
                    (
                        nueva_distancia,
                        vecino
                    )
                )

    return distancias


# ==========================================
# ALGORITMO A*
# ==========================================

def buscar_mejor_ruta(origen, destino):

    heuristica = calcular_heuristica(destino)

    cola = []
    contador = 0

    heapq.heappush(
        cola,
        (
            heuristica[origen],
            0,
            contador,
            origen,
            None,
            [origen]
        )
    )

    visitados = {}

    while cola:

        (
            costo_estimado,
            costo_real,
            identificador,
            estacion_actual,
            linea_actual,
            ruta
        ) = heapq.heappop(cola)

        if es_destino(estacion_actual, destino):
            return ruta, costo_real

        estado = (
            estacion_actual,
            linea_actual
        )

        if estado in visitados:
            if visitados[estado] <= costo_real:
                continue

        visitados[estado] = costo_real

        for vecino, tiempo, nueva_linea in grafo.get(
            estacion_actual,
            []
        ):

            if not conexion_disponible(
                estacion_actual,
                vecino
            ):
                continue

            transferencia = costo_transferencia(
                linea_actual,
                nueva_linea
            )

            nuevo_costo = (
                costo_real
                + tiempo
                + transferencia
            )

            estimacion = (
                nuevo_costo
                + heuristica[vecino]
            )

            nueva_ruta = ruta + [vecino]

            contador += 1

            heapq.heappush(
                cola,
                (
                    estimacion,
                    nuevo_costo,
                    contador,
                    vecino,
                    nueva_linea,
                    nueva_ruta
                )
            )

    return None, None


# ==========================================
# FORMATEAR PRECIO
# ==========================================

def formatear_precio(valor):
    return (
        f"${valor:,.0f}"
        .replace(",", ".")
    )


# ==========================================
# ANIMACI脫N GR脕FICA DEL TREN CON VAGONES
# ==========================================

def dibujar_tren(canvas, x, y, tren):
    """
    Dibuja un tren gr谩fico inspirado en el modelo de referencia:
    tres vagones rectangulares, locomotora azul y ruedas.
    Retorna los elementos dibujados para poder moverlos.
    """

    elementos = []

    verde = "#2f9e24"
    azul = "#176b87"
    borde = "#082f49"
    blanco = "#ffffff"

    ancho_vagon = 120
    alto_vagon = 52
    separacion = 24
    diametro_rueda = 28

    # Dibujar vagones
    for i, vagon in enumerate(tren.vagones):
        vx = x + i * (ancho_vagon + separacion)

        cuerpo = canvas.create_rectangle(
            vx,
            y,
            vx + ancho_vagon,
            y + alto_vagon,
            outline=verde,
            width=3,
            fill=blanco
        )
        elementos.append(cuerpo)

        # Texto corto del vag贸n
        etiqueta = canvas.create_text(
            vx + ancho_vagon / 2,
            y + alto_vagon / 2,
            text=vagon.tipo,
            font=("Arial", 9, "bold"),
            fill="#1f2937"
        )
        elementos.append(etiqueta)

        # Ruedas
        for rueda_x in (vx + 28, vx + ancho_vagon - 28):
            rueda = canvas.create_oval(
                rueda_x - diametro_rueda / 2,
                y + alto_vagon + 10,
                rueda_x + diametro_rueda / 2,
                y + alto_vagon + 10 + diametro_rueda,
                fill=azul,
                outline=borde,
                width=2
            )
            elementos.append(rueda)

        # Acople al siguiente vag贸n / locomotora
        acople = canvas.create_rectangle(
            vx + ancho_vagon,
            y + 20,
            vx + ancho_vagon + separacion,
            y + 28,
            fill=azul,
            outline=borde,
            width=2
        )
        elementos.append(acople)

    # Locomotora a la derecha
    locomotora_x = x + len(tren.vagones) * (ancho_vagon + separacion)

    cabina = canvas.create_rectangle(
        locomotora_x,
        y - 28,
        locomotora_x + 118,
        y + alto_vagon,
        outline=verde,
        width=3,
        fill=blanco
    )
    elementos.append(cabina)

    # Parte azul frontal de la locomotora
    caldera = canvas.create_arc(
        locomotora_x + 18,
        y - 8,
        locomotora_x + 100,
        y + 58,
        start=0,
        extent=180,
        style=tk.PIESLICE,
        fill=azul,
        outline=borde,
        width=2
    )
    elementos.append(caldera)

    # Chimenea
    chimenea = canvas.create_rectangle(
        locomotora_x + 55,
        y - 70,
        locomotora_x + 73,
        y - 28,
        fill=azul,
        outline=borde,
        width=2
    )
    elementos.append(chimenea)

    tapa = canvas.create_oval(
        locomotora_x + 55,
        y - 74,
        locomotora_x + 73,
        y - 66,
        fill=azul,
        outline=borde,
        width=2
    )
    elementos.append(tapa)

    # Rueda de locomotora
    rueda_loco = canvas.create_oval(
        locomotora_x + 42,
        y + alto_vagon + 10,
        locomotora_x + 76,
        y + alto_vagon + 44,
        fill=azul,
        outline=borde,
        width=2
    )
    elementos.append(rueda_loco)

    return elementos


def dibujar_estacion(canvas, nombre):
    """
    Dibuja una parada de tren sencilla al lado derecho.
    """

    x = 775
    y = 115

    # Techo
    canvas.create_polygon(
        x - 20, y + 35,
        x + 85, y - 5,
        x + 190, y + 35,
        fill="#d1d5db",
        outline="#374151",
        width=2
    )

    # Edificio
    canvas.create_rectangle(
        x,
        y + 35,
        x + 170,
        y + 150,
        fill="#f8fafc",
        outline="#374151",
        width=2
    )

    # Puerta
    canvas.create_rectangle(
        x + 65,
        y + 85,
        x + 105,
        y + 150,
        fill="#cbd5e1",
        outline="#374151",
        width=2
    )

    # Letrero
    canvas.create_rectangle(
        x + 15,
        y + 50,
        x + 155,
        y + 78,
        fill="#ffffff",
        outline="#2f9e24",
        width=2
    )

    canvas.create_text(
        x + 85,
        y + 64,
        text=nombre,
        font=("Arial", 10, "bold"),
        fill="#111827"
    )

    # And茅n
    canvas.create_rectangle(
        x - 35,
        y + 150,
        x + 205,
        y + 165,
        fill="#9ca3af",
        outline="#6b7280"
    )


def animar_tren(origen, destino, tren, destino_final=False):
    """
    Abre una ventana gr谩fica y mueve el tren completo
    desde el lado izquierdo hasta la estaci贸n destino.
    """

    ventana = tk.Tk()
    ventana.title("Sistema inteligente de rutas")
    ventana.geometry("1000x390")
    ventana.resizable(False, False)

    canvas = tk.Canvas(
        ventana,
        width=1000,
        height=390,
        bg="white",
        highlightthickness=0
    )
    canvas.pack()

    # Encabezado
    canvas.create_text(
        500,
        28,
        text=f"{origen}  鈫? {destino}",
        font=("Arial", 16, "bold"),
        fill="#111827"
    )

    # V铆a
    canvas.create_line(
        0,
        290,
        1000,
        290,
        fill="#4b5563",
        width=4
    )

    canvas.create_line(
        0,
        306,
        1000,
        306,
        fill="#4b5563",
        width=4
    )

    # Durmientes
    for x in range(0, 1000, 35):
        canvas.create_line(
            x,
            282,
            x + 12,
            314,
            fill="#6b7280",
            width=2
        )

    dibujar_estacion(canvas, destino)

    # El tren inicia fuera de la ventana
    inicio_x = -560
    posicion_y = 205

    elementos = dibujar_tren(
        canvas,
        inicio_x,
        posicion_y,
        tren
    )

    # Distancia que debe avanzar para quedar junto a la estaci贸n
    pasos = 150
    desplazamiento = 5

    def mover(paso=0):
        if paso < pasos:
            for elemento in elementos:
                canvas.move(
                    elemento,
                    desplazamiento,
                    0
                )

            ventana.after(
                25,
                lambda: mover(paso + 1)
            )

        else:
            if destino_final:
                mensaje = f"隆Llegamos a {destino}!"
            else:
                mensaje = f"Parada: {destino}"

            canvas.create_text(
                500,
                345,
                text=mensaje,
                font=("Arial", 18, "bold"),
                fill="#176b87"
            )

            # Mantener la llegada visible y cerrar autom谩ticamente
            ventana.after(
                1800,
                ventana.destroy
            )

    ventana.after(
        300,
        mover
    )

    ventana.mainloop()


# ==========================================
# MOSTRAR PARADA INTERMEDIA EN CONSOLA
# ==========================================

def mostrar_parada(estacion):

    print("\n============================================")
    print(f"       PARADA INTERMEDIA: {estacion}")
    print("============================================")
    print("El tren contin煤a su recorrido...")
    print("============================================")


# ==========================================
# MOSTRAR LLEGADA FINAL EN CONSOLA
# ==========================================

def mostrar_estacion(destino):

    print("\n============================================")
    print(f"       ESTACI脫N FINAL: {destino}")
    print("============================================")
    print("       EL TREN HA LLEGADO A SU DESTINO")
    print("============================================\n")


# ==========================================
# SELECCIONAR ESTACI脫N DE ORIGEN
# ==========================================

def seleccionar_origen():

    print("================================")
    print("\nSELECCIONE LA ESTACI脫N DE ORIGEN")
    print("================================")

    for numero, estacion in estaciones.items():
        print(f"{numero}. {estacion}")

    while True:

        try:

            opcion = int(
                input(
                    "\nSeleccione una opci贸n: "
                )
            )

            if opcion in estaciones:
                return estaciones[opcion]

            print(
                "\nOpci贸n incorrecta."
            )

            print(
                "Seleccione un n煤mero del 1 al 6."
            )

        except ValueError:

            print(
                "\nDebe ingresar 煤nicamente un n煤mero."
            )


# ==========================================
# SELECCIONAR ESTACI脫N DE DESTINO
# ==========================================

def seleccionar_destino(origen):

    print("=================================")
    print("\nSELECCIONE LA ESTACI脫N DE DESTINO")
    print("=================================")

    opciones_destino = {}
    numero = 1

    for estacion in estaciones.values():

        if estacion != origen:

            precio = precios_destino[estacion]

            opciones_destino[numero] = estacion

            print(
                f"{numero}. "
                f"{estacion} - "
                f"{formatear_precio(precio)}"
            )

            numero += 1

    while True:

        try:

            opcion = int(
                input(
                    "\nSeleccione una opci贸n: "
                )
            )

            if opcion in opciones_destino:
                return opciones_destino[opcion]

            print(
                "\nOpci贸n incorrecta."
            )

            print(
                "Seleccione una de las opciones disponibles."
            )

        except ValueError:

            print(
                "\nDebe ingresar 煤nicamente un n煤mero."
            )


# ==========================================
# EJECUTAR SISTEMA
# ==========================================

def ejecutar_sistema():

    print(
        "\n*****************************************************"
    )

    print(
        "\nHOLA, BIENVENIDO AL SISTEMA INTELIGENTE DE RUTAS"
    )

    print(
        "\n*****************************************************"
    )

    print("\nTREN DISPONIBLE")
    print("===============")
    print(tren)

    print(
        f"\nN煤mero de vagones: {len(tren)}"
    )

    print(
        f"Capacidad total de los vagones: "
        f"{tren.capacidad_total()}"
    )

    print(
        f"Carga actual total: "
        f"{tren.carga_total()}"
    )


    # ==========================================
    # ORIGEN
    # ==========================================

    origen = seleccionar_origen()

    print(
        f"\nEstaci贸n de origen seleccionada: {origen}"
    )


    # ==========================================
    # DESTINO
    # ==========================================

    destino = seleccionar_destino(
        origen
    )

    precio = precios_destino[
        destino
    ]

    print(
        f"\nEstaci贸n de destino seleccionada: {destino}"
    )

    print(
        f"Precio del viaje: {formatear_precio(precio)}"
    )


    # ==========================================
    # BUSCAR MEJOR RUTA
    # ==========================================

    ruta, tiempo_estimado = buscar_mejor_ruta(
        origen,
        destino
    )


    # ==========================================
    # MOSTRAR RESULTADO
    # ==========================================

    if ruta:

        print(
            "\n================================"
        )

        print(
            "      MEJOR RUTA ENCONTRADA"
        )

        print(
            "================================"
        )

        print(
            f"\nOrigen: {origen}"
        )

        print(
            f"Destino: {destino}"
        )

        print(
            f"Valor del viaje: "
            f"{formatear_precio(precio)}"
        )

        print(
            "\nRuta recomendada:"
        )

        print(
            " -> ".join(ruta)
        )

        print(
            f"\nTiempo estimado: "
            f"{tiempo_estimado} minutos"
        )

        print("\nTren asignado:")
        print(tren.dibujo())


        # ======================================
        # INICIAR SIMULACI脫N DEL VIAJE
        # ======================================

        input(
            "\nPresione ENTER para iniciar el viaje..."
        )

        for i in range(len(ruta) - 1):

            estacion_actual = ruta[i]
            siguiente_estacion = ruta[i + 1]

            es_final = (
                siguiente_estacion == destino
            )

            animar_tren(
                estacion_actual,
                siguiente_estacion,
                tren,
                destino_final=es_final
            )

            if not es_final:

                mostrar_parada(
                    siguiente_estacion
                )


        # ======================================
        # LLEGADA AL DESTINO FINAL
        # ======================================

        mostrar_estacion(
            destino
        )

        print(
            f"Destino final: {destino}"
        )

        print(
            f"Valor pagado: {formatear_precio(precio)}"
        )

        print(
            f"Tiempo estimado del recorrido: "
            f"{tiempo_estimado} minutos"
        )

    else:

        print(
            "\nNo existe una ruta disponible "
            "entre las estaciones seleccionadas."
        )


# ==========================================
# MEN脷 PARA VOLVER A INICIAR
# ==========================================

while True:

    ejecutar_sistema()

    print(
        "\n============================================"
    )

    print(
        "驴QU脡 DESEA HACER?"
    )

    print(
        "============================================"
    )

    print("1. Volver a iniciar")
    print("2. Salir")

    while True:

        try:

            opcion_final = int(
                input(
                    "\nSeleccione una opci贸n: "
                )
            )

            if opcion_final in [1, 2]:
                break

            print(
                "\nOpci贸n incorrecta. "
                "Seleccione 1 o 2."
            )

        except ValueError:

            print(
                "\nDebe ingresar 煤nicamente un n煤mero."
            )

    if opcion_final == 1:

        print(
            "\n\nREINICIANDO EL SISTEMA..."
        )

        print(
            "============================================\n"
        )

        continue

    else:

        print(
            "\n============================================"
        )

        print(
            "GRACIAS POR UTILIZAR EL SISTEMA DE RUTAS"
        )

        print(
            "============================================\n"
        )

        break
