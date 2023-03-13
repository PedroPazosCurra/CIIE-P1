# -*- coding: utf-8 -*-

from pygame.locals import *

import personajes
from escena import *
from gestorRecursos import GestorRecursos
from muerte import Muerte
from personajes import Jugador, MiSprite

VELOCIDAD_NUBES = 0.04  # Pixeles por milisegundo

DIBUJAR_RECTS = False  # Flag para marcar si se dibujan o no rects


class Fase(Escena):
    def __init__(self, director, nombre_fase):

        Escena.__init__(self, director)
        self.director = director

        self.nombre_fase = nombre_fase
        self.datos = GestorRecursos.CargarArchivoFaseJSON(nombre_fase)

        # Creamos el suelo, el decorado y el fondo
        self.suelo = Suelo(self.datos)
        self.decorado = Decorado(self.datos)
        self.fondo = Fondo(self.datos)
        self.cielo = Cielo(self.datos)

        #  En ese caso solo hay scroll horizontal
        #  Si ademas lo hubiese vertical, seria self.scroll = (0, 0)

        # Creamos los sprites de los jugadores y el display de su vida
        
        self.jugador = Jugador()
        self.grupoJugadores = pygame.sprite.Group(self.jugador)

        # Ponemos a los jugadores en sus posiciones iniciales y le añadimos el display de vida
        self.jugador.establecerPosicion((self.datos["POS_INICIAL_PERSONAJE"]))
        self.vida_display = VidaDisplay(self.jugador.max_vida)
        self.jugador.establecerVidaDisplay(self.vida_display)

        # Que parte del decorado estamos visualizando
        self.scrollx = 0

        # TODO: La vida ahora mismo se reinicia entre escenas. Esto tiene que cambiarse de alguna forma

        # Creamos las plataformas del decorado
        # La plataforma que conforma el suelo
        self.grupoPlataformas = pygame.sprite.Group()
        self.crearPlataformas()

        # Triggers para cambiar de escena parametrizados
        ancho = self.datos["SIZE"][0]
        alto = self.datos["SIZE"][1]

        # TODO: Parametrizar los triggers según largo de fase

        self.trigger_izq = Trigger(pygame.Rect(0, alto, 1, alto), self.datos["TRIGGER_IZQ_ESCENA"])
        self.trigger_der = Trigger(pygame.Rect(0.5*ancho, alto, 1, alto), self.datos["TRIGGER_DER_ESCENA"])

        # Sprites que se mueven
        #  En este caso, solo los personajes, pero podría haber más (proyectiles, etc.)
        self.grupoSpritesDinamicos = pygame.sprite.Group(self.jugador)
        # Todos los sprites
        self.grupoSprites = pygame.sprite.Group(self.jugador)

        # NPC y enemigos
        self.grupoEnemigos = pygame.sprite.Group()
        self.grupoNPCs = pygame.sprite.Group()
        self.grupoObjetos = pygame.sprite.Group()
        self.crearEnemigos()
        self.crearNPCs()
        self.crearObjetos()

        self.grupoProyectiles = pygame.sprite.Group()
        self.crearProyectiles()

        # Musica
        self.cargarMusica()
        self.reproducirMusica()

    def cargarMusica(self):
        GestorRecursos.CargarMusica(self.datos["MUSICA"])

    def reproducirMusica(self):
        pygame.mixer.music.play(-1)

    def detenerMusica(self):
        pygame.mixer.music.stop()

    def crearPlataformas(self):
        plataformas = []
        for reg_plataforma in self.datos["PLATAFORMAS"]:
            plataforma = Plataforma(pygame.Rect(reg_plataforma["RECT"]), reg_plataforma["IMAGEN"])
            plataformas.append(plataforma)
        self.grupoPlataformas.add(plataformas)
    
    def crearEnemigos(self):
        enemigos = []
        
        for reg_enemigo in self.datos["ENEMIGOS"]:
            clase_enemigo = getattr(personajes, reg_enemigo["CLASE"])
            inst_enemigo = clase_enemigo()
            inst_enemigo.establecerPosicion(reg_enemigo["POS"])
            enemigos.append(inst_enemigo)

        self.grupoEnemigos.add(enemigos)
        self.grupoSpritesDinamicos.add(enemigos)
        self.grupoSprites.add(enemigos)
        
    def crearProyectiles(self):
        proyectiles = []

        clase_proyectil = getattr(personajes, "Croissant")
        inst_proyectil1 = clase_proyectil(self.jugador.mirando)
        proyectiles.append(inst_proyectil1)
        inst_proyectil2 = clase_proyectil(self.jugador.mirando)
        proyectiles.append(inst_proyectil2)
        inst_proyectil3 = clase_proyectil(self.jugador.mirando)
        proyectiles.append(inst_proyectil3)

        self.grupoProyectiles.add(proyectiles)
        self.grupoSpritesDinamicos.add(proyectiles)
        self.grupoSprites.add(proyectiles)

    def crearNPCs(self):
        listaNPC = []
        
        for reg_npc in self.datos["NPCS"]:
            clase_npc = getattr(personajes, reg_npc["CLASE"])
            inst_npc = clase_npc()
            inst_npc.establecerPosicion(reg_npc["POS"])
            listaNPC.append(inst_npc)

        self.grupoNPCs.add(listaNPC)
        self.grupoSpritesDinamicos.add(listaNPC)
        self.grupoSprites.add(listaNPC)

    def crearObjetos(self):
        listaObjetos = []

        for reg_obj in self.datos["OBJETOS"]:
            clase_obj = getattr(personajes, reg_obj["CLASE"])
            inst_obj = clase_obj()
            inst_obj.establecerPosicion(reg_obj["POS"])
            listaObjetos.append(inst_obj)

        self.grupoObjetos.add(listaObjetos)
        self.grupoSprites.add(listaObjetos)
    
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

        # Actualizamos los Sprites dinamicos
        self.grupoSpritesDinamicos.update(tiempo, self.grupoPlataformas)

        # Colision entre jugador y enemigo -> quita vida
        if not self.jugador.atacando:
            if pygame.sprite.groupcollide(self.grupoJugadores, self.grupoEnemigos, False, False) != {}:
                if self.jugador.quitar_vida() and self.jugador.muerto():
                    self.detenerMusica()
                    self.director.cambiarEscena(Muerte(self.director))

        if pygame.sprite.groupcollide(self.grupoJugadores, self.grupoObjetos, False, True) != {}:
            self.jugador.curar()

        # Colision con hitbox de baguette
        if self.jugador.atacando:

            enemigos_hit_list = pygame.sprite.spritecollide(self.jugador.hitbox_baguette, self.grupoEnemigos, False)
            if enemigos_hit_list:

                hit = GestorRecursos.CargarSonido("punch.mp3")
                for enemigo in enemigos_hit_list:

                    if enemigo.quitar_vida():
                        hit.play()

                    if enemigo.muerto():
                        enemigo.kill()
        for disparo in self.grupoProyectiles:
            enemigos_hit_list = pygame.sprite.spritecollide(disparo, self.grupoEnemigos, False)
            if enemigos_hit_list:
                
                disparo.mover(personajes.DISPARO_CERTERO)

                hit = GestorRecursos.CargarSonido("punch.mp3")
                for enemigo in enemigos_hit_list:

                    if enemigo.quitar_vida():
                        hit.play()

                    if enemigo.muerto():
                        enemigo.kill()

                # TODO: No sé cómo se cogería la referencia del enemigo en base al sprite
        # if (pygame.sprite.spritecollide(self.jugador.hitbox_baguette, self.grupoEnemigos, False, False) != {}) and
        # (self.jugador.atacando is True):
        # (...)
        # if (bicho.vida >= 1) bicho.vida.quitar_vida()
        # else                 bicho.matar()

        # TODO: Colision con croissant seguramente sea un pelin diferente por el tema de ser muchos
        # Colision con hitbox de croissant
        # if pygame.sprite.spritecollide(self.jugador.hitbox_croissant, self.grupoEnemigos, False, False) != {}:

        # hit = GestorRecursos.CargarSonido("punch.mp3")
        # hit.play()

        # TODO: No sé cómo se cogería la referencia del enemigo en base al sprite
        # sprite_bicho = pygame.sprite.spritecollide(self.jugador.hitbox_croissant, self.grupoEnemigos, False, False)[0]
        # (...)
        # if (bicho.vida >= 1) bicho.vida.quitar_vida()
        # else                 bicho.matar()

        # Colision entre jugador y triggers -> cambia fase
        # Trigger izquierdo
        if self.trigger_izq.rect.colliderect(self.jugador.rect):
            fase = Fase(self.director, self.trigger_izq.escena)
            self.director.cambiarEscena(fase)

        # Trigger derecho
        if self.trigger_der.rect.colliderect(self.jugador.rect):
            fase = Fase(self.director, self.trigger_der.escena)
            self.director.cambiarEscena(fase)

        # Actualizamos el scroll
        self.actualizarScroll(self.jugador)

        # Actualizamos el cielo:
        self.cielo.update(tiempo)

        # CPU
        for enemigo in iter(self.grupoEnemigos):
            enemigo.mover_cpu(self.jugador)

        for npc in iter(self.grupoNPCs):
            npc.mover_cpu(self.jugador)

    # Dibuja los rectangulos: Útil mientras que aún estemos ajustando las colisiones
    def dibujar_rects(self, pantalla):
        for sprite in self.grupoSprites.sprites():
            pygame.draw.rect(pantalla, (255, 255, 255), sprite.rect, 2)

        pygame.draw.rect(pantalla, (255, 0, 0), self.jugador.hitbox_baguette.rect, 2)

    def dibujar(self, pantalla):

        # Ponemos primero el fondo
        self.cielo.dibujar(pantalla)
        self.fondo.dibujar(pantalla)

        # Después el decorado
        self.decorado.dibujar(pantalla)
        self.suelo.dibujar(pantalla)
        self.vida_display.dibujar(pantalla)

        # Luego los Sprites
        self.grupoSprites.draw(pantalla)

        if DIBUJAR_RECTS:
            self.dibujar_rects(pantalla)

    def eventos(self, lista_eventos):
        # Miramos a ver si hay algun evento de salir del programa
        for evento in lista_eventos:
            # Si se quiere salir, se le indica al director
            if evento.type == pygame.QUIT:
                self.director.salirPrograma()

        # Indicamos la acción a realizar segun la tecla pulsada para cada jugador
        teclasPulsadas = pygame.key.get_pressed()            

        if teclasPulsadas[K_x] and self.jugador.cooldownCroissant <= 0:
            self.jugador.disparando = False
            for disparo in self.grupoProyectiles:
                if disparo.movimiento == personajes.DISPARO_CERTERO:
                    disparo.establecerPosicion(self.jugador.posicion)
                    disparo.mover(self.jugador.mirando)
                    break

        self.jugador.mover(teclasPulsadas, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_z, K_x)

        

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
    def __init__(self, rectangulo, escena):
        MiSprite.__init__(self)
        self.rect = rectangulo
        self.establecerPosicion((self.rect.left, self.rect.bottom))
        self.image = pygame.Surface((0, 0))
        self.escena = escena


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
class VidaDisplay:
    def __init__(self, vida_max):
        self.vida = vida_max
        self.imagen = []

        for i in range(vida_max):
            auxImg = GestorRecursos.CargarImagen('vidas' + str(i + 1) + '.png', -1)
            auxImg = pygame.transform.scale(auxImg, (200, 50))
            self.imagen.append(auxImg)

        self.rect = self.imagen[0].get_rect()
        self.cooldownDano = 0

    def notificar(self, nueva_vida):
        self.vida = nueva_vida

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen[self.vida - 1], self.rect)



