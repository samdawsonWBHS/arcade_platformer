"""
Platformer Game - ADD COMMENTS AND DOCSTRINGS, ENSURE LINE LENGTH < 80
"""
# Imports
import arcade
import os

# Constants for the game window
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN_TITLE = "Sam's Platformer"

# Constants to scale sprites
CHARACTER_SCALING = 0.8
TILE_SCALING = 0.5
COIN_SCALING = 0.5

# Constants for sprite movement
PLAYER_MOVEMENT_SPEED = 5
PLAYER_JUMP_SPEED = 20
GRAVITY = 1

MAIN_PATH = os.path.dirname(os.path.abspath(__file__))

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Inherit methods from arcade parent class (Window)
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Initialise instance variables
        self.scene = None
        self.player_sprite = None
        self.physics_engine = None
        self.camera = None
        self.gui_camera = None
        self.score = 0
        self.tile_map = None

        # Instance variables for sound effects
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

        # Set background for the game window using arcade's built-in colours
        arcade.set_background_color(arcade.csscolor.INDIGO)

    def setup(self):
        """
        Set up the game here. Call this method to restart the game.
        """

        # Dictionary to specify options for individual layers e.g. spatial hash for the platforms SpriteList
        layer_options = {
            "Platforms": {"use_spatial_hash": True,}
        }

        map_name = f"{MAIN_PATH}/first_map.tmx"

        # Loads tile map in to tile_map variable
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Create SpriteList for wall sprites - spatial hashing improves collision detection for stationary sprites
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)

        # Create player_sprite as an instance of arcade's 'Sprite' class
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/male_adventurer/maleAdventurer_idle.png", CHARACTER_SCALING)

        # Set spawn point for player
        self.player_sprite.position = 64, 128

        # Add player sprite to "Player" sprite list
        self.scene.add_sprite("Player", self.player_sprite)

        # Sets the foreground layer to be rendered behind the player sprite
        self.scene.add_sprite_list_before("Player", "Foreground")

        # Create 'camera' variable as an instance of arcade's 'Camera' class - main camera
        self.camera = arcade.Camera(self.width, self.height)

        # Create 'gui_camera' variable as an instance of arcade's 'Camera' class - camera only for gui e.g. score
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Resets 'score' variable
        self.score = 0

        # Set the background color of the specific tile map - overrides window background colour
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Create the 'physics engine' passing in the player sprite, gravity constant, and Platforms layer of the tile map
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Platforms"]
        )

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

        self.gui_camera.use()

        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10, 10, arcade.csscolor.WHITE, 18)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
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

        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.scene["Coins"])

        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 1

def main():
    """Main function"""

    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()