import os
import pygame
from pygame.locals import *
import json
from pygame import mixer

# -------------------------------------------------
# Clases de los objetos del juego
# -------------------------------------------------
# -------------------------------------------------


# Clase GestorRecursos. En este caso se implementa como una clase vacía, solo con métodos de clase
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
                if colorkey == -1:
                    colorkey = imagen.get_at((0, 0))
                imagen.set_colorkey(colorkey, RLEACCEL)
            # Se almacena
            cls.recursos[nombre] = imagen
            # Se devuelve
            return imagen
    
    @classmethod
    def CargarMusica(cls, nombre):
        # La música se reproduce por streaming, no es un recurso en memoria que podamos referenciar
        fullname = os.path.join('musica', nombre)
        try:
            mixer.music.load(fullname)
        except pygame.error as message:
            print('Cannot load music file:', fullname)
            raise SystemExit(message)

    @classmethod
    def CargarSonido(cls, nombre):
        # Si el nombre de archivo está entre los recursos ya cargados
        if nombre in cls.recursos:
            # Se devuelve ese recurso
            return cls.recursos[nombre]
        # Si no ha sido cargado anteriormente
        else:
            # Se carga la imagen indicando la carpeta en la que está
            fullname = os.path.join('musica', nombre)
            
            try:
                sonido = mixer.Sound(fullname)

            except pygame.error as message:
                print('Cannot load sound file:', fullname)
                raise SystemExit(message)
                
            # Se almacena
            cls.recursos[nombre] = sonido
            # Se devuelve
            return sonido

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

            pfile = None
            try:
                pfile = open(fullname, 'r')
                datos = pfile.read()
            except pygame.error as message:
                print('Cannot load coordinates file:', fullname)
                raise SystemExit(message)
            finally:
                if pfile is not None:
                    pfile.close()
            
            # Se almacena
            cls.recursos[nombre] = datos
            # Se devuelve
            return datos

    @classmethod
    def CargarArchivoFaseJSON(cls, nombre):
        # Si el nombre de archivo está entre los recursos ya cargados
        nombre += '.json'
        if nombre in cls.recursos:
            # Se devuelve ese recurso
            return cls.recursos[nombre]

        # Si no ha sido cargado anteriormente
        else:
            # Se carga el recurso indicando el nombre de su carpeta
            fullname = os.path.join('fases', nombre)

            f = None
            try:
                f = open(fullname, 'r')
                datos = json.load(f)
            except pygame.error as message:
                print('Cannot load JSON file:', fullname)
                raise SystemExit(message)
            finally:
                if f is not None:
                    f.close()
            
            cls.recursos[nombre] = datos
            return datos  

