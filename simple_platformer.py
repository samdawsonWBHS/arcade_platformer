"""
Platformer Game
"""
# Imports
import arcade
import os

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
        main_path = ":resources:images/animated_characters/male_person/malePerson"

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
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
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

        # Create player_sprite as an instance of arcade's 'Sprite' class
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/male_adventurer/maleAdventurer_idle.png", CHARACTER_SCALING)

        # Set spawn point for player
        self.player_sprite.position = PLAYER_SPAWN_X, PLAYER_SPAWN_Y

        # Add player sprite to "Player" sprite list
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
        self.scene.draw()

        # Initialises gui_camera for use to draw the score
        self.gui_camera.use()

        # Draws current score (number of diamonds collected in level)
        score_text = f"Diamonds Collected: {self.score}/3"
        arcade.draw_text(score_text, 10, 10, arcade.csscolor.WHITE, 18)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

        if key == arcade.key.SPACE:
            self.score = 3

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
        """Movement and game logic - running constantly"""

        # Move the player with the physics engine
        self.physics_engine.update()

        # Calls center_camera_to_player method to keep the player centered on screen
        self.center_camera_to_player()

        # Update Animations
        self.scene.update_animation(
            delta_time, [LAYER_NAME_COINS, LAYER_NAME_BACKGROUND, self.player_sprite]
        )

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

def main():
    """Main function"""

    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()