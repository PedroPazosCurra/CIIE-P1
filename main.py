import os
import pygame
import sys
import jugador
import director
import fase
from fase import *
from director import *
from jugador import *
from pygame.locals import *

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
# Funcion principal del juego
# -------------------------------------------------

def main():

    # Inicializar pygame
    pygame.init()
    
    # Crear el director
    director = Director()
    
    """
    # Crear la pantalla
    pantalla = pygame.display.set_mode((800, 600), 0, 32)

    # Creamos el objeto reloj para sincronizar el juego
    reloj = pygame.time.Clock()

    # Poner el título de la ventana
    pygame.display.set_caption('Juego panadero')
    
    """
    
    fase = Fase(director)
    director.apilarEscena(fase)
    
    director.ejecutar()
    pygame.quit()
    
    """    
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
    """


if __name__ == "__main__":
    main()
