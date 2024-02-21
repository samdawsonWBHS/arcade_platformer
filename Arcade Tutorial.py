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

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Inherits methods from parent class (Window)
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Initialises scene and player_sprite attributes
        self.scene = None
        self.player_sprite = None

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

        for x in range(0, 1250, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        coordinate_list = [[512, 96], [256, 96], [768, 96], [576, 224], [640, 224], [704, 224], [768, 224]]

        for coordinate in coordinate_list:
            wall = arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png", TILE_SCALING
            )
            wall.position = coordinate
            self.scene.add_sprite("Walls", wall)

    def on_draw(self):
        """Render the screen."""

        self.clear()

        self.scene.draw()

def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()