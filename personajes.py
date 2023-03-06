import os
import pygame
import sys
from escena import *
from gestorRecursos import *
from pygame.locals import *

VIDA_TOTAL = 5

# Movimientos
QUIETO = 0
IZQUIERDA = 1
DERECHA = 2
ARRIBA = 3
ABAJO = 4
ATACAR_BAGUETTE = 5

# Posturas
SPRITE_QUIETO = 0
SPRITE_ANDANDO = 1
SPRITE_SALTANDO_UP = 2
SPRITE_SALTANDO_DOWN = 3
SPRITE_BAGUETTAZO = 4

# Velocidades de los distintos personajes
VELOCIDAD_JUGADOR = 0.2  # Pixeles por milisegundo
VELOCIDAD_SALTO_JUGADOR = 0.25  # Pixeles por milisegundo
RETARDO_ANIMACION_JUGADOR = 8  # updates que durará cada imagen del personaje
# debería de ser un valor distinto para cada postura

VELOCIDAD_ENEMIGOS = 0.12  # Pixeles por milisegundo
VELOCIDAD_SALTO_ENEMIGOS = 0.27  # Pixeles por milisegundo
RETARDO_ANIMACION_ENEMIGOS = 8  # updates que durará cada imagen del personaje
# debería de ser un valor distinto para cada postura
# El Sniper camina un poco más lento que el jugador, y salta menos

GRAVEDAD = 0.00055  # Píxeles / ms2


class MiSprite(pygame.sprite.Sprite):
    "Los Sprites que tendra este juego"

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.posicion = (0, 0)
        self.velocidad = (0, 0)
        self.scroll = (0, 0)

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
        self.establecerPosicion((posx + incrementox, posy + incrementoy))

    def update(self, tiempo):
        incrementox = self.velocidad[0] * tiempo
        incrementoy = self.velocidad[1] * tiempo
        self.incrementarPosicion((incrementox, incrementoy))


class Personaje(MiSprite):
    "Cualquier personaje del juego"

    # Parametros pasados al constructor de esta clase:
    #  Archivo con la hoja de Sprites
    #  Archivo con las coordenadoas dentro de la hoja
    #  Numero de imagenes en cada postura
    #  Velocidad de caminar y de salto
    #  Retardo para mostrar la animacion del personaje
    def __init__(self, imagen, coordenadas, numImagenes, velocidadCarrera, velocidadSalto, retardoAnimacion):

        # Primero invocamos al constructor de la clase padre
        MiSprite.__init__(self)

        # Se carga la hoja
        self.hoja = GestorRecursos.CargarImagen(imagen, 0)
        self.hoja = self.hoja.convert_alpha()
        # El movimiento que esta realizando
        self.movimiento = QUIETO
        # Lado hacia el que esta mirando
        self.mirando = IZQUIERDA

        # Leemos las coordenadas de un archivo de texto
        datos = GestorRecursos.CargarArchivoCoordenadas(coordenadas)
        datos = datos.split()
        self.numPostura = 1
        self.numImagenPostura = 0
        self.prevPostura = 1
        cont = 0
        self.coordenadasHoja = []
        for linea in range(0, 5):
            self.coordenadasHoja.append([])
            tmp = self.coordenadasHoja[linea]
            for postura in range(1, numImagenes[linea] + 1):
                tmp.append(
                    pygame.Rect((int(datos[cont]), int(datos[cont + 1])), (int(datos[cont + 2]), int(datos[cont + 3]))))
                cont += 4

        # El retardo a la hora de cambiar la imagen del Sprite (para que no se mueva demasiado rápido)
        self.retardoMovimiento = 0

        # En que postura esta inicialmente
        self.numPostura = QUIETO

        # El rectangulo del Sprite
        self.rect = pygame.Rect(100, 100, self.coordenadasHoja[self.numPostura][self.numImagenPostura][2],
                                self.coordenadasHoja[self.numPostura][self.numImagenPostura][3])

        # Las velocidades de caminar y salto
        self.velocidadCarrera = velocidadCarrera
        self.velocidadSalto = velocidadSalto

        # El retardo en la animacion del personaje (podria y deberia ser distinto para cada postura)
        self.retardoAnimacion = retardoAnimacion

        # Y actualizamos la postura del Sprite inicial, llamando al metodo correspondiente
        self.actualizarPostura()

    # Metodo base para realizar el movimiento: simplemente se le indica cual va a hacer, y lo almacena
    def mover(self, movimiento):
            if movimiento == ARRIBA or movimiento == ATACAR_BAGUETTE:
                # Si estamos en el aire y el personaje quiere saltar, ignoramos este movimiento
                if self.numPostura == SPRITE_SALTANDO_UP or self.numPostura == SPRITE_SALTANDO_DOWN:
                    self.movimiento = QUIETO
                    self.atacando = False
                else:
                    self.movimiento = movimiento
            else:
                self.movimiento = movimiento
            

    def actualizarPostura(self):
        self.retardoMovimiento -= 1
        # Miramos si ha pasado el retardo para dibujar una nueva postura
        if self.retardoMovimiento < 0:
            self.retardoMovimiento = self.retardoAnimacion
            # Si ha pasado, actualizamos la postura
            self.numImagenPostura += 1
            if self.numImagenPostura >= len(self.coordenadasHoja[self.numPostura]) or self.numPostura != self.prevPostura:
                self.numImagenPostura = 0
            if self.numImagenPostura < 0:
                self.numImagenPostura = len(self.coordenadasHoja[self.numPostura]) - 1
            self.image = self.hoja.subsurface(self.coordenadasHoja[self.numPostura][self.numImagenPostura])

            # Si esta mirando a la izquiera, cogemos la porcion de la hoja
            if self.mirando == DERECHA:
                self.image = self.hoja.subsurface(self.coordenadasHoja[self.numPostura][self.numImagenPostura])
            #  Si no, si mira a la derecha, invertimos esa imagen
            elif self.mirando == IZQUIERDA:
                self.image = pygame.transform.flip(
                    self.hoja.subsurface(self.coordenadasHoja[self.numPostura][self.numImagenPostura]), 1, 0)
        self.prevPostura = self.numPostura

    def update(self, grupoPlataformas, tiempo):

        # Las velocidades a las que iba hasta este momento
        (velocidadx, velocidady) = self.velocidad

        # Si vamos a la izquierda o a la derecha
        if (self.movimiento == IZQUIERDA) or (self.movimiento == DERECHA):
            # Esta mirando hacia ese lado
            self.mirando = self.movimiento

            # Si vamos a la izquierda, le ponemos velocidad en esa dirección
            if self.movimiento == IZQUIERDA:
                velocidadx = -self.velocidadCarrera
            # Si vamos a la derecha, le ponemos velocidad en esa dirección
            else:
                velocidadx = self.velocidadCarrera

            # Si no estamos en el aire
            if self.numPostura != SPRITE_SALTANDO_UP:
                # La postura actual sera estar caminando
                self.numPostura = SPRITE_ANDANDO
                # Ademas, si no estamos encima de ninguna plataforma, caeremos
                if pygame.sprite.spritecollideany(self, grupoPlataformas) is None:
                    self.numPostura = SPRITE_SALTANDO_UP

        # Si queremos saltar
        elif self.movimiento == ARRIBA:
            # La postura actual sera estar saltando
            self.numPostura = SPRITE_SALTANDO_UP
            # Le imprimimos una velocidad en el eje y
            velocidady = -self.velocidadSalto

        # Si queremos atacar
        elif self.movimiento == ATACAR_BAGUETTE:
            self.numPostura = SPRITE_BAGUETTAZO
            if self.numImagenPostura >= 4 and self.prevPostura == SPRITE_BAGUETTAZO:
                self.atacando = False
                self.movimiento = QUIETO

        # Si no se ha pulsado ninguna tecla
        elif self.movimiento == QUIETO:
            # Si no estamos saltando, la postura actual será estar quieto
            if not self.numPostura == SPRITE_SALTANDO_UP:
                self.numPostura = SPRITE_QUIETO
            velocidadx = 0

        # Además, si estamos en el aire
        if self.numPostura == SPRITE_SALTANDO_UP:

            # Miramos a ver si hay que parar de caer: si hemos llegado a una plataforma
            #  Para ello, miramos si hay colision con alguna plataforma del grupo
            plataforma = pygame.sprite.spritecollideany(self, grupoPlataformas)
            #  Ademas, esa colision solo nos interesa cuando estamos cayendo
            #  y solo es efectiva cuando caemos encima, no de lado, es decir,
            #  cuando nuestra posicion inferior esta por encima de la parte de abajo de la plataforma
            if (plataforma is not None) and (velocidady > 0) and (plataforma.rect.bottom > self.rect.bottom):
                # Lo situamos con la parte de abajo un pixel colisionando con la plataforma
                #  para poder detectar cuando se cae de ella
                self.establecerPosicion((self.posicion[0], plataforma.posicion[1] - plataforma.rect.height + 1))
                # Lo ponemos como quieto
                self.numPostura = SPRITE_QUIETO
                # Y estará quieto en el eje y
                velocidady = 0

            # Si no caemos en una plataforma, aplicamos el efecto de la gravedad
            else:
                velocidady += GRAVEDAD * tiempo

        # Actualizamos la imagen a mostrar
        self.actualizarPostura()

        # Aplicamos la velocidad en cada eje
        self.velocidad = (velocidadx, velocidady)

        # Y llamamos al método de la superclase para que, según la velocidad y el tiempo
        #  calcule la nueva posición del Sprite
        MiSprite.update(self, tiempo)

        return


# ----------------------------------------- Jugador y No Jugador -------------------------------------------------------

class Jugador(Personaje):
    "Cualquier personaje del juego"

    def __init__(self):
        # Invocamos al constructor de la clase padre con la configuracion de este personaje concreto
        Personaje.__init__(self, 'francois_with_hit.png', 'coordJugador.txt', [3, 6, 1, 1, 5], VELOCIDAD_JUGADOR,
                           VELOCIDAD_SALTO_JUGADOR, RETARDO_ANIMACION_JUGADOR)
        
        self.vida = VIDA_TOTAL
        self.atacando = False
        self.cooldownBaguette = 0

    def mover(self, teclasPulsadas, arriba, abajo, izquierda, derecha, ataque):
        # Indicamos la acción a realizar segun la tecla pulsada para el jugador
        if self.atacando == False:
            if teclasPulsadas[arriba]:
                Personaje.mover(self, ARRIBA)
            elif teclasPulsadas[izquierda]:
                Personaje.mover(self, IZQUIERDA)
            elif teclasPulsadas[derecha]:
                Personaje.mover(self, DERECHA)
            elif teclasPulsadas[ataque]:
                if self.cooldownBaguette <= 0:
                    self.atacar()
                    Personaje.mover(self, ATACAR_BAGUETTE)
            else:
                Personaje.mover(self, QUIETO)

        # Reduccion en el cooldown desde el ultimo ataque        
        if self.cooldownBaguette > 0:
            self.cooldownBaguette -= 1

    def atacar(self):
        self.atacando = True
        self.cooldownBaguette = 70
        # Rectangulo colision de ataque
        #rect_ataque = pygame.Rect(self.rect.centerx, self.rect.y, 1.5 * self.rect.width, self.rect.height)


class NoJugador(Personaje):
    "El resto de personajes no jugadores"

    def __init__(self, imagen, coordenadas, numImagenes, velocidad, velocidadSalto, retardoAnimacion):
        # Primero invocamos al constructor de la clase padre con los parametros pasados
        Personaje.__init__(self, imagen, coordenadas, numImagenes, velocidad, velocidadSalto, retardoAnimacion)

    def mover_cpu(self, jugador):
        if jugador.posicion[0] < self.posicion[0]:
            self.mirando = IZQUIERDA
        else:
            self.mirando = DERECHA


# -------------------------------------------- Enemigos y NPCs ---------------------------------------------------------
# Clase para enemigo concreto

"""class Sniper(NoJugador):
    "El enemigo 'Sniper'"

    def __init__(self):
        # Invocamos al constructor de la clase padre con la configuracion de este personaje concreto
        NoJugador.__init__(self, 'Sniper.png', 'coordSniper.txt', [5, 10, 6], VELOCIDAD_ENEMIGOS, VELOCIDAD_SALTO_ENEMIGOS,
                           RETARDO_ANIMACION_ENEMIGOS);

    # Aqui vendria la implementacion de la IA segun las posiciones de los jugadores
    # La implementacion de la inteligencia segun este personaje particular
    def mover_cpu(self, jugador1):

        # Movemos solo a los enemigos que esten en la pantalla
        if self.rect.left > 0 and self.rect.right < ANCHO_PANTALLA and self.rect.bottom > 0 and self.rect.top < ALTO_PANTALLA:

            if jugador1.posicion[0] < self.posicion[0]:
                Personaje.mover(self, IZQUIERDA)
            else:
                Personaje.mover(self, DERECHA)

        # Si este personaje no esta en pantalla, no hara nada
        else:
            Personaje.mover(self, QUIETO)"""""


class Tomate(NoJugador):

    def __init__(self):
        NoJugador.__init__(self, 'Tomato-Sheet.png', 'coordTomato.txt', [8, 8, 2, 13, 0],VELOCIDAD_ENEMIGOS,VELOCIDAD_SALTO_ENEMIGOS,RETARDO_ANIMACION_ENEMIGOS)

    def mover_cpu(self, jugador):

        # Movemos solo a los enemigos que esten en la pantalla
        if self.rect.left > 0 and self.rect.right < ANCHO_PANTALLA and self.rect.bottom > 0 and self.rect.top < ALTO_PANTALLA:

            if jugador.posicion[0] < self.posicion[0]:
                #Personaje.mover(self, IZQUIERDA)
                self.mirando = DERECHA
            else:
                #Personaje.mover(self, DERECHA)
                self.mirando = IZQUIERDA

        # Si este personaje no esta en pantalla, no hara nada
        else:
            Personaje.mover(self, QUIETO)


class Zanahoria(NoJugador):

    def __init__(self):
        NoJugador.__init__(self, 'Carrot-sheet.png', 'coordCarrot.txt', [6,2,7,0,0],VELOCIDAD_ENEMIGOS,VELOCIDAD_SALTO_ENEMIGOS,RETARDO_ANIMACION_ENEMIGOS)

    def mover_cpu(self, jugador):

        # Movemos solo a los enemigos que esten en la pantalla
        if self.rect.left > 0 and self.rect.right < ANCHO_PANTALLA and self.rect.bottom > 0 and self.rect.top < ALTO_PANTALLA:

            if jugador.posicion[0] < self.posicion[0]:
                #Personaje.mover(self, IZQUIERDA)
                self.mirando = DERECHA
            else:
                #Personaje.mover(self, DERECHA)
                self.mirando = IZQUIERDA

        # Si este personaje no esta en pantalla, no hara nada
        else:
            Personaje.mover(self, QUIETO)


class Madre(NoJugador):
    def __init__(self):
        NoJugador.__init__(self, 'Madre-sheet.png', 'coordMadre.txt', [8, 0, 0, 0, 0], VELOCIDAD_ENEMIGOS,
                           VELOCIDAD_SALTO_ENEMIGOS, RETARDO_ANIMACION_ENEMIGOS)

    def mover_cpu(self, jugador):
        if jugador.posicion[0] < self.posicion[0]:
            self.mirando = IZQUIERDA
        else:
            self.mirando = DERECHA
