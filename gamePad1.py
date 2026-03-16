import pygame
import sys

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------
DEADZONE = 0.1  # seuil minimal pour ignorer le drift analogique

BUTTON_MAP = {
    0: "triangle",
    1: "circle",
    2: "cross",
    3: "square",
    4: "L1",
    5: "R1",
    6: "L2",
    7: "R2",
    8: "select",
    9: "start",
    10: "L3",
    11: "R3",
}

AXIS_MAP = {
    0: "left_x",
    1: "left_y",
    2: "right_x",
    3: "right_y",
}

class GamepadManager:
    """
    Classe gérant l'initialisation des manettes,
    le hot-plug, et le dispatch des événements
    vers votre logique de jeu.
    """
    def __init__(self, game):
        pygame.init()
        pygame.joystick.init()
        self.game = game
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pygame : Gestion Manettes PS4")
        self.clock = pygame.time.Clock()
        self.joysticks = []
        self.init_joysticks()

    def init_joysticks(self):
        """Initialise toutes les manettes détectées"""
        count = pygame.joystick.get_count()
        for idx in range(count):
            js = pygame.joystick.Joystick(idx)
            js.init()
            print(f"[INIT] Manette {idx} : {js.get_name()} "
                  f"(axes={js.get_numaxes()} boutons={js.get_numbuttons()} hats={js.get_numhats()})")
            self.joysticks.append(js)
        if not self.joysticks:
            print("⚠️ Aucune manette détectée au démarrage.")

    def add_joystick(self, device_index):
        """Ajout d'une manette à chaud"""
        js = pygame.joystick.Joystick(device_index)
        js.init()
        self.joysticks.append(js)
        print(f"[HOTPLUG] Manette ajoutée : {js.get_name()} (instance_id={js.get_instance_id()})")

    def remove_joystick(self, instance_id):
        """Retrait d'une manette à chaud"""
        for js in self.joysticks:
            if js.get_instance_id() == instance_id:
                print(f"[HOTPLUG] Manette retirée : {js.get_name()} (instance_id={instance_id})")
                self.joysticks.remove(js)
                break

    def handle_event(self, event):
        """Traite un événement pygame lié aux manettes"""
        if event.type == pygame.JOYDEVICEADDED:
            self.add_joystick(event.device_index)

        elif event.type == pygame.JOYDEVICEREMOVED:
            self.remove_joystick(event.instance_id)

        elif event.type == pygame.JOYBUTTONDOWN:
            name = BUTTON_MAP.get(event.button, f"btn_{event.button}")
            
            if name == "cross":
                self.game.validate_menu_selection()
            else:
                self.game.handle_button_down(name)


        elif event.type == pygame.JOYBUTTONUP:
            name = BUTTON_MAP.get(event.button, f"btn_{event.button}")
            self.game.handle_button_up(name)

        elif event.type == pygame.JOYAXISMOTION:
            axis_name = AXIS_MAP.get(event.axis, f"axis_{event.axis}")
            val = event.value
            if abs(val) < DEADZONE:
                val = 0.0
            self.game.handle_axis_motion(axis_name, val)

        
        elif event.type == pygame.JOYHATMOTION:
            x, y = event.value
            if y == 1:
                self.game.navigate_menu("up")
            elif y == -1:
                self.game.navigate_menu("down")
            elif x == 1:
                self.game.navigate_menu("right")
            elif x == -1:
                self.game.navigate_menu("left")

            self.game.handle_dpad(event.value)

    def run(self):
        """Boucle principale"""
        running = True
        while running:
            dt = self.clock.get_time() / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    self.handle_event(event)

            # Mise à jour du jeu
            self.game.update(dt)

            # Rendu
            self.screen.fill((30, 30, 30))
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


