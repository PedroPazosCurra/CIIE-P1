import os
import pygame
import sys
from pygame.locals import *

QUIETO = 0
IZQUIERDA = 1
DERECHA = 2

#Posturas
ANDANDO = 1

VELOCIDAD_JUGADOR = 0.2 # Pixeles por milisegundo
RETARDO_ANIMACION_JUGADOR = 15  # updates que durará cada imagen del personaje
                                # debería de ser un valor distinto para cada postura

# -------------------------------------------------
# Funciones auxiliares
# -------------------------------------------------

# El colorkey es es color que indicara la transparencia
# -1 es 0,0
def load_image(name, colorkey=-1):

    fullname = os.path.join('imagenes', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', fullname)
        raise SystemExit(message)
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image


# -------------------------------------------------
# Clases de los objetos del juego
# -------------------------------------------------

class Jugador(pygame.sprite.Sprite):

    def __init__(self):

        # Primero invocamos al constructor de la clase padre
        pygame.sprite.Sprite.__init__(self)

        # Se carga la hoja
        self.hoja = load_image('Chef.png', -1)
        self.hoja = self.hoja.convert_alpha()

        # El movimiento que esta realizando
        self.movimiento = QUIETO

        # Lado hacia el que esta mirando
        self.mirando = DERECHA

        # Leemos las coordenadas de un archivo de texto
        pfile = open('imagenes/coordJugador.txt', 'r')
        datos = pfile.read()
        pfile.close()
        datos = datos.split()
        self.numPostura = 1
        self.numImagenPostura = 0
        cont = 0
        numImagenes = [3,6]
        self.coordenadasHoja = []
        for linea in range(0, 2):
            self.coordenadasHoja.append([])
            tmp = self.coordenadasHoja[linea]
            for postura in range(1, numImagenes[linea] + 1):
                tmp.append(
                    pygame.Rect((int(datos[cont]), int(datos[cont + 1])), (int(datos[cont + 2]), int(datos[cont + 3]))))
                cont += 4

        # El retardo a la hora de cambiar la imagen del Sprite (para que no se mueva demasiado rápido)
        self.retardoMovimiento = 0

        # La posicion inicial del Sprite
        self.rect = pygame.Rect(100,100,self.coordenadasHoja[self.numPostura][self.numImagenPostura][2],self.coordenadasHoja[self.numPostura][self.numImagenPostura][3])

        # La posicion x que ocupa
        self.posicionx = 300
        self.rect.left = self.posicionx

        # Y actualizamos la postura del Sprite inicial, llamando al metodo correspondiente
        self.actualizarPostura()

    def actualizarPostura(self):
        self.retardoMovimiento -= 1
        # Miramos si ha pasado el retardo para dibujar una nueva postura
        if self.retardoMovimiento < 0:
            self.retardoMovimiento = RETARDO_ANIMACION_JUGADOR
            # Si ha pasado, actualizamos la postura
            self.numImagenPostura += 1
            if self.numImagenPostura >= len(self.coordenadasHoja[self.numPostura]):
                self.numImagenPostura = 0
            if self.numImagenPostura < 0:
                self.numImagenPostura = len(self.coordenadasHoja[self.numPostura])-1
            self.image = self.hoja.subsurface(self.coordenadasHoja[self.numPostura][self.numImagenPostura])

            # Si esta mirando a la izquiera, cogemos la porcion de la hoja
            if self.mirando == DERECHA:
                self.image = self.hoja.subsurface(self.coordenadasHoja[self.numPostura][self.numImagenPostura])
            #  Si no, si mira a la derecha, invertimos esa imagen
            elif self.mirando == IZQUIERDA:
                self.image = pygame.transform.flip(self.hoja.subsurface(self.coordenadasHoja[self.numPostura][self.numImagenPostura]), 1, 0)

    def mover(self, direccion):
        # Almacenamos el movimiento realizado
        self.movimiento = direccion

    def update(self, tiempo):
        # Si vamos a la izquierda
        if self.movimiento == IZQUIERDA:
            # La postura actual sera estar caminando
            self.numPostura = ANDANDO
            # Esta mirando a la izquierda
            self.mirando = IZQUIERDA
            # Actualizamos la posicion
            self.posicionx -= VELOCIDAD_JUGADOR * tiempo
            self.rect.left = self.posicionx
            # Actualizamos la imagen a mostrar
            self.actualizarPostura()
        # Si vamos a la derecha
        elif self.movimiento == DERECHA:
            # La postura actual sera estar caminando
            self.numPostura = ANDANDO
            # Esta mirando a la derecha
            self.mirando = DERECHA
            # Actualizamos la posicion
            self.posicionx += VELOCIDAD_JUGADOR * tiempo
            self.rect.left = self.posicionx
            # Actualizamos la imagen a mostrar
            self.actualizarPostura()
        else:
            # La postura actual será estar quieto
            self.numPostura = QUIETO
            # Actualizamos la imagen a mostrar
            self.actualizarPostura()
        return

# -------------------------------------------------
# Funcion principal del juego
# -------------------------------------------------

def main():

    # Inicializar pygame
    pygame.init()

    # Crear la pantalla
    pantalla = pygame.display.set_mode((800, 600), 0, 32)

    # Creamos el objeto reloj para sincronizar el juego
    reloj = pygame.time.Clock()

    # Poner el título de la ventana
    pygame.display.set_caption('Juego panadero')

    # Creamos el jugador
    jugador = Jugador()

    # Creamos el grupo de Sprites de jugadores
    grupoJugadores = pygame.sprite.Group(jugador)

    # El bucle de eventos
    while True:

        # Hacemos que el reloj espere a un determinado fps
        tiempo_pasado = reloj.tick(60)

        # Para cada evento, hacemos
        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # Miramos que teclas se han pulsado
        teclasPulsadas = pygame.key.get_pressed()

        # Si la tecla es Escape
        if teclasPulsadas[K_ESCAPE]:
            # Se sale del programa
            pygame.quit()
            sys.exit()

        # Indicamos la acción a realizar segun la tecla pulsada para el jugador 1
        if teclasPulsadas[K_LEFT]:
            jugador.mover(IZQUIERDA)
        elif teclasPulsadas[K_RIGHT]:
            jugador.mover(DERECHA)
        else:
            jugador.mover(QUIETO)

        # Actualizamos el jugador
        jugador.update(tiempo_pasado)

        # Dibujar el fondo de color
        pantalla.fill((255, 255, 255))

        # Dibujar el grupo de Sprites
        grupoJugadores.draw(pantalla)

        # Actualizar la pantalla
        pygame.display.update()


if __name__ == "__main__":
    main()