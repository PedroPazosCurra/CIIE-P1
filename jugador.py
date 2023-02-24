import os
import pygame
import sys
import gestorRecursos
from gestorRecursos import *
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
        self.posicion = (0, 0)
        self.scroll = (0, 0)
        """
        self.posicionx = 300
        self.posiciony = 300
        self.rect.left = self.posicionx
        self.rect.bottom = self.posiciony
        """
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

    def establecerPosicion(self, posicion):
        self.posicion = posicion
        self.rect.left = self.posicion[0] - self.scroll[0]
        self.rect.bottom = self.posicion[1] - self.scroll[1]

    def establecerPosicionPantalla(self, scrollDecorado):
        self.scroll = scrollDecorado
        (scrollx, scrolly) = self.scroll
        (posx, posy) = self.posicion
        self.rect.left = posx - scrollx
        self.rect.bottom = posy - scrolly
    
    def incrementarPosicion(self, incremento):
        (posx, posy) = self.posicion
        (incrementox, incrementoy) = incremento
        self.estableceerPosicion((posx+incrementox, posy+incrementoy))

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
            self.establecerPosicion((self.posicion[0] - VELOCIDAD_JUGADOR * tiempo, self.posicion[1]))
            """
            self.posicionx -= VELOCIDAD_JUGADOR * tiempo
            self.rect.left = self.posicionx
            """
        # Si vamos a la derecha
        elif self.movimiento == DERECHA:
            # Si no estamos en el aire, la postura actual sera estar caminando
            if not self.numPostura == SPRITE_SALTANDO_UP and not self.numPostura == SPRITE_SALTANDO_DOWN:
                self.numPostura = SPRITE_ANDANDO
            # Esta mirando a la derecha
            self.mirando = DERECHA
            # Actualizamos la posicion
            self.establecerPosicion((self.posicion[0] + VELOCIDAD_JUGADOR * tiempo, self.posicion[1]))
            """
            self.posicionx += VELOCIDAD_JUGADOR * tiempo
            self.rect.left = self.posicionx
            """

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
            self.establecerPosicion((self.posicion[0], self.posicion[1] - self.velocidady * tiempo))
            """
            self.posiciony -= self.velocidady * tiempo
            """

            if self.velocidady < 0:
                self.numPostura = SPRITE_SALTANDO_DOWN
            else:
                self.numPostura = SPRITE_SALTANDO_UP

            # Si llegamos a la posicion inferior, paramos de caer y lo ponemos como quieto
            if self.posicion[1]>300:
                self.numPostura = SPRITE_QUIETO
                self.establecerPosicion((self.posicion[0],300))
                self.velocidady = 0
            # Si no, aplicamos el efecto de la gravedad
            else:
                self.velocidady -= 0.004
            """
            if self.posiciony>300:
                self.numPostura = SPRITE_QUIETO
                self.posiciony = 300
                self.velovidady = 0
            # Si no, aplicamos el efecto de la gravedad
            else:
                self.velocidady -= 0.004
            """

        # Actualizamos la imagen a mostrar
        self.actualizarPostura()
        return
