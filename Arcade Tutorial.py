"""
Platformer Game
"""
# Imports arcade library
import arcade

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
SCREEN_TITLE = "Sam's Platformer"
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Inherits methods from parent class (Window)
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Initialises scene, player_sprite, camera, and physics_engine attributes
        """self.scene = None
        self.player_sprite = None
        self.physics_engine = None
        self.camera = None"""

        # Sets background colour for the window using arcade's provided colours
        arcade.set_background_color(arcade.csscolor.INDIGO)

    def setup(self):
        """Set up the game here. Call this method to restart the game."""

        # Initialises the Scene class
        self.scene = arcade.Scene()

        # Adds "Player" anbd "Walls" sprite lists to the Scene class
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True) # Spatial hashing improves collision detection for stationary sprites

        # Adds information for player sprite including image and position
        image_source = ":resources:images/animated_characters/male_adventurer/maleAdventurer_idle.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.position = 64, 128

        # Adds player sprite to "Player" sprite list
        self.scene.add_sprite("Player", self.player_sprite)

        # Loops to add grass & wall sprites at equal intervals (64 pixels) to form the floor and left wall
        for x in range(0, 1314, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        for y in range(96, 416, 64):
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", TILE_SCALING)
            wall.center_x = 32
            wall.center_y = y
            self.scene.add_sprite("Walls", wall)

        # List of coordinates at which to place wall sprites (units are pixels)
        coordinate_list = [[512, 96], [256, 96], [768, 96], [576, 224], [640, 224], [704, 224], [768, 224], [960, 416], [1152, 608], [1344, 800], [1536, 992]]

        # Iterates through list of coordinates and adds wall sprites at the specified locations
        for coordinate in coordinate_list:
            wall = arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png", TILE_SCALING
            )
            wall.position = coordinate
            self.scene.add_sprite("Walls", wall)

        # Creates the physics engine, passing in the player sprite, grvaity constant, and list of wall sprites
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Walls"]
        )

        # Initialises camera
        self.camera = arcade.Camera(self.width, self.height)

    def center_camera_to_player(self):
        """"""

        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
            
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def on_draw(self):
        """Clears and re-renders the scene every frame."""

        self.clear()
        self.camera.use()
        self.scene.draw()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Move the player with the physics engine
        self.physics_engine.update()

        # Calls center_camera_to_player method
        self.center_camera_to_player()

        if self.player_sprite.center_y < 0:
            self.player_sprite.position = 64, 128

def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()