"""
Platformer Game - ADD COMMENTS AND DOCSTRINGS, ENSURE LINE LENGTH < 80
"""
# Imports arcade library
import arcade

# Constants to be passed into arcade classes
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
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

        # Inherit methods from parent class (arcade.Window)
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Initialise scene, player_sprite, camera, and physics_engine
        # instance variables (best practice)
        self.scene = None
        self.player_sprite = None
        self.physics_engine = None
        self.camera = None

        # Set background for the game window using arcade's built-in colours
        arcade.set_background_color(arcade.csscolor.INDIGO)

    def setup(self):
        """
        Set up the game here. Call this method to restart the game.
        """

        # Create an instance of the Scene class, saved within the 'scene' instance variable
        self.scene = arcade.Scene()

        # Add "Player" and "Walls" sprite lists to the scene variable - sprite lists allow for batch drawing sprites, improving performance
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True) # Spatial hashing improves collision detection *for stationary sprites*

        # Create instance of Sprite class which will be used as the player_sprite
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/male_adventurer/maleAdventurer_idle.png", CHARACTER_SCALING)
        self.player_sprite.position = 64, 128

        # Add player sprite to "Player" sprite list
        self.scene.add_sprite("Player", self.player_sprite)

        # Loops add grass & wall sprites at equal intervals (64 pixels) to form the floor and left wall
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

        # List pixel coordinates for wall sprite placement - (0,0) is bottom left of window
        coordinate_list = [[384, 96], [256, 96], [768, 96], [576, 224], [640, 224], [704, 224], [768, 224], [960, 416], [1152, 608], [1344, 800], [1536, 992]]

        # Iterate through list of coordinates and add wall sprites at the specified locations
        for coordinate in coordinate_list:
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", TILE_SCALING)
            wall.position = coordinate
            self.scene.add_sprite("Walls", wall)

        # Create the physics engine, passing in the player sprite, grvaity constant, and list of wall sprites
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Walls"])

        # Initialise camera
        self.camera = arcade.Camera(self.width, self.height)

    def center_camera_to_player(self):
        """ADD COMMENTS AND DOCSTRINGS FROM HERE"""

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