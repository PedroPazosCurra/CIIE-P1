import pygame
from director import Director
from menu import Menu

# -------------------------------------------------
# Funcion principal del juego
# -------------------------------------------------

def main():

    # Inicializar pygame
    pygame.init()
    
    # Crear el director
    director = Director()

    # Creamos escena de pantalla inicial
    #fase = Fase(director)
    escena = Menu(director)

    # Director, apila esa escena inicial
    director.apilarEscena(escena)

    # Director, ejecuta el juego
    director.ejecutar()

    # Listo
    pygame.quit()


if __name__ == "__main__":
    main()
