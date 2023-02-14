import os
import pygame
import sys
from pygame.locals import *

QUIETO = 0
IZQUIERDA = 1
DERECHA = 2
ARRIBA = 3
ABAJO = 4

#Posturas
SPRITE_QUIETO = 0
SPRITE_ANDANDO = 1
SPRITE_SALTANDO_UP = 2
SPRITE_SALTANDO_DOWN = 3

VELOCIDAD_JUGADOR = 0.2 # Pixeles por milisegundo
VELOCIDAD_SALTO_JUGADOR = 0.25 # Pixeles por milisegundo
RETARDO_ANIMACION_JUGADOR = 8  # updates que durará cada imagen del personaje
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
# -------------------------------------------------
# Clase GestorRecursos

# En este caso se implementa como una clase vacía, solo con métodos de clase
class GestorRecursos(object):
    recursos = {}

    @classmethod
    def CargarImagen(cls, nombre, colorkey=None):
        # Si el nombre de archivo está entre los recursos ya cargados
        if nombre in cls.recursos:
            # Se devuelve ese recurso
            return cls.recursos[nombre]
        # Si no ha sido cargado anteriormente
        else:
            # Se carga la imagen indicando la carpeta en la que está
            fullname = os.path.join('imagenes', nombre)
            try:
                imagen = pygame.image.load(fullname)
            except pygame.error as message:
                print('Cannot load image:', fullname)
                raise SystemExit(message)
            imagen = imagen.convert()
            if colorkey is not None:
                if colorkey is -1:
                    colorkey = imagen.get_at((0, 0))
                imagen.set_colorkey(colorkey, RLEACCEL)
            # Se almacena
            cls.recursos[nombre] = imagen
            # Se devuelve
            return imagen

    @classmethod
    def CargarArchivoCoordenadas(cls, nombre):
        # Si el nombre de archivo está entre los recursos ya cargados
        if nombre in cls.recursos:
            # Se devuelve ese recurso
            return cls.recursos[nombre]
        # Si no ha sido cargado anteriormente
        else:
            # Se carga el recurso indicando el nombre de su carpeta
            fullname = os.path.join('imagenes', nombre)
            pfile = open(fullname, 'r')
            datos = pfile.read()
            pfile.close()
            # Se almacena
            cls.recursos[nombre] = datos
            # Se devuelve
            return datos


class Jugador(pygame.sprite.Sprite):

    def __init__(self):

        # Primero invocamos al constructor de la clase padre
        pygame.sprite.Sprite.__init__(self)

        # Se carga la hoja
        self.hoja = GestorRecursos.CargarImagen('francois_base.png', -1)
        self.hoja = self.hoja.convert_alpha()

        # El movimiento que esta realizando
        self.movimiento = QUIETO

        # Lado hacia el que esta mirando
        self.mirando = DERECHA

        # Leemos las coordenadas de un archivo de texto
        datos = GestorRecursos.CargarArchivoCoordenadas('coordJugador.txt')
        datos = datos.split()
        self.numPostura = 1
        self.numImagenPostura = 0
        cont = 0
        numImagenes = [3,6,1,1]       # Quieto, Andar, Saltar, Caer
        self.coordenadasHoja = []
        for linea in range(0, 4):
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

        # La posicion x e y que ocupa
        self.posicionx = 300
        self.posiciony = 300
        self.rect.left = self.posicionx
        self.rect.bottom = self.posiciony
        # Velocidad en el eje y (para los saltos)
        #  En el eje x se utilizaria si hubiese algun tipo de inercia
        self.velocidady = 0

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

    def mover(self,teclasPulsadas, arriba, abajo, izquierda, derecha):

        # Indicamos la acción a realizar segun la tecla pulsada para el jugador
        if teclasPulsadas[arriba]:
            # Si estamos en el aire y han pulsado arriba, ignoramos este movimiento
            if self.numPostura == SPRITE_SALTANDO_UP or self.numPostura == SPRITE_SALTANDO_DOWN:
                self.movimiento = QUIETO
            else:
                self.movimiento = ARRIBA
        elif teclasPulsadas[izquierda]:
            self.movimiento = IZQUIERDA
        elif teclasPulsadas[derecha]:
            self.movimiento = DERECHA
        else:
            self.movimiento = QUIETO

    def update(self, tiempo):
        # Si vamos a la izquierda
        if self.movimiento == IZQUIERDA:
            # Si no estamos en el aire, la postura actual sera estar caminando
            if not self.numPostura == SPRITE_SALTANDO_UP and not self.numPostura == SPRITE_SALTANDO_DOWN:
                self.numPostura = SPRITE_ANDANDO
            # Esta mirando a la izquierda
            self.mirando = IZQUIERDA
            # Actualizamos la posicion
            self.posicionx -= VELOCIDAD_JUGADOR * tiempo
            self.rect.left = self.posicionx
        # Si vamos a la derecha
        elif self.movimiento == DERECHA:
            # Si no estamos en el aire, la postura actual sera estar caminando
            if not self.numPostura == SPRITE_SALTANDO_UP and not self.numPostura == SPRITE_SALTANDO_DOWN:
                self.numPostura = SPRITE_ANDANDO
            # Esta mirando a la derecha
            self.mirando = DERECHA
            # Actualizamos la posicion
            self.posicionx += VELOCIDAD_JUGADOR * tiempo
            self.rect.left = self.posicionx

        # Si estamos saltando
        elif self.movimiento == ARRIBA:
            # La postura actual sera estar saltando
            self.numPostura = SPRITE_SALTANDO_UP
            # Le imprimimos una velocidad en el eje y
            self.velocidady = VELOCIDAD_SALTO_JUGADOR
        # Si no se ha pulsado ninguna tecla
        elif self.movimiento == QUIETO:
            # Si no estamos saltando, la postura actual será estar quieto
            if not self.numPostura == SPRITE_SALTANDO_UP and not self.numPostura == SPRITE_SALTANDO_DOWN:
                self.numPostura = SPRITE_QUIETO

        # Si estamos en el aire
        if self.numPostura == SPRITE_SALTANDO_UP or self.numPostura == SPRITE_SALTANDO_DOWN:
            # Actualizamos la posicion
            self.posiciony -= self.velocidady * tiempo

            if self.velocidady < 0:
                self.numPostura = SPRITE_SALTANDO_DOWN
            else:
                self.numPostura = SPRITE_SALTANDO_UP

            # Si llegamos a la posicion inferior, paramos de caer y lo ponemos como quieto
            if self.posiciony>300:
                self.numPostura = SPRITE_QUIETO
                self.posiciony = 300
                self.velovidady = 0
            # Si no, aplicamos el efecto de la gravedad
            else:
                self.velocidady -= 0.004

            # Nos ponemos en esa posicion en el eje y
            self.rect.bottom = self.posiciony

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

        # Acciones según teclas
        jugador.mover(teclasPulsadas, K_UP, K_DOWN, K_LEFT, K_RIGHT)

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
