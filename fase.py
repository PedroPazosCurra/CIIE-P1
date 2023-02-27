# -*- coding: utf-8 -*-

import pygame
from escena import *
from personajes import *
from pygame.locals import *

# -------------------------------------------------
# -------------------------------------------------
# Constantes
# -------------------------------------------------
# -------------------------------------------------

VELOCIDAD_SOL = 0.1 # Pixeles por milisegundo

# Los bordes de la pantalla para hacer scroll horizontal
MINIMO_X_JUGADOR = 50
MAXIMO_X_JUGADOR = ANCHO_PANTALLA - MINIMO_X_JUGADOR

# -------------------------------------------------
# Clase Fase

class Fase(Escena):
    def __init__(self, director):

        # Habria que pasarle como parámetro el número de fase, a partir del cual se cargue
        #  un fichero donde este la configuracion de esa fase en concreto, con cosas como
        #   - Nombre del archivo con el decorado
        #   - Posiciones de las plataformas
        #   - Posiciones de los enemigos
        #   - Posiciones de inicio de los jugadores
        #  etc.
        # Y cargar esa configuracion del archivo en lugar de ponerla a mano, como aqui abajo
        # De esta forma, se podrian tener muchas fases distintas con esta clase

        # Primero invocamos al constructor de la clase padre
        Escena.__init__(self, director)

        # Creamos el decorado y el fondo
        self.decorado = Decorado()
        self.fondo = Cielo()

        #  En ese caso solo hay scroll horizontal
        #  Si ademas lo hubiese vertical, seria self.scroll = (0, 0)

        # Creamos los sprites de los jugadores
        self.jugador = Jugador()
        self.grupoJugadores = pygame.sprite.Group(self.jugador)

        # Ponemos a los jugadores en sus posiciones iniciales
        self.jugador.establecerPosicion((400, 300))
        
        # Que parte del decorado estamos visualizando
        self.scrollx = 0
        

        # Creamos las plataformas del decorado
        # La plataforma que conforma el suelo
        plataformaSuelo = Plataforma(pygame.Rect(0, 550, 1200, 15))
        self.grupoPlataformas = pygame.sprite.Group(plataformaSuelo)

        self.trigger_izq = Trigger(pygame.Rect(0, 550, 100, 500))
        self.trigger_der = Trigger(pygame.Rect(800, 550, -100, 500))

        """     NOTA: Cuando creemos enemigos debemos hacerlos aquí y de esta forma
        # Y los enemigos que tendran en este decorado
        enemigo1 = NoJugador()
        enemigo1.establecerPosicion((1000, 418))

        # Creamos un grupo con los enemigos
        self.grupoEnemigos = pygame.sprite.Group( enemigo1 )"""

        # Creamos un grupo con los Sprites que se mueven
        #  En este caso, solo los personajes, pero podría haber más (proyectiles, etc.)
        self.grupoSpritesDinamicos = pygame.sprite.Group(self.jugador)
        # Creamos otro grupo con todos los Sprites
        self.grupoSprites = pygame.sprite.Group(self.jugador)

    # Para evitar que el jugador se salga de pantalla podemos poner maximos/plataformas ¿?    
    def actualizarScroll(self, jugador):
        if jugador.posicion[0] + ANCHO_PANTALLA / 2 >= self.decorado.rect.right:
            self.scrollx = self.decorado.rect.right - ANCHO_PANTALLA
        elif jugador.posicion[0] - ANCHO_PANTALLA / 2 <= 0:
            self.scrollx = 0
        else:
            self.scrollx = jugador.posicion[0] - ANCHO_PANTALLA / 2
            
            for sprite in iter(self.grupoSprites):
                sprite.establecerPosicionPantalla((self.scrollx, 0))
            
            self.decorado.update(self.scrollx)

    # Se actualiza el decorado, realizando las siguientes acciones:
    #  Se indica para los personajes no jugadores qué movimiento desean realizar según su IA
    #  Se mueven los sprites dinámicos, todos a la vez
    #  Se comprueba si hay colision entre algun jugador y algun enemigo
    #  Se comprueba si algún jugador ha salido de la pantalla, y se actualiza el scroll en consecuencia
    #     Actualizar el scroll implica tener que desplazar todos los sprites por pantalla
    #  Se actualiza la posicion del sol y el color del cielo
    def update(self, tiempo):

        """     Cuando haya enemigos, descomentar
        # Primero, se indican las acciones que van a hacer los enemigos segun como esten los jugadores
        for enemigo in iter(self.grupoEnemigos):
            enemigo.mover_cpu(self.jugador1)
        # Esta operación es aplicable también a cualquier Sprite que tenga algún tipo de IA"""

        # Actualizamos los Sprites dinamicos
        # De esta forma, se simula que cambian todos a la vez
        # Esta operación de update ya comprueba que los movimientos sean correctos
        #  y, si lo son, realiza el movimiento de los Sprites
        self.grupoSpritesDinamicos.update(self.grupoPlataformas, tiempo)
        # Dentro del update ya se comprueba que todos los movimientos son válidos
        #  (que no choque con paredes, etc.)

        # Los Sprites que no se mueven no hace falta actualizarlos,
        #  si se actualiza el scroll, sus posiciones en pantalla se actualizan más abajo
        # En cambio, sí haría falta actualizar los Sprites que no se mueven pero que tienen que
        #  mostrar alguna animación

        """     Cuando haya enemigos, descomentar
        # Comprobamos si hay colision entre algun jugador y algun enemigo
        # Se comprueba la colision entre ambos grupos
        # Si la hay, indicamos que se ha finalizado la fase
        if pygame.sprite.groupcollide(self.grupoJugadores, self.grupoEnemigos, False, False)!={}:
            # Se le dice al director que salga de esta escena y ejecute la siguiente en la pila
            self.director.salirEscena()"""

        # Comprobamos si hay colision entre jugador y triggers

        # Trigger izquierdo
        if self.trigger_izq.rect.colliderect(self.jugador.rect):
            fase = Fase(self.director)
            self.director.cambiarEscena(fase)

        # Trigger derecho
        if self.trigger_der.rect.colliderect(self.jugador.rect):
            fase = Fase(self.director)
            self.director.cambiarEscena(fase)

        # Actualizamos el scroll
        self.actualizarScroll(self.jugador)
  
        # Actualizamos el fondo:
        #  la posicion del sol y el color del cielo
        self.fondo.update(tiempo)

        
    def dibujar(self, pantalla):
        # Ponemos primero el fondo
        self.fondo.dibujar(pantalla)

        # Si hubiera alguna animación detrás, se dibuja aquí

        # Después el decorado
        self.decorado.dibujar(pantalla)

        # Si hubiera alguna animación delante, se dibuja aquí

        # Luego los Sprites
        self.grupoSprites.draw(pantalla)


    def eventos(self, lista_eventos):
        # Miramos a ver si hay algun evento de salir del programa
        for evento in lista_eventos:
            # Si se quiere salir, se le indica al director
            if evento.type == pygame.QUIT:
                self.director.salirPrograma()

        # Indicamos la acción a realizar segun la tecla pulsada para cada jugador
        teclasPulsadas = pygame.key.get_pressed()
        self.jugador.mover(teclasPulsadas, K_UP, K_DOWN, K_LEFT, K_RIGHT)

# -------------------------------------------------
# Clase Plataforma

#class Plataforma(pygame.sprite.Sprite):
class Plataforma(MiSprite):
    def __init__(self, rectangulo):
        # Primero invocamos al constructor de la clase padre
        MiSprite.__init__(self)
        # Rectangulo con las coordenadas en pantalla que ocupara
        self.rect = rectangulo
        # Y lo situamos de forma global en esas coordenadas
        self.establecerPosicion((self.rect.left, self.rect.bottom))
        # En el caso particular de este juego, las plataformas no se van a ver, asi que no se carga ninguna imagen
        self.image = pygame.Surface((0, 0))



# ------------------------------------------------
# Clase trigger para pasar entre fases
class Trigger(MiSprite):
    def __init__(self, rectangulo):

        MiSprite.__init__(self)

        self.rect = rectangulo

        self.establecerPosicion((self.rect.left, self.rect.bottom))

        self.image = pygame.Surface((0, 0))


# -------------------------------------------------
# Clase Cielo

class Cielo:
    def __init__(self):

        self.nubes = GestorRecursos.CargarImagen('cielo_fondo1.png', 0)
        self.nubes = pygame.transform.scale(self.nubes, (1100, 550))

        self.nubesdup = GestorRecursos.CargarImagen('cielo_fondo1.png', 0)
        self.nubesdup = pygame.transform.scale(self.nubesdup, (1100, 550))

        self.rect_nubes = self.nubes.get_rect()
        self.rect_nubesdup = self.nubesdup.get_rect()
        self.posicionx = 0
        self.posicionxdup = -1100
        self.update(0)

    def update(self, tiempo):

        self.posicionx += VELOCIDAD_SOL * tiempo
        self.posicionxdup += VELOCIDAD_SOL * tiempo

        if self.posicionx >= ANCHO_PANTALLA:
            self.posicionx = -1100

        if self.posicionxdup >= ANCHO_PANTALLA:
            self.posicionxdup = -1100

        self.rect_nubes.left = self.posicionx
        self.rect_nubesdup.left = self.posicionxdup

        
    def dibujar(self, pantalla):

        pantalla.fill((100, 200, 255))

        pantalla.blit(self.nubes, self.rect_nubes)
        pantalla.blit(self.nubesdup, self.rect_nubesdup)

        # Y ponemos el sol
        #pantalla.blit(self.sol, self.rect)


# -------------------------------------------------
# Clase Decorado

class Decorado:
    def __init__(self):
        self.imagen = GestorRecursos.CargarImagen('road.png', -1)
        self.imagen = pygame.transform.scale(self.imagen, (1200, 400))

        self.rect = self.imagen.get_rect()
        self.rect.bottom = ALTO_PANTALLA

        # La subimagen que estamos viendo
        self.rectSubimagen = pygame.Rect(0, 0, ANCHO_PANTALLA, ALTO_PANTALLA)
        self.rectSubimagen.left = 0 # El scroll horizontal empieza en la posicion 0 por defecto

    def update(self, scrollx):
        self.rectSubimagen.left = scrollx

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen, self.rect, self.rectSubimagen)
