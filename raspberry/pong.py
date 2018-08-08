
#!/usr/bin/env python3

from time import sleep
import uuid
import random
import paho.mqtt.client as mqtt
from pixel_art import PixelArt

# Import the fake sense hat module if available
# We do this because we need a pong game to run on non-raspberry devices 
# (using a Tkinter interface) to use it as a debugging platform and because
# sometimes a pi is not available
# If the "normal" module is not found, just import the "fake" API
try:
    from sense_hat import SenseHat
except ImportError:
    from fake_sense_hat import SenseHat
    pass

DEBUG_WALLS = False

class Vector_2d(object):
    """Dead simple 2D vector class"""
    x = 0;
    y = 0;

class Ball:
    """ Class that implements the Pong ball"""
    def __init__(self, init_velocity_x, init_velocity_y, hat):
        """Set ball to inital values"""
        self.position = Vector_2d()
        self.velocity = Vector_2d()
        self.velocity.x = init_velocity_x
        self.velocity.y = init_velocity_y
        self.init_velocity_x = init_velocity_x
        self.init_velocity_y = init_velocity_y
        self.position.x = 7
        self.position.y = 3
        self.deflection = 1
        self.hat = hat

    def reinit(self):
        """Re-initialise the ball to the default location"""
        self.velocity.x = self.init_velocity_x
        self.velocity.y = self.init_velocity_y
        self.position.x = 7
        self.position.y = 3
        self.deflection = 1

    def set(self, x_pos, y_pos, x_vel, y_vel):
        """Set ball position and velocity"""
        self.position.x = x_pos
        self.position.y = y_pos
        self.velocity.x = x_vel
        self.velocity.y = y_vel

    def draw(self):
        """Draw the ball in the current position"""
        # The color is always the same dull white
        self.hat.set_pixel(int(self.position.x), int(self.position.y), 100, 100, 100)

    def move(self):
        """Move the ball according to the set velocity"""
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

class Paddle():
    """ Class that implements the Pong paddle (the thing you hit the ball with)"""
    def __init__(self, height, hat):
        self.position = Vector_2d()
        self.position.x = 0
        self.position.y = 7
        self.height = height
        self.hat = hat

    def draw(self):
        """Draw the paddle in the current position"""

        # The paddle is a range of pixels that are to be drawn horizontally on the last row
        # of pixels
        # The color is always the same dull white
        for pixel in range(self.position.y - self.height, self.position.y):
            self.hat.set_pixel(int(self.position.x), int(pixel), 100, 100, 100)

    def move(self, hat):
        """Move the paddle according to user input"""

        # Get a joystick press event from the sense hat
        for event in hat.stick.get_events():
            if event.direction == "up":
                print("up: " + str((self.position.y - self.height - 1)))
                if (self.position.y - self.height - 1) < 0:
                    print("Paddle limit UP")
                else:
                    # FIXME: Directions are mirrored, so move down when up is pressed 
                    self.position.y -= 1
            elif event.direction == "down":
                print("down: " + str((self.position.y + 1)))
                if (self.position.y + 1) > 8:
                    print("Paddle limit DOWN")
                else:
                    # FIXME: Directions are mirrored
                    self.position.y += 1

def intra_object_collision_detection(ball, paddle):
    """This function detects and retruns a collision event between ball, paddle, edges and walls. A touple of booleans is
       return, the first boolean denoting a score and the second a collision between the ball and something else"""
    # Set this to true if there has been a goal scored
    score = False

    # Ball colides with the paddle, mirror x velocity (relfect)
    if (frange(ball.position.y, paddle.position.y - paddle.height, paddle.position.y)) and (ball.position.x <= 1):
        print("PADDLE COLLISION")
        ball.velocity.x = -ball.velocity.x
    
    # An x position smaller or equal to 1 denotes a goal scored
    elif ball.position.x <= 1:
        print("SCORE")
        score = True 
    # An x position larger or equal to 7 denotes a wall collision (edge, pass the ball to the other player)
    elif ball.position.x >= 7:
        print("WALL COLLISION")
        ball.velocity.x = -ball.velocity.x

        # Return no score, just out of bounds
        return False, True
    
    # An y position larger or equal to 7 or smaller or equal to 0 denotes a side wall collision (reflect)
    if not frange(ball.position.y, 0, 7):
        print("SIDEWALL COLLISION")
        ball.velocity.y = -ball.velocity.y

    # Make sure the ball and paddle is within bounds
    ball.position.x = realign(ball.position.x, 0, 7)
    ball.position.y = realign(ball.position.y, 0, 7)
    paddle.position.x = realign(paddle.position.x, 0, 7)
    paddle.position.y = realign(paddle.position.y, paddle.height, 7)

    # Return if there has been a score
    return score, False
    
def realign(value, range_min, range_max):
    """This function re-aligns a value within a min and max bound by rounding it
       to the nearest range value""" 
    if value >= range_max:
        value = range_max
    if value <= range_min:
        value = range_min

    return value

def frange(value, range_min, range_max):
    """Returns true if a value is within a certain range"""
    if (value < range_min) or (value > range_max):
        return False
    return True

def fill_color(hat, color):
    """Fills the SenseHat screen with a certain color"""
    hat.set_pixels([color] * 8 * 8)

def on_connect(client, userdata, flags, rc):
    """The callback for when the client receives a CONNACK response from the server."""

    print("Connected with result code " + str(rc))

    # Subscribe to the session topic, we are going to subscribe to the enemy player topic
    # when a game is started
    client.subscribe("thm_rr_iot_project/session/#")
    #client.publish("thm_rr_iot_project/session/id", payload=None, retain=True)
    #client.publish("thm_rr_iot_project/session/game", payload=None)
    #client.publish("thm_rr_iot_project/player0/score", payload=None, retain=True)
    #client.publish("thm_rr_iot_project/player1/score", payload=None, retain=True)
    client.connected_flag = True

def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(msg.topic + " " + str(msg.payload))

    # The current session ID is published, check if it is ours, otherwise start a new enemy-initiated
    # game
    if msg.topic == "thm_rr_iot_project/session/id" and msg.payload.decode("utf-8") != client.session_id:
        client.session_id = msg.payload.decode("utf-8")
        client.new_game_flag = True

        # Subscribe to enemy and unsubscribe from our own topic for safety
        client.subscribe("thm_rr_iot_project/player0/#")
        client.unsubscribe("thm_rr_iot_project/player1/#")

    # Set the difficulty, this value is saved as retain from the webapp
    if msg.topic == "thm_rr_iot_project/session/difficulty":
        client.difficulty = int(msg.payload.decode("utf-8"))

    # Set the winning score, this value is saved as retain from the webapp
    if msg.topic == "thm_rr_iot_project/session/winning_score":
        client.winning_score = int(msg.payload.decode("utf-8"))

    # Receive a pass
    if msg.topic == "thm_rr_iot_project/player" + ("1" if client.game_initiator else "0") + "/pass":
        if msg.payload.decode("utf-8") != "":
            client.pass_received_flag = True
            # Get the ball values from the pass
            client.pass_value_pos_x, client.pass_value_pos_y, client.pass_value_vel_x, client.pass_value_vel_y = comma_seperated_float_tuple_decode(msg.payload.decode("utf-8"))

    # Receive a message for a scored goal
    if msg.topic == "thm_rr_iot_project/player" + ("1" if client.game_initiator else "0") + "/score":
        client.goals_scored = int(msg.payload.decode("utf-8"))
        client.goal_scored_flag = True

    if msg.topic == "thm_rr_iot_project/player" + ("1" if client.game_initiator else "0") + "/game":
        session_id, name = comma_seperated_string_tuple_decode(msg.payload.decode("utf-8"))

        if session_id == client.session_id:
            client.enemy_name = name

def pass_ball_string(ball):
    """This creates a string that describes a ball pass to the other player"""
    return str(ball.position.x) + "," + str(ball.position.y) + "," + str(ball.velocity.x) + "," + str(ball.velocity.y)

def comma_seperated_float_tuple_decode(string):
    print(str(tuple(map(float, string.split(',')))))
    return tuple(map(float, string.split(',')))

def comma_seperated_string_tuple_decode(string):
    print(str(tuple(string.split(','))))
    return tuple(string.split(','))


def new_game(client, fade):
    """Wait for a new game, either player or enemy initiated. Returns a touple of booleans.
       The first boolean denotes if a new game was started, the second boolean denotes
       if it was us who started the game"""
    hat.set_pixels(pa.fade(pa.make_up_arrow(), fade))

    # Other player initiated game
    if client.new_game_flag:
        # Reset flag
        #client.publish("thm_rr_iot_project/session/game", payload="")
        client.new_game_flag = False
        return True, False

    for event in hat.stick.get_events():
        if event.direction == "up":
            sleep(random.uniform(0.1, 2.0))

            if client.new_game_flag == False:
                client.session_id = str(uuid.uuid4())
                print("Creating game:" +  client.session_id)
                client.publish("thm_rr_iot_project/session/id", payload=client.session_id)
                client.unsubscribe("thm_rr_iot_project/player0/#")
                client.subscribe("thm_rr_iot_project/player1/#")
                return True, True
            else:
                client.new_game_flag = False
                return True, False
    
    return False, False

def next_letter(letter):

    # Only support uppercase
    letter = letter.upper()

    if letter == 'Z':
        return ' '
    elif letter == ' ':
        return 'A'
    else:
        return chr(ord(letter) + 1)

def previous_letter(letter):

    # Only support uppercase
    letter = letter.upper()

    if letter == 'A':
        return ' '
    elif letter == ' ':
        return 'Z'
    else:
        return chr(ord(letter) - 1)

def select_name():
    blink = 0
    name = ["A", "A", "A"]
    current_letter = "A"
    index = 0
    print(str(pa.make_letter(current_letter)))
    hat.set_pixels(pa.make_letter(current_letter))

    while True:
        for event in hat.stick.get_events():
            if event.direction == "up":
                current_letter = next_letter(current_letter)
            elif event.direction == "down":
                current_letter = previous_letter(current_letter)
            elif event.direction == "right":
                # Set letter and get next letter
                name[index] = current_letter
                
                index += 1
                print(str(len(name)))
                
                # All letters set, return the name as a string
                if index > (len(name) - 1):
                    return ''.join(name)
                
                current_letter = name[index];
            elif event.direction == "left":
                # Set letter and get next letter
                name[index] = current_letter
                
                index -= 1
                
                # Can't go lower than zero
                if index < 0:
                    index = 0
                
                current_letter = name[index];

        if blink < 2:
            hat.set_pixels(pa.make_letter(current_letter))
        else:
            fill_color(hat, [0, 0, 0])

        if blink > 4:
            blink = 0

        blink += 1

        sleep(0.30)


#######################################################
# Game loop
#######################################################

# Create mqtt client
client = mqtt.Client()

# Set mqtt callbacks
client.on_connect = on_connect
client.on_message = on_message

# Set game and session flags
client.connected_flag = False
client.new_game_flag = False
client.pass_received_flag = False
client.session_id = ""
client.difficulty = 1
client.winning_score = 9
client.game_initiator = False
client.goals_scored = 0
client.goals_suffered = 0
client.goal_scored_flag = False
client.pass_value_pos_x = 0
client.pass_value_pos_y = 0
client.pass_value_vel_x = 0
client.pass_value_vel_y = 0

client.name = ""
client.enemy_name = ""

# Connect to broker
client.connect("iot.eclipse.org", 1883, 60)
client.loop_start()

# Create pixel art object
pa = PixelArt()

# Create sense hat object
hat = SenseHat()

# Create ball and paddle
ball = Ball(-1, 0.5, hat)
paddle = Paddle(3, hat)

# Set state machine initial state
next_stage = "wait_for_connection"


# Those are some counters that help with
# some pixel art visualizations (loading, up-arrow etc)
i = 0; # Counts up to 100 and then down to 0 again
inc = 1 # Increment for i
scan = 0 # Counts up to 7 and then starts from 0 again

# Main state machine
while True:
    if i == 100:
        inc = -1
    elif i == 0:
        inc = 1

    i += inc

    scan += 1

    if scan == 8:
        scan = 0

    print(next_stage)

    if client.new_game_flag and next_stage != "new_game":
        next_stage = "wait_for_ball"
        client.new_game_flag = False

    if next_stage == "wait_for_connection":
        # Wait for mqtt connection
        # Show random pixels
        hat.set_pixels(pa.fade(pa.loading(), i/100))

        if client.connected_flag:
            # We have a connection, ask the user to start a game and wait for a game start
            # from the enemy
            next_stage = "new_game"

    elif next_stage == "new_game":
        # Call the new_game() function
        new_game_started, client.game_initiator = new_game(client, i/100)

        if new_game_started:
            # A new game has been started, either wait for the ball if the enemy initiated
            # or set the ball and start playing
            client.goals_scored = 0
            client.goals_suffered = 0
            client.new_game_flag = False
            if client.game_initiator:
                next_stage = "play"
                ball.reinit()
            else:
                next_stage = "wait_for_ball"

    elif (next_stage == "scored") or (next_stage == "suffered_goal"):
        # Show score for 2 seconds
        if next_stage == "scored":
            hat.set_pixels(pa.make_score(client.goals_scored, client.goals_suffered, [0, 255, 0]))
        else:
            hat.set_pixels(pa.make_score(client.goals_scored, client.goals_suffered, [255, 0, 0]))
        
        for wait in range(2):
            sleep(1)

        if client.goals_scored >= client.winning_score or client.goals_suffered >= client.winning_score:
            # End of game, show win or lose for two seconds
            next_stage = "new_game"
            print("Goals: " + str(client.goals_suffered) + " " + str(client.goals_scored))
            
            if client.goals_suffered > client.goals_scored:
                fill_color(hat, [0, 0, 0])
                #client.publish("thm_rr_iot_project/player" + ("0" if client.game_initiator else "1") + "/lost", payload=(client.session_id + "," + select_name()))
            else:
                fill_color(hat, [0, 0, 0])
                #client.publish("thm_rr_iot_project/player" + ("0" if client.game_initiator else "1") + "/won", payload=(client.session_id + "," + select_name()))

            client.name = select_name()
            message = client.session_id + "," + client.name

            if client.enemy_name == "":
                client.publish("thm_rr_iot_project/player" + ("0" if client.game_initiator else "1") + "/game", payload=(message))
            else:
                message += "," + str(client.goals_scored) + "," + client.enemy_name + "," + str(client.goals_suffered)
                client.publish("thm_rr_iot_project/session/game", payload=(message))
                client.enemy_name = ""

            #for wait in range(2):
            #    sleep(1)
            #continue
        else:
            if next_stage == "scored":
                next_stage = "play"
                ball.reinit()
            else:
                next_stage = "wait_for_ball"

    elif next_stage == "wait_for_ball":
        if client.pass_received_flag:
            client.pass_received_flag = False
            ball.set(client.pass_value_pos_x, client.pass_value_pos_y, client.pass_value_vel_x, client.pass_value_vel_y)
            next_stage = "play"
        
        elif client.goal_scored_flag:
            client.goal_scored_flag = False
            next_stage = "scored"

        fill_color(hat, [0, 0, 0])
        paddle.move(hat)
        paddle.draw()

    elif next_stage == "play":
        fill_color(hat, [0, 0, 0])
   
        ball.move()
        paddle.move(hat)

        suffered_goal, court_change = intra_object_collision_detection(ball, paddle)
        
        if suffered_goal:
            client.goals_suffered += 1
            client.publish("thm_rr_iot_project/player" + ("0" if client.game_initiator else "1") + "/score", payload=str(client.goals_suffered))
            next_stage = "suffered_goal"

        if court_change:
            client.publish("thm_rr_iot_project/player" + ("0" if client.game_initiator else "1") + "/pass", payload=pass_ball_string(ball))
            next_stage = "wait_for_ball"
        
        ball.draw()
        paddle.draw()

    if client.difficulty == 1:
        sleep(0.15)
    elif client.difficulty == 2:
        sleep(0.10)
    elif client.difficulty == 3:
        sleep(0.05)
    else:
        sleep(0.15)

