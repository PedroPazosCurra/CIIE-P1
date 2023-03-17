
from pygame.locals import *

from escena import *
from gestorRecursos import GestorRecursos

VIDA_JUGADOR = 5
VIDA_ZANAHORIA = 3
VIDA_TOMATE = 1
VIDA_NPC = 999
VIDA_BOSS = 10
INVENCIBILITY_FRAMES = 80

# Movimientos
QUIETO = 0
IZQUIERDA = 1
DERECHA = 2
ARRIBA = 3
ABAJO = 4
ATACAR_BAGUETTE = 5
DISPARO = 6
DISPARO_CERTERO = 7

# Posturas
SPRITE_QUIETO = 0
SPRITE_ANDANDO = 1
SPRITE_SALTANDO_UP = 2
SPRITE_SALTANDO_DOWN = 3
SPRITE_BAGUETTAZO = 4
SPRITE_DISPARANDO = 5

# Velocidades de los distintos personajes
VELOCIDAD_JUGADOR = 0.2  # Pixeles por milisegundo
VELOCIDAD_SALTO_JUGADOR = 0.25  # Pixeles por milisegundo
RETARDO_ANIMACION_JUGADOR = 8  # updates que durará cada imagen del personaje
# debería de ser un valor distinto para cada postura

# Movimientos Especiales Proyectiles

VELOCIDAD_ENEMIGOS = 0.06  # Pixeles por milisegundo
VELOCIDAD_SALTO_ENEMIGOS = 0.27  # Pixeles por milisegundo
RETARDO_ANIMACION_ENEMIGOS = 8  # updates que durará cada imagen del personaje
# debería de ser un valor distinto para cada postura
# El Sniper camina un poco más lento que el jugador, y salta menos
VELOCIDAD_BOSS = 0.01

VELOCIDAD_CROISSANT = 0.12

GRAVEDAD = 0.00055  # Píxeles / ms2


class MiSprite(pygame.sprite.Sprite):
    """Clase que engloba a todos los sprites del juego"""

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
    """Cualquier personaje del juego"""

    # Parametros pasados al constructor de esta clase:
    #  Archivo con la hoja de Sprites
    #  Archivo con las coordenadoas dentro de la hoja
    #  Numero de imagenes en cada postura
    #  Velocidad de caminar y de salto
    #  Retardo para mostrar la animacion del personaje
    def __init__(self, imagen, coordenadas, numImagenes, velocidadCarrera, velocidadSalto, retardoAnimacion, vida):
        # Primero invocamos al constructor de la clase padre
        MiSprite.__init__(self)

        # Se carga la hoja
        self.atacando = False
        self.hoja = GestorRecursos.CargarImagen(imagen, 0)
        self.hoja = self.hoja.convert()
        # El movimiento que esta realizando
        self.movimiento = QUIETO
        # Movimiento extra -> Permite desplazarse a la vez que se salta
        self.movimiento_extra = None
        # Lado hacia el que esta mirando
        self.mirando = IZQUIERDA

        self.vida = vida

        # Leemos las coordenadas de un archivo de texto
        datos = GestorRecursos.CargarArchivoCoordenadas(coordenadas)
        datos = datos.split()
        self.numPostura = 1
        self.numImagenPostura = 0
        self.prevPostura = 1
        cont = 0
        self.coordenadasHoja = []

        for linea in range(0, 6):
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

        # Cooldown de daño (frames de invencibilidad)
        self.cooldownDano = 0

        # Y actualizamos la postura del Sprite inicial, llamando al metodo correspondiente
        self.actualizarPostura()

    # Metodo base para realizar el movimiento: simplemente se le indica cual va a hacer, y lo almacena
    def mover(self, movimiento):	
        if movimiento == ARRIBA or movimiento == ATACAR_BAGUETTE or movimiento == DISPARO:
            # Si estamos en el aire y el personaje quiere saltar, ignoramos este movimiento
            if self.numPostura == SPRITE_SALTANDO_UP or self.numPostura == SPRITE_SALTANDO_DOWN:
                self.movimiento = QUIETO
            else:
                self.movimiento = movimiento
        elif self.movimiento == ARRIBA and movimiento != QUIETO:
            self.movimiento_extra = movimiento
        else:
            self.movimiento = movimiento
            self.movimiento_extra = None

    def actualizarPostura(self):
        cambiarImagen = False
        self.retardoMovimiento -= 1
        
        # Comprobamos si hay que reiniciar self.numImagenPostura porque hemos cambiado de postura
        if self.prevPostura != self.numPostura:
            cambiarImagen = True
            self.numImagenPostura = 0
        
        # Miramos si ha pasado el retardo para dibujar una nueva imagen de la postura actual
        elif self.retardoMovimiento < 0:
            cambiarImagen = True
            
            # Si ha pasado, actualizamos la postura
            self.numImagenPostura += 1
            if self.numImagenPostura >= len(self.coordenadasHoja[self.numPostura]) or self.numPostura != self.prevPostura:
                self.numImagenPostura = 0
            if self.numImagenPostura < 0:
                self.numImagenPostura = len(self.coordenadasHoja[self.numPostura]) - 1
        
        # Modificar la imagen a mostrar si el contador de retardo ha llegado a 0 o si se ha cambiado la postura
        if cambiarImagen:
            # El retardo se reinicia tanto si ha llegado a 0 como si se ha cambiado de postura
            self.retardoMovimiento = self.retardoAnimacion

            # Si esta mirando a la izquierda, cogemos la porcion de la hoja
            if self.mirando == DERECHA:
                self.image = self.hoja.subsurface(self.coordenadasHoja[self.numPostura][self.numImagenPostura])
            #  Si no, si mira a la derecha, invertimos esa imagen
            elif self.mirando == IZQUIERDA:
                self.image = pygame.transform.flip(self.hoja.subsurface(self.coordenadasHoja[self.numPostura][self.numImagenPostura]), True, False)
        
            # Actualizamos el tamaño del rect para que coincida con la imagen actual
            self.rect.size = (self.coordenadasHoja[self.numPostura][self.numImagenPostura][2],
                              self.coordenadasHoja[self.numPostura][self.numImagenPostura][3])
        
        self.prevPostura = self.numPostura

    def update(self, tiempo, grupos):

        grupoPlataformas = grupos[0]
        grupoObstaculos = grupos[1]

        # Comprobamos si el coolDown para ser golpeado debe descontarse
        if self.cooldownDano > 0:
            self.cooldownDano -= 1

        self.atacando = self.movimiento == ATACAR_BAGUETTE or self.movimiento == DISPARO

        # Las velocidades a las que iba hasta este momento
        (velocidadx, velocidady) = self.velocidad

        # Si vamos a la izquierda o a la derecha
        if (self.movimiento == IZQUIERDA) or (self.movimiento == DERECHA):
            velocidadx = self.desplHorizontal(self.movimiento, grupoObstaculos)
            
            # Si no estamos en el aire
            if self.numPostura != SPRITE_SALTANDO_UP:
                # La postura actual sera estar caminando
                self.numPostura = SPRITE_ANDANDO
                # Ademas, si no estamos encima de ninguna plataforma, caeremos
                if pygame.sprite.spritecollideany(self, grupoPlataformas) is None:
                    self.numPostura = SPRITE_SALTANDO_UP

        # Si queremos saltar
        elif self.movimiento == ARRIBA:

            if (self.movimiento_extra == IZQUIERDA) or (self.movimiento_extra == DERECHA):
                velocidadx = self.desplHorizontal(self.movimiento_extra, grupoObstaculos)
            
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

        # Si queremos disparar
        elif self.movimiento == DISPARO:
            self.numPostura = SPRITE_DISPARANDO
            if self.numImagenPostura >= 2 and self.prevPostura == SPRITE_DISPARANDO:
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

    def desplHorizontal(self, movimiento, grupoObstaculos):
        self.mirando = movimiento

        # Si vamos a la izquierda, le ponemos velocidad en esa dirección
        if self.movimiento == IZQUIERDA:
            if pygame.sprite.spritecollideany(self, grupoObstaculos) is None:
                return -self.velocidadCarrera
            else:
                return 0

        # Si vamos a la derecha, le ponemos velocidad en esa dirección
        else:
            if pygame.sprite.spritecollideany(self, grupoObstaculos) is None:
                return self.velocidadCarrera
            else:
                return 0

    # Quita vida solo si no hay frames de invencibilidad
    def quitar_vida(self):
        if self.cooldownDano <= 0:
            self.cooldownDano = INVENCIBILITY_FRAMES
            self.vida -= 1
            return True
        else:
            return False

    def muerto(self):
        return self.vida < 1


class Tarta(MiSprite):
    """Objeto de vida"""
    def __init__(self):
        MiSprite.__init__(self)
        self.image = GestorRecursos.CargarImagen('PiePumpkin.png', 0).convert_alpha()
        self.rect = self.image.get_rect()


# ----------------------------------------- Jugador y No Jugador -------------------------------------------------------

class Jugador(Personaje):
    """Cualquier personaje del juego"""

    def __init__(self):
        # Invocamos al constructor de la clase padre con la configuracion de este personaje concreto
        Personaje.__init__(self, 'francois_with_hit.png', 'coordJugador.txt', [3, 6, 1, 1, 5, 4], VELOCIDAD_JUGADOR,
                           VELOCIDAD_SALTO_JUGADOR, RETARDO_ANIMACION_JUGADOR, VIDA_JUGADOR)

        self.hitbox_baguette = Hitbox([self.rect.centerx, self.rect.y, self.rect.width * 1.7, self.rect.height])
        # self.atacando = False
        self.cooldownBaguette = 0
        self.cooldownCroissant = 0
        self.max_vida = self.vida  # Jugador puede recuperar vida asi que ponemos un tope máximo
        self.vida_display = None
        self.animacionAcabada = True
        self.croissants = None
        self.usoCroissant = False

    def establecerCroissants(self, croissants):
        self.croissants = croissants

    def mover(self, teclasPulsadas, arriba, abajo, izquierda, derecha, ataque, disparo):
        # Indicamos la acción a realizar segun la tecla pulsada para el jugador

        if teclasPulsadas[arriba]:
            Personaje.mover(self, ARRIBA)

            # Movimiento extra -> Desplazarse a la vez que se salta
            if teclasPulsadas[izquierda]:
                Personaje.mover(self, IZQUIERDA)
            elif teclasPulsadas[derecha]:
                Personaje.mover(self, DERECHA)
            elif teclasPulsadas[disparo]:
                if self.cooldownCroissant <= 0:
                    self.disparar()
                    Personaje.mover(self, DISPARO)
        elif teclasPulsadas[izquierda]:
            Personaje.mover(self, IZQUIERDA)
        elif teclasPulsadas[derecha]:
            Personaje.mover(self, DERECHA)
        elif teclasPulsadas[ataque]:
            if self.cooldownBaguette <= 0:
                self.atacar()
                Personaje.mover(self, ATACAR_BAGUETTE)
        elif teclasPulsadas[disparo]:
            if self.cooldownCroissant <= 0:
                self.disparar()
                Personaje.mover(self, DISPARO)
        elif not self.atacando:
            Personaje.mover(self, QUIETO)

        # Reduccion en el cooldown desde el ultimo ataque        
        if self.cooldownBaguette > 0:
            self.cooldownBaguette -= 1
        
        if self.cooldownCroissant > 0:
            self.cooldownCroissant -= 1

        self.usoCroissant = False

    def atacar(self):
        attack_sound = GestorRecursos.CargarSonido('air-whoosh.mp3')
        attack_sound.play()
        self.atacando = True
        self.cooldownBaguette = 70

        if self.mirando == IZQUIERDA:
            self.hitbox_baguette.establecerPosicion((self.hitbox_baguette.posicion[0] - self.hitbox_baguette.rect.width - 20, self.hitbox_baguette.posicion[1]))
        else:
            self.hitbox_baguette.establecerPosicion((self.hitbox_baguette.posicion[0] + 150, self.hitbox_baguette.posicion[1]))
        
        # TODO -> colision 

        # Activa la hitbox de alguna forma
    
    def disparar(self):
        attack_sound = GestorRecursos.CargarSonido('air-whoosh.mp3')
        attack_sound.play()
        self.atacando = True
        self.cooldownCroissant = 60
        
        for disparo in self.croissants:
            if disparo.movimiento == DISPARO_CERTERO:
                disparo.establecerPosicion(self.posicion)
                disparo.mover(self.mirando)
                break
        # TODO -> colision 
        
        # Activa la hitbox

    # Notificar cambio en el valor de vida al display
    def notificarVidaDisplay(self):
        self.vida_display.notificar(self.vida)

    def establecerVidaDisplay(self, vida_display):
        self.vida_display = vida_display  # Elemento que muestra la información de vida
        self.notificarVidaDisplay()  # Le pasamos la información de vida inicial

    def quitar_vida(self):
        vida_quitada = Personaje.quitar_vida(self)
        if vida_quitada and self.vida_display is not None:
            self.notificarVidaDisplay()

        return vida_quitada

    def curar(self):
        if self.vida < self.max_vida:
            self.vida += 1

            if self.vida_display is not None:
                self.notificarVidaDisplay()

    # Redefinición de operaciones de posición para que la hitbox se mueva con el jugador.
    def establecerPosicion(self, posicion):
        MiSprite.establecerPosicion(self, posicion)
        posx_media = posicion[0] + self.rect.width/2

        if self.mirando == IZQUIERDA:
            self.hitbox_baguette.establecerPosicion((posx_media - self.hitbox_baguette.rect.width, posicion[1]))
        else:
            self.hitbox_baguette.establecerPosicion((posx_media, posicion[1]))

    def establecerPosicionPantalla(self, scrollDecorado):
        MiSprite.establecerPosicionPantalla(self, scrollDecorado)
        self.hitbox_baguette.establecerPosicionPantalla(scrollDecorado)


class NoJugador(Personaje):
    """Personajes que no son el jugador. CPU por defecto: miran al jugador"""

    def __init__(self, imagen, coordenadas, numImagenes, velocidad, velocidadSalto, retardoAnimacion, vida):

        Personaje.__init__(self, imagen, coordenadas, numImagenes, velocidad, velocidadSalto, retardoAnimacion, vida)

    def mover_cpu(self, jugador):
        if jugador.posicion[0] < self.posicion[0]:
            self.mirando = IZQUIERDA
        else:
            self.mirando = DERECHA


class Obstaculo(NoJugador):
    """Estatuas para bloquear el paso"""

    def __init__(self, coordenadas, velocidad, velocidadSalto, retardoAnimacion):

        Personaje.__init__(self, 'estatua.png', coordenadas, [1, 0, 0, 0, 0, 0], velocidad, velocidadSalto, retardoAnimacion, 3)

    def mover_cpu(self, jugador):
        self.mirando = IZQUIERDA


# -------------------------------------------- Enemigos y NPCs ---------------------------------------------------------

class Tomate(NoJugador):

    def __init__(self):
        NoJugador.__init__(self, 'Tomato-Sheet.png', 'coordTomato.txt', [8, 8, 2, 13, 0, 0], VELOCIDAD_ENEMIGOS,
                           VELOCIDAD_SALTO_ENEMIGOS, RETARDO_ANIMACION_ENEMIGOS, VIDA_TOMATE)

    def mover_cpu(self, jugador):

        # Movemos solo a los enemigos que esten en la pantalla
        if self.rect.left > 0 and self.rect.right < ANCHO_PANTALLA and self.rect.bottom > 0 and self.rect.top < ALTO_PANTALLA:

            if jugador.posicion[0] < self.posicion[0]:
                Personaje.mover(self, IZQUIERDA)
                self.mirando = DERECHA
            else:
                Personaje.mover(self, DERECHA)
                # self.mirando = IZQUIERDA

        # Si este personaje no esta en pantalla, no hara nada
        else:
            Personaje.mover(self, QUIETO)


class Zanahoria(NoJugador):

    def __init__(self):
        NoJugador.__init__(self, 'Carrot-sheet.png', 'coordCarrot.txt', [6, 6, 6, 2, 7, 0], VELOCIDAD_ENEMIGOS,
                           VELOCIDAD_SALTO_ENEMIGOS, RETARDO_ANIMACION_ENEMIGOS, VIDA_ZANAHORIA)

    def mover_cpu(self, jugador):

        if self.rect.left > 0 and self.rect.right < ANCHO_PANTALLA and self.rect.bottom > 0 and self.rect.top < ALTO_PANTALLA:

            if jugador.posicion[0] < self.posicion[0]:
                # Personaje.mover(self, IZQUIERDA)
                self.mirando = DERECHA
            else:
                Personaje.mover(self, DERECHA)
                # self.mirando = IZQUIERDA

        # Si este personaje no esta en pantalla, no hara nada
        else:
            Personaje.mover(self, QUIETO)


class Boss(NoJugador):

    def __init__(self):
        NoJugador.__init__(self, 'boss.png', 'coordBoss.txt', [4, 4, 4, 0, 0, 0], VELOCIDAD_BOSS,
                           VELOCIDAD_SALTO_ENEMIGOS, RETARDO_ANIMACION_ENEMIGOS, VIDA_BOSS)

    def mover_cpu(self, jugador):

        # Movemos solo a los enemigos que esten en la pantalla
        if self.rect.left > 0 and self.rect.right < ANCHO_PANTALLA and self.rect.bottom > 0 and self.rect.top < ALTO_PANTALLA:

            if jugador.posicion[0] < self.posicion[0]:
                Personaje.mover(self, IZQUIERDA)
                self.mirando = DERECHA
            else:
                Personaje.mover(self, DERECHA)
                # self.mirando = IZQUIERDA

        self.image = pygame.transform.scale(self.image, (self.rect.size[0] * 1.3, self.rect.size[1] * 1.3))


class NPC(NoJugador):
    def __init__(self, sheet, coord, array_coord):
        NoJugador.__init__(self, sheet, coord, array_coord, VELOCIDAD_ENEMIGOS,
                           VELOCIDAD_SALTO_ENEMIGOS, RETARDO_ANIMACION_ENEMIGOS, VIDA_NPC)

    def mover_cpu(self, jugador):
        if jugador.posicion[0] < self.posicion[0]:
            self.mirando = IZQUIERDA
        else:
            self.mirando = DERECHA


class Madre(NPC):
    def __init__(self):
        NPC.__init__(self, 'Madre-Sheet.png', 'coordMadre.txt', [8, 0, 0, 0, 0, 0])


class AldeanoFalda(NPC):
    def __init__(self):
        NPC.__init__(self, 'AldeanoFalda-sheet.png', 'coordFalda.txt', [7, 0, 0, 0, 0, 0])

    def mover_cpu(self, jugador):
        NPC.mover_cpu(self, jugador)


class AldeanoSombrero(NPC):
    def __init__(self):
        NPC.__init__(self, 'AldeanoSombrero-sheet.png', 'coordSombrero.txt', [4, 0, 0, 0, 0, 0])

    def mover_cpu(self, jugador):
        NPC.mover_cpu(self, jugador)


# ----------------------------------------- Proyectiles y Hitbox -------------------------------------------------------
class Proyectil(MiSprite):
    """Cada proyectil del juego"""

    # Parametros pasados al constructor de esta clase:
    #  Archivo con la hoja de Sprites
    #  Archivo con las coordenadoas dentro de la hoja
    #  Numero de imagenes en cada postura
    #  Velocidad de caminar y de rotacion
    #  Retardo para mostrar la animacion del personaje
    def __init__(self, imagen, coordenadas, numImagenes, velocidadCarrera, retardoAnimacion, direccion):

        # Primero invocamos al constructor de la clase padre
        MiSprite.__init__(self)

        # Se carga la hoja
        self.hoja = GestorRecursos.CargarImagen(imagen, 0)
        self.hoja = self.hoja.convert_alpha()
        # El movimiento que esta realizando
        self.movimiento = DISPARO_CERTERO
        # Lado hacia el que esta mirando
        self.mirando = direccion

        # Leemos las coordenadas de un archivo de texto
        datos = GestorRecursos.CargarArchivoCoordenadas(coordenadas)
        datos = datos.split()
        self.numPostura = 1
        self.numImagenPostura = 0
        self.prevPostura = 0
        cont = 0
        self.coordenadasHoja = []
        self.coordenadasHoja.append([])
        tmp = self.coordenadasHoja[0]

        for postura in range(1, numImagenes[0] + 1):
            tmp.append(
                pygame.Rect((int(datos[cont]), int(datos[cont + 1])), (int(datos[cont + 2]), int(datos[cont + 3]))))
            cont += 4

        # El retardo a la hora de cambiar la imagen del Sprite (para que no se mueva demasiado rápido)
        self.retardoMovimiento = 0

        # En que postura esta inicialmente

        # El rectangulo del Sprite
        self.rect = pygame.Rect(100, 100, self.coordenadasHoja[0][self.numImagenPostura][2],
                                self.coordenadasHoja[0][self.numImagenPostura][3])
        
        # Las velocidades de caminar y salto
        self.velocidadCarrera = velocidadCarrera

        # El retardo en la animacion del personaje (podria y deberia ser distinto para cada postura)
        self.retardoAnimacion = retardoAnimacion

        # Y actualizamos la postura del Sprite inicial, llamando al metodo correspondiente
        self.image = self.hoja.subsurface(self.coordenadasHoja[self.numPostura-1][self.numImagenPostura])

        self.image = pygame.transform.scale(self.image, (self.rect.size[0] * 0.5, self.rect.size[1] * 0.5))

    # Metodo base para realizar el movimiento: simplemente se le indica cual va a hacer, y lo almacena
    def mover(self, movimiento):
        self.movimiento = movimiento

    def update(self, tiempo, grupoPlataformas):

        # Las velocidades a las que iba hasta este momento
        (velocidadx, velocidady) = self.velocidad

        # Si vamos a la izquierda o a la derecha
        
        if (self.movimiento == IZQUIERDA) or (self.movimiento == DERECHA):
            velocidadx = self.desplHorizontal(self.movimiento)

        if self.movimiento == DISPARO_CERTERO:
            self.establecerPosicion((1000, 1000))

        if self.rect.left > (ANCHO_PANTALLA + 20) or self.rect.right < (-20):
            self.movimiento = DISPARO_CERTERO

        if self.movimiento == DISPARO_CERTERO:
            velocidadx = 0

        # Actualizamos la imagen a mostrar
        # self.actualizarRotacion()

        # Aplicamos la velocidad en cada eje
        self.velocidad = (velocidadx, velocidady)

        self.actualizarPostura()
        # Y llamamos al método de la superclase para que, según la velocidad y el tiempo
        #  calcule la nueva posición del Sprite
        self.image = pygame.transform.scale(self.image, (self.rect.size[0] * 0.5, self.rect.size[1] * 0.5))

        MiSprite.update(self, tiempo)            

    def desplHorizontal(self, movimiento):
        self.mirando = movimiento

        # Si vamos a la izquierda, le ponemos velocidad en esa dirección
        if self.movimiento == IZQUIERDA:
            return -self.velocidadCarrera
        # Si vamos a la derecha, le ponemos velocidad en esa dirección
        else:
            return self.velocidadCarrera

    def actualizarPostura(self):
        cambiarImagen = False
        self.retardoMovimiento -= 1
        
        # Comprobamos si hay que reiniciar self.numImagenPostura porque hemos cambiado de postura
        
        # Miramos si ha pasado el retardo para dibujar una nueva imagen de la postura actual
        if self.retardoMovimiento < 0:
            cambiarImagen = True
            
            # Si ha pasado, actualizamos la postura
            self.numImagenPostura += 1
            if self.numImagenPostura >= len(self.coordenadasHoja[self.numPostura - 1]):
                self.numImagenPostura = 0
            if self.numImagenPostura < 0:
                self.numImagenPostura = len(self.coordenadasHoja[self.numPostura - 1]) - 1
        
        # Modificar la imagen a mostrar si el contador de retardo ha llegado a 0 o si se ha cambiado la postura
        if cambiarImagen:
            # El retardo se reinicia tanto si ha llegado a 0 como si se ha cambiado de postura
            self.retardoMovimiento = self.retardoAnimacion

            # Si esta mirando a la izquierda, cogemos la porcion de la hoja
            if self.mirando == DERECHA:
                self.image = self.hoja.subsurface(self.coordenadasHoja[self.numPostura - 1][self.numImagenPostura])
            #  Si no, si mira a la derecha, invertimos esa imagen
            elif self.mirando == IZQUIERDA:
                self.image = pygame.transform.flip(self.hoja.subsurface(self.coordenadasHoja[self.numPostura - 1][self.numImagenPostura]), True, False)
        
            # Actualizamos el tamaño del rect para que coincida con la imagen actual
            self.rect.size = (self.coordenadasHoja[self.numPostura - 1][self.numImagenPostura][2],
                              self.coordenadasHoja[self.numPostura - 1][self.numImagenPostura][3])
        

class Croissant(Proyectil):
    """Proyectil lanzado por el jugador el línea recta"""
    def __init__(self, direccion):
        Proyectil.__init__(self, 'thrownCroissant.png', 'coordCroissant.txt', [8, 8, 8, 0, 0, 0], VELOCIDAD_CROISSANT,
                           RETARDO_ANIMACION_ENEMIGOS, direccion)


class Hitbox(MiSprite):
    def __init__(self, rectangulo):

        MiSprite.__init__(self)
        self.rect = Rect(rectangulo)

