# -*- coding: utf-8 -*-

import pygame
from escena import *
from personajes import *
from pygame.locals import *

VELOCIDAD_NUBES = 0.04  # Pixeles por milisegundo


class Fase(Escena):
    def __init__(self, director, nombre_fase):

        # TODO: Tenemos que abstraer esta clase para hacer todo con JSON y no depender de lo puesto aquí

        # Primero invocamos al constructor de la clase padre
        Escena.__init__(self, director)

        self.nombre_fase = nombre_fase
        self.datos = GestorRecursos.CargarArchivoFaseJSON(nombre_fase)

        # Creamos el suelo, el decorado y el fondo
        self.suelo = Suelo(self.datos)
        self.decorado = Decorado(self.datos)
        self.fondo = Fondo(self.datos)
        self.cielo = Cielo(self.datos)

        #  En ese caso solo hay scroll horizontal
        #  Si ademas lo hubiese vertical, seria self.scroll = (0, 0)

        # Creamos los sprites de los jugadores
        self.jugador = Jugador()
        self.grupoJugadores = pygame.sprite.Group(self.jugador)

        # Ponemos a los jugadores en sus posiciones iniciales
        self.jugador.establecerPosicion((self.datos["POS_INICIAL"]))

        # Que parte del decorado estamos visualizando
        self.scrollx = 0

        self.vida = Vida(self.jugador)

        # Creamos las plataformas del decorado
        # La plataforma que conforma el suelo
        #plataformaSuelo = Plataforma(pygame.Rect(self.datos["PLATAFORMA"]), self.datos["PLATAFORMA_SPRITE"])
        #self.grupoPlataformas = pygame.sprite.Group(plataformaSuelo)
        self.grupoPlataformas = pygame.sprite.Group()
        self.crearPlataformas()

        self.trigger_izq = Trigger(pygame.Rect(0, 550, 100, 500))
        self.trigger_der = Trigger(pygame.Rect(800, 550, -100, 500))

        # Y los enemigos que tendran en este decorado
        tomate = Tomate()
        tomate.establecerPosicion((500, 550))

        zanahoria = Zanahoria()
        zanahoria.establecerPosicion((550, 550))
        self.grupoEnemigos = pygame.sprite.Group(tomate, zanahoria)

        madre = Madre()
        madre.establecerPosicion((600, 550))
        self.grupoNPCs = pygame.sprite.Group(madre)

        # Creamos un grupo con los Sprites que se mueven
        #  En este caso, solo los personajes, pero podría haber más (proyectiles, etc.)
        self.grupoSpritesDinamicos = pygame.sprite.Group(self.jugador, tomate, zanahoria, madre)
        # Creamos otro grupo con todos los Sprites
        self.grupoSprites = pygame.sprite.Group(self.jugador, tomate, zanahoria, madre)

    def crearPlataformas(self):
        plataformas = []
        for plataforma in self.datos["PLATAFORMA"]:
           plataformas.append(Plataforma(pygame.Rect(plataforma),self.datos["PLATAFORMA_SPRITE"]))
        self.grupoPlataformas.add(plataformas)
    
    # Para evitar que el jugador se salga de pantalla podemos poner maximos/plataformas ¿?    
    def actualizarScroll(self, jugador):
        if jugador.posicion[0] + ANCHO_PANTALLA / 2 >= self.fondo.rect.right:
            self.scrollx = self.fondo.rect.right - ANCHO_PANTALLA
        elif jugador.posicion[0] - ANCHO_PANTALLA / 2 <= 0:
            self.scrollx = 0
        else:
            self.scrollx = jugador.posicion[0] - ANCHO_PANTALLA / 2

            for sprite in iter(self.grupoSprites):
                sprite.establecerPosicionPantalla((self.scrollx, 0))

            self.decorado.update(self.scrollx)
            self.fondo.update(self.scrollx)
            self.suelo.update(self.scrollx)

    # Se actualiza el decorado
    def update(self, tiempo):

        # Primero, se indican las acciones que van a hacer los enemigos segun como esten los jugadores
        for enemigo in iter(self.grupoEnemigos):
            enemigo.mover_cpu(self.jugador)

        for npc in iter(self.grupoNPCs):
            npc.mover_cpu(self.jugador)

        # Actualizamos los Sprites dinamicos
        self.grupoSpritesDinamicos.update(self.grupoPlataformas, tiempo)

        # Dentro del update ya se comprueba que todos los movimientos son válidos
        #  (que no choque con paredes, etc.)

        # Los Sprites que no se mueven no hace falta actualizarlos,
        #  si se actualiza el scroll, sus posiciones en pantalla se actualizan más abajo
        # En cambio, sí haría falta actualizar los Sprites que no se mueven pero que tienen que
        #  mostrar alguna animación

        # Colision entre jugador y enemigo -> quita vida
        if pygame.sprite.groupcollide(self.grupoJugadores, self.grupoEnemigos, False, False) != {}:
            if self.vida.cooldownDano <= 0:
                self.vida.quitar_vida()

        # Cooldown tras recibir daño
        if self.vida.cooldownDano > 0:
            self.vida.cooldownDano -= 1

        # Colision entre jugador y triggers -> cambia fase

        # Trigger izquierdo
        if self.trigger_izq.rect.colliderect(self.jugador.rect):
            fase = Fase(self.director, self.nombre_fase)
            self.director.cambiarEscena(fase)

        # Trigger derecho
        if self.trigger_der.rect.colliderect(self.jugador.rect):
            fase = Fase(self.director, self.nombre_fase)
            self.director.cambiarEscena(fase)

        # Actualizamos el scroll
        self.actualizarScroll(self.jugador)

        # Actualizamos el cielo:
        self.cielo.update(tiempo)

    def dibujar(self, pantalla):

        # Ponemos primero el fondo
        self.cielo.dibujar(pantalla)
        self.fondo.dibujar(pantalla)

        # Después el decorado
        self.decorado.dibujar(pantalla)
        self.suelo.dibujar(pantalla)
        self.vida.dibujar(pantalla)

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
        self.jugador.mover(teclasPulsadas, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_z)


# ----------------------------------------------Plataforma--------------------------------------------------------------
class Plataforma(MiSprite):
    def __init__(self, rectangulo, imagen=None):

        MiSprite.__init__(self)
        # Rectangulo con las coordenadas en pantalla que ocupara
        self.rect = rectangulo
        self.establecerPosicion((self.rect.left, self.rect.bottom))

        if imagen is not None:
            self.image = imagen
        else:
            self.image = pygame.Surface((0, 0))


# ------------------------------------------------Trigger--------------------------------------------------------------
class Trigger(MiSprite):
    def __init__(self, rectangulo):
        MiSprite.__init__(self)
        self.rect = rectangulo
        self.establecerPosicion((self.rect.left, self.rect.bottom))
        self.image = pygame.Surface((0, 0))


# ----------------------------------------Cielo, Decorado, Suelo--------------------------------------------------------

class Cielo:
    def __init__(self, datos):

        self.nubes = GestorRecursos.CargarImagen(datos['CIELO'], 0)
        self.nubes = pygame.transform.scale(self.nubes, (1100, 550))

        self.nubesdup = GestorRecursos.CargarImagen(datos['CIELO'], 0)
        self.nubesdup = pygame.transform.scale(self.nubesdup, (1100, 550))

        self.rect_nubes = self.nubes.get_rect()
        self.rect_nubesdup = self.nubesdup.get_rect()
        self.posicionx = 0
        self.posicionxdup = -1100
        self.update(0)

    def update(self, tiempo):

        self.posicionx += VELOCIDAD_NUBES * tiempo
        self.posicionxdup += VELOCIDAD_NUBES * tiempo

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


class Fondo:
    def __init__(self, datos):
        self.imagen = GestorRecursos.CargarImagen(datos["FONDO"], -1)
        self.imagen = pygame.transform.scale(self.imagen, datos["SIZE"])

        self.rect = self.imagen.get_rect()
        self.rect.bottom = ALTO_PANTALLA

        # La subimagen que estamos viendo
        self.rectSubimagen = pygame.Rect(0, 0, ANCHO_PANTALLA, ALTO_PANTALLA)
        self.rectSubimagen.left = 0  # El scroll horizontal empieza en la posicion 0 por defecto

    def update(self, scrollx):
        self.rectSubimagen.left = scrollx/3

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen, self.rect, self.rectSubimagen)

class Decorado:
    def __init__(self, datos):
        self.imagen = GestorRecursos.CargarImagen(datos["DECORADO"], -1)
        self.imagen = pygame.transform.scale(self.imagen, datos["SIZE"])

        self.rect = self.imagen.get_rect()
        self.rect.bottom = ALTO_PANTALLA

        # La subimagen que estamos viendo
        self.rectSubimagen = pygame.Rect(0, 0, ANCHO_PANTALLA, ALTO_PANTALLA)
        self.rectSubimagen.left = 0  # El scroll horizontal empieza en la posicion 0 por defecto

    def update(self, scrollx):
        self.rectSubimagen.left = scrollx/1.2

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen, self.rect, self.rectSubimagen)


class Suelo:
    def __init__(self, datos):
        self.suelo = GestorRecursos.CargarImagen(datos["SUELO"], -1)
        self.suelo = pygame.transform.scale(self.suelo, datos["SIZE"])

        self.rect = self.suelo.get_rect()
        self.rect.bottom = ALTO_PANTALLA

        # La subimagen que estamos viendo
        self.rectSubimagen = pygame.Rect(0, 0, ANCHO_PANTALLA, ALTO_PANTALLA)
        self.rectSubimagen.left = 0  # El scroll horizontal empieza en la posicion 0 por defecto

    def update(self, scrollx):
        self.rectSubimagen.left = scrollx

    def dibujar(self, pantalla):
        pantalla.blit(self.suelo, self.rect, self.rectSubimagen)


# --------------------------------------------------Vida----------------------------------------------------------------
class Vida:
    def __init__(self, jugador):
        self.vida_actual = jugador.vida
        self.imagen = []
        for i in range(5):
            auxImg = GestorRecursos.CargarImagen('vidas' + str(i + 1) + '.png', -1)
            auxImg = pygame.transform.scale(auxImg, (200, 50))
            self.imagen.append(auxImg)

        self.rect = self.imagen[0].get_rect()
        self.cooldownDano = 0

    def quitar_vida(self):

        self.cooldownDano = 120

        if self.vida_actual >= 1:
            self.vida_actual -= 1
        else:
            print("Muere")

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen[self.vida_actual - 1], self.rect)
