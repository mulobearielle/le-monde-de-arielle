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
    3: "axis_3",  
    4: "axis_4", # souvent L2
    5: "axis_5",  # souvent R2

}

class GamepadManager:
    def __init__(self, game):
        pygame.init()
        pygame.joystick.init()
        self.game = game
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pygame : Gestion Manettes Universelle")
        self.clock = pygame.time.Clock()
        self.joysticks = []
        self.joystick_mappings = {}
        self.init_joysticks()

    def get_button_map(self, joystick_name):
        if "PS4" in joystick_name or "Wireless Controller" in joystick_name or "Xbox 360 Controller" in joystick_name:
            return {
                0: "cross",
                1: "circle",
                2: "square",
                3: "triangle",
                4: "L1",
                5: "R1",
                6: "share",
                7: "options",
                8: "L3",
                9: "R3",
                10: "PS"
            }
        else:
            return BUTTON_MAP

    def init_joysticks(self):
        count = pygame.joystick.get_count()
        for idx in range(count):
            js = pygame.joystick.Joystick(idx)
            js.init()
            name = js.get_name()
            print(f"[INIT] Manette {idx} : {name} (axes={js.get_numaxes()} boutons={js.get_numbuttons()} hats={js.get_numhats()})")
            self.joysticks.append(js)
            self.joystick_mappings[js.get_instance_id()] = self.get_button_map(name)

        if not self.joysticks:
            print("⚠️ Aucune manette détectée au démarrage.")

    def add_joystick(self, device_index):
        js = pygame.joystick.Joystick(device_index)
        js.init()
        self.joysticks.append(js)
        self.joystick_mappings[js.get_instance_id()] = self.get_button_map(js.get_name())
        print(f"[HOTPLUG] Manette ajoutée : {js.get_name()} (instance_id={js.get_instance_id()})")

    def remove_joystick(self, instance_id):
        for js in self.joysticks:
            if js.get_instance_id() == instance_id:
                print(f"[HOTPLUG] Manette retirée : {js.get_name()} (instance_id={instance_id})")
                self.joysticks.remove(js)
                break

    def handle_event(self, event):
        if event.type == pygame.JOYDEVICEADDED:
            self.add_joystick(event.device_index)

        elif event.type == pygame.JOYDEVICEREMOVED:
            self.remove_joystick(event.instance_id)

        elif event.type == pygame.JOYBUTTONDOWN:
            btn_map = self.joystick_mappings.get(event.instance_id, BUTTON_MAP)
            name = btn_map.get(event.button, f"btn_{event.button}")
            print(f"[MANETTE] (id={event.instance_id}) Bouton pressé : {event.button} => {name}")
            if name == "cross" or name == "A":
                self.game.validate_menu_selection()
            else:
                self.game.handle_button_down(name)

        elif event.type == pygame.JOYBUTTONUP:
            btn_map = self.joystick_mappings.get(event.instance_id, BUTTON_MAP)
            name = btn_map.get(event.button, f"btn_{event.button}")
            self.game.handle_button_up(name)

        elif event.type == pygame.JOYAXISMOTION:
            axis_name = AXIS_MAP.get(event.axis, f"axis_{event.axis}")
            val = event.value
            if abs(val) < DEADZONE:
                val = 0.0
            self.game.handle_axis_motion(axis_name, val)

            # Gestion des gâchettes analogiques comme boutons
            if axis_name == "axis_4" and val > 0.5:
                self.game.handle_button_down("L2")
            elif axis_name == "axis_4" and val <= 0.5:
                self.game.handle_button_up("L2")
            if axis_name == "axis_5" and val > 0.5:
                self.game.handle_button_down("R2")
            elif axis_name == "axis_5" and val <= 0.5:
                self.game.handle_button_up("R2")

        elif event.type == pygame.JOYHATMOTION:
            x, y = event.value
            if y == 1:
                self.game.navigate_menu("up")
                #self.game.handle_button_down("Haut")
            elif y == -1:
                self.game.navigate_menu("down")
                #self.game.handle_button_down("Bas")
            elif x == 1:
                self.game.navigate_menu("right")
                #self.game.handle_button_down("Droite")
            elif x == -1:
                self.game.navigate_menu("left")
                #self.game.handle_button_down("Gauche")
            #elif x == 0 and y == 0:
            #    for d in ["Haut", "Bas", "Gauche", "Droite"]:
            #        self.game.handle_button_up(d)
            self.game.handle_dpad(event.value)

    def run(self):
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

            self.game.update(dt)
            self.screen.fill((30, 30, 30))
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


# --------------------------------------------------
# BLOC DE TEST TERMINAL
# --------------------------------------------------
if __name__ == "__main__":
    class DummyGame:
        def validate_menu_selection(self): print("✅ Sélection validée")
        def handle_button_down(self, name): print(f"🔘 Bouton pressé : {name}")
        def handle_button_up(self, name): print(f"🔄 Bouton relâché : {name}")
        def handle_axis_motion(self, axis, value): print(f"🕹️ Axe {axis} → {value:.2f}")
        def handle_dpad(self, value): print(f"🎯 D-Pad : {value}")
        def navigate_menu(self, direction): print(f"➡️ Navigation menu : {direction}")
        def update(self, dt): pass

    GamepadManager(DummyGame()).run()
