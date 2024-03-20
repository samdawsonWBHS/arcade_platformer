"""
Platformer Game
"""

# Imports
import arcade
from arcade.experimental.lights import Light, LightLayer
import os

AMBIENT_COLOR = (10, 10, 10)

# Constants for the game window
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN_TITLE = "Sam's Platformer"
WINDOW_COLOUR = arcade.csscolor.IVORY

# Constants to scale sprites
CHARACTER_SCALING = 0.8
TILE_SCALING = 0.5
COIN_SCALING = 0.5

# Constants for sprite movement
PLAYER_MOVEMENT_SPEED = 5
PLAYER_JUMP_SPEED = 20
GRAVITY = 1
PLAYER_SPAWN_X = 64
PLAYER_SPAWN_Y = 128

# Layer Names from our TileMap
LAYER_NAME_FOREGROUND = "Foreground"
LAYER_NAME_PLATFORMS = "Platforms"
LAYER_NAME_MOVING_PLATFORMS = "Moving Platforms"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_LADDERS = "Ladders"
LAYER_NAME_DANGERS = "Dangers"
LAYER_NAME_PLAYER = "Player"

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

MAIN_PATH = os.path.dirname(os.path.abspath(__file__))

def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True),
    ]

class PlayerCharacter(arcade.Sprite):
    """Player Sprite"""

    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Track our state
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

        # --- Load Textures ---

        # Images from Kenney.nl's Asset Pack 3
        main_path = ":resources:images/animated_characters/male_adventurer/maleAdventurer"

        # Load textures for idle standing
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")
        self.jump_texture_pair = load_texture_pair(f"{main_path}_jump.png")
        self.fall_texture_pair = load_texture_pair(f"{main_path}_fall.png")

        # Load textures for walking
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Load textures for climbing
        self.climbing_textures = []
        for i in range(2):
            texture = arcade.load_texture(f"{main_path}_climb{i}.png")
            self.climbing_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # set_hit_box = [[-22, -64], [22, -64], [22, 28], [-22, 28]]
        self.hit_box = self.texture.hit_box_points

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Climbing animation
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return

        # Jumping animation
        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][
            self.character_face_direction
        ]

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
        self.level = 1

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        # Instance variables for sound effects
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

        # Set background for the game window using arcade's built-in colours
        arcade.set_background_color(WINDOW_COLOUR)

        # List of all the lights
        self.light_layer = None
        # Individual light we move with player, and turn on/off
        self.player_light = None

    def setup(self):
        """
        Set up the game here. Call this method to restart the game.
        """

        # Dictionary to specify options for individual layers e.g. spatial hash for the platforms SpriteList
        layer_options = {
            LAYER_NAME_PLATFORMS: {"use_spatial_hash": True,},
            LAYER_NAME_MOVING_PLATFORMS: {"use_spatial_hash": True,},
            LAYER_NAME_LADDERS: {"use_spatial_hash": True,},
            LAYER_NAME_COINS: {"use_spatial_hash": True,}
        }

        # Sets map file name based on current level
        map_name = f"{MAIN_PATH}/map_level_{self.level}.tmx"

        # Loads tile map in to tile_map variable
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)

        # Initialize Scene with our TileMap, this will automatically add all layers
        # from the map as SpriteLists in the scene in the proper order
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerCharacter()
        self.player_sprite.position = PLAYER_SPAWN_X, PLAYER_SPAWN_Y
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player_sprite)

        # Sets the foreground layer to be rendered behind the player sprite
        self.scene.add_sprite_list_before(LAYER_NAME_PLAYER, LAYER_NAME_FOREGROUND)

        # Create 'camera' variable as an instance of arcade's 'Camera' class - main camera
        self.camera = arcade.Camera(self.width, self.height)

        # Create 'gui_camera' variable as an instance of arcade's 'Camera' class - camera only for gui e.g. score
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Resets 'score' variable
        self.score = 0

        # Set the background color of the specific tile map - overrides window background colour
        if self.tile_map.background_color:
            arcade.set_background_color(self.tile_map.background_color)

        # Create the physics engine, passing in the player sprite, gravity constant, and Platforms layer of the tile map
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, gravity_constant=GRAVITY, walls=self.scene[LAYER_NAME_PLATFORMS],
            platforms=self.scene[LAYER_NAME_MOVING_PLATFORMS], ladders=self.scene[LAYER_NAME_LADDERS]
        )

        # Create a light layer, used to render things to, then post-process and
        # add lights. This must match the screen size.
        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        # We can also set the background color that will be lit by lights,
        # but in this instance we just want a black background
        self.light_layer.set_background_color(arcade.color.BLACK)

        # Create a light to follow the player around.
        # We'll position it later, when the player moves.
        # We'll only add it to the light layer when the player turns the light
        # on. We start with the light off.
        radius = 150
        mode = 'soft'
        color = arcade.csscolor.WHITE
        self.player_light = Light(0, 0, radius, color, mode)

    def center_camera_to_player(self):
        """
        Update every frame to relocate camera to player.
        """
        
        # Set the intended center of the screen to the coordinates of the player sprite
        # Subtract half the viewport size in each direction since the anchor point is bottom left of screen not centre
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past map boundaries
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_x > 1280:
            screen_center_x = 1280
        if screen_center_y < 0:
            screen_center_y = 0
            
        # Defines the coordinates of the camera to be centered on player
        player_centered = screen_center_x, screen_center_y

        # Moves camera to correct position
        self.camera.move_to(player_centered)

    def on_draw(self):
        """Clears and re-renders the scene every frame."""

        # Clears current frame, initialises camera for use, then renders spritelists
        self.clear()

        self.camera.use()

        # Everything that should be affected by lights gets rendered inside this
        # 'with' statement. Nothing is rendered to the screen yet, just the light
        # layer.
        with self.light_layer:
            self.scene.draw()

        # Initialises gui_camera for use to draw the score
        self.gui_camera.use()

        # Draw the light layer to the screen.
        # This fills the entire screen with the lit version
        # of what we drew into the light layer above.
        self.light_layer.draw(ambient_color=AMBIENT_COLOR)

        # Draws current score (number of diamonds collected in level)
        score_text = f"Diamonds Collected: {self.score}/3"
        arcade.draw_text(score_text, 10, 10, arcade.csscolor.WHITE, 18)

<<<<<<< HEAD
        arcade.draw_text("Press SPACE to turn character light on/off.",
                         10, 100, arcade.color.WHITE, 18)
=======
    def process_keychange(self):
        """
        Called when we change a key up/down or we move on/off a ladder.
        """
        # Process up/down
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif (
                self.physics_engine.can_jump(y_distance=10)
                and not self.jump_needs_reset
            ):
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Process up/down when on a ladder and no movement
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0
>>>>>>> 039a7a3a16c27e3e375c26b2abd050f53faf7d7c

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
<<<<<<< HEAD
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.SPACE:
            # --- Light related ---
            # We can add/remove lights from the light layer. If they aren't
            # in the light layer, the light is off.
            if self.player_light in self.light_layer:
                self.light_layer.remove(self.player_light)
            else:
                self.light_layer.add(self.player_light)
=======
            self.right_pressed = True
>>>>>>> 039a7a3a16c27e3e375c26b2abd050f53faf7d7c

        if key == arcade.key.MOD_SHIFT:
            self.score = 3

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def on_update(self, delta_time):
        """Movement and game logic - running constantly"""

        # Move the player with the physics engine
        self.physics_engine.update()

        # Calls center_camera_to_player method to keep the player centered on screen
        self.center_camera_to_player()

<<<<<<< HEAD
        # Update Animations
        self.scene.update_animation(delta_time, self.player_sprite)
=======
        # Update animations
        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        # Update player_sprite animations
        self.player_sprite.update_animation(delta_time)
>>>>>>> 039a7a3a16c27e3e375c26b2abd050f53faf7d7c

        # Update walls, used with moving platforms
        self.scene.update([LAYER_NAME_MOVING_PLATFORMS])

        # If player sprite falls below map, respawn at spawn point
        if self.player_sprite.center_y < 0:
            self.player_sprite.position = PLAYER_SPAWN_X, PLAYER_SPAWN_Y

        # If player sprite contacts a coin, add coin to coin_hit_list
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.scene["Coins"])

        # Coins in hit list are removed from coin spritelist, while a sound is played and score increased
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 1

        # Moves to next level once score reaches 3 with all level diamonds collected - setup method called to reset everything
        if self.score == 3:
            self.level += 1
            self.reset_score = True
            self.setup()

        # --- Light related ---
        # We can easily move the light by setting the position,
        # or by center_x, center_y.
        self.player_light.position = self.player_sprite.position

def main():
    """Main function"""

    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()