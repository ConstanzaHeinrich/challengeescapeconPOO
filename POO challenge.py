import random
import heapq


class Mapa:
    def __init__(self):
        self.entrada = None #sin posicion definida
        self.salida = None
        self.tablero = []
        self.filas = 0 #sin tamaño definido
        self.columnas = 0
        self.obstaculo = None
        self.tipo_obstaculo = None
        self.emoji_ciudad = ["🏨", "🏢", "🌳", "🏛️", "🚧", "🏦", "🏙️", "🏬", "💒", "🏭", "🏘️"]
        self.entrada_emoji = "⭐"
        self.salida_emoji = "➡️"

    def configurar_mapa(self):
        print("🗺️ GENERADOR DE MAPAS CON A*")
        print("=" * 50)
        while True:
            self.filas = int(input("Ingrese el número de FILAS (mínimo 15): "))
            self.columnas = int(input("Ingrese el número de COLUMNAS (mínimo 15): "))
            if self.filas >= 15 and self.columnas >= 15:
                break
            else:
                print("⚠️ El tamaño mínimo es 15x15. Intente de nuevo.")

        self.tablero = [["◻️" for _ in range(self.columnas)] for _ in range(self.filas)]

        self.entrada = self.pedir_coordenada("ENTRADA") #aca se le define al metodo que se crea mas abajo
        self.salida = self.pedir_coordenada("SALIDA")

        self.tablero[self.entrada[0]][self.entrada[1]] = self.entrada_emoji
        self.tablero[self.salida[0]][self.salida[1]] = self.salida_emoji

        while True:
            tipo = input("Elegí obstáculo (raudal o bache): ").strip().lower()
            if tipo == "raudal":
                self.obstaculo = "🌊"
                self.tipo_obstaculo = "raudal"
                break
            elif tipo == "bache":
                self.obstaculo = "🕳️"
                self.tipo_obstaculo = "bache"
                break
            else:
                print("⚠️ Opción inválida. Escribí 'raudal' o 'bache'.")

        print(f"\n📋 INFORMACIÓN DE COSTOS:")
        print(f"• Camino vacío (◻️): 1 punto")
        print(f"• {self.tipo_obstaculo.capitalize()} ({self.obstaculo}): 5 puntos")

    def pedir_coordenada(self, tipo):
        while True:
            try:
                entrada = input(f"Coordenada de {tipo} (formato: fila,columna): ")
                f, c = map(int, entrada.split(','))
                if 0 <= f < self.filas and 0 <= c < self.columnas:
                    if tipo == "SALIDA" and (f, c) == self.entrada:
                        print("⚠️ La SALIDA no puede estar en la misma casilla que la ENTRADA.")
                        continue
                    return (f, c)
                else:
                    print("⚠️ Coordenada fuera de rango.")
            except:
                print("⚠️ Formato inválido.")

    def generar_ciudad(self):
        for f in range(1, self.filas - 2, 4):
            for c in range(1, self.columnas - 2, 4):
                if random.random() < 0.85:
                    emoji = random.choice(self.emoji_ciudad)
                    for df in range(2):
                        for dc in range(2):
                            r, col = f + df, c + dc
                            if (r, col) not in [self.entrada, self.salida]:
                                self.tablero[r][col] = emoji

    def mostrar_tablero(self, titulo=""):
        if titulo:
            print(f"\n{titulo}")
        ancho = self.columnas * 3 + 1
        print("╔" + "═" * ancho + "╗")
        for fila in self.tablero:
            fila_str = "║ " + " ".join(fila) + " ║"
            print(fila_str)
        print("╚" + "═" * ancho + "╝\n")

    def agregar_obstaculos(self):
        print(f"📍 Ahora puedes agregar hasta 8 obstáculos ({self.obstaculo}) manualmente.")
        print("Ingresa las coordenadas una por una. Presiona Enter sin escribir nada para terminar.")
        colocados = 0
        while colocados < 8:
            try:
                entrada = input(f"Obstáculo {colocados + 1}/8 (formato: fila,columna): ").strip()
                if not entrada:
                    break
                f, c = map(int, entrada.split(','))
                if not self.es_celda_libre(f, c) or (f, c) in [self.entrada, self.salida]:
                    print("⚠️ Esta celda no está disponible.")
                    continue
                self.tablero[f][c] = self.obstaculo
                colocados += 1
                print(f"✅ Obstáculo colocado en ({f},{c})")
            except:
                print("⚠️ Coordenada inválida.")

    def es_celda_libre(self, fila, col):
        return self.tablero[fila][col] == "◻️"

    def obtener_costo(self, fila, col):
        celda = self.tablero[fila][col]
        if celda == "◻️" or celda == self.salida_emoji:
            return 1
        elif celda in ["🌊", "🕳️"]:
            return 5
        else:
            return float('inf')

class CalculadoraDeRutas:
    def __init__(self, mapa):
        self.mapa = mapa

    def heuristica(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def reconstruir_camino(self, nodo):
        camino = []
        costo_total = 0
        while nodo:
            camino.append(nodo.pos)
            if nodo.padre:
                costo_total += self.mapa.obtener_costo(*nodo.pos)
            nodo = nodo.padre
        return camino[::-1], costo_total

    def a_estrella(self):
        inicio, fin = self.mapa.entrada, self.mapa.salida
        abierto = []
        heapq.heappush(abierto, Nodo(inicio))
        cerrado = set()

        while abierto:
            actual = heapq.heappop(abierto)
            if actual.pos == fin:
                return self.reconstruir_camino(actual)

            cerrado.add(actual.pos)

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                vecino_pos = (actual.pos[0] + dx, actual.pos[1] + dy)
                if not (0 <= vecino_pos[0] < self.mapa.filas) or not (0 <= vecino_pos[1] < self.mapa.columnas):
                    continue
                if self.mapa.obtener_costo(*vecino_pos) == float('inf') or vecino_pos in cerrado:
                    continue

                vecino = Nodo(vecino_pos, actual)
                vecino.g = actual.g + self.mapa.obtener_costo(*vecino.pos)
                vecino.h = self.heuristica(vecino.pos, fin)
                vecino.f = vecino.g + vecino.h

                if any(nodo.pos == vecino.pos and nodo.f <= vecino.f for nodo in abierto):
                    continue

                heapq.heappush(abierto, vecino)
        return None, 0
    
class Nodo:
    def __init__(self, pos, padre=None):
        self.pos = pos
        self.padre = padre
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, otro):
        return self.f < otro.f


# -------------------- EJECUCIÓN --------------------
def main():
    mapa = Mapa()
    mapa.configurar_mapa()
    mapa.generar_ciudad()
    mapa.mostrar_tablero("🗺️ MAPA INICIAL (sin obstáculos):")
    mapa.agregar_obstaculos()

    print("\n🔍 Calculando el camino más corto...")
    calculadora = CalculadoraDeRutas(mapa)
    camino, costo = calculadora.a_estrella()

    if camino:
        for f, c in camino[1:-1]:
            if mapa.tablero[f][c] == "◻️":
                mapa.tablero[f][c] = "🟩"
        print(f"✅ Camino más corto encontrado!")
        print(f"📊 ESTADÍSTICAS DEL CAMINO:")
        print(f"• Longitud: {len(camino)} celdas")
        print(f"• Costo total: {costo} puntos")
    else:
        print("❌ No se encontró un camino posible.")

    mapa.mostrar_tablero("🗺️ MAPA FINAL (con camino óptimo):")

    print("🎯 ¡Mapa completado!")
    print(f"\n📋 LEYENDA:")
    print(f"{mapa.entrada_emoji} = Entrada")
    print(f"{mapa.salida_emoji} = Salida")  
    print(f"🟩 = Camino óptimo")
    print(f"{mapa.obstaculo} = {mapa.tipo_obstaculo.capitalize()}") 
    print(f"🏨🏢🌳 etc. = Edificios")
    print(f"◻️ = Camino libre")
if __name__ == "__main__":
    main()
