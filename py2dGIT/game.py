import pygame
import sys
import time
import socket
import threading
import json 
import math


server_address = ('147.185.221.17', 45922)  #connect to public WizLand Servers for testing
server_address = ('127.0.0.1', 25565)       #local machine server hosting for easy troubleshooting

# Initialize Pygame
pygame.init()
pygame.mixer.init()

pygame.mixer.music.load('sounds/soundtrack2.mp3')
pygame.mixer.music.set_volume(0.45)
pygame.mixer.music.play(loops=-1)

map_img = pygame.image.load("assets/map2.png") 

gui_img = pygame.image.load("assets/cont.png") 
# Constants
WIDTH, HEIGHT = 1200, 800
FPS = 60

favicon_image = pygame.image.load("assets/favicon.png")  # Replace "favicon.png" with your icon file
pygame.display.set_icon(favicon_image)

# Colors
WEIRD = (0, 20, 20)
GREEN = (0, 0, 0)
PURP = (93, 65, 116)
TEXT_COLOR = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
REAL_GREEN = (0, 255, 0)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)  #for windowed screen(for troubleshooting),remove ", pygame.FULLSCREEN | pygame.SCALED"
pygame.display.set_caption("WizLand")

# Font
font = pygame.font.Font('empire.otf', 36)

KEY_X = pygame.K_x

KEY_C = pygame.K_c

KEY_L = pygame.K_l

last_key_press_time = 0

opengates = True

# Clock to control the frame rate
clock = pygame.time.Clock()

# Game states
STATE_USERNAME_ENTRY = 0
STATE_MENU = 1
STATE_CREATE_GAME = 2
STATE_JOIN_GAME = 3
STATE_GAMEROOM = 4

current_state = STATE_USERNAME_ENTRY
username = ""
room_name = ""
selected_room = ""

# List to store room names for the "Join Game" state
room_names_list = []

# Player avatar
player_avatar = pygame.image.load('SoloSprites/Idle_1.png')
player_avatar = pygame.transform.scale(player_avatar, (40, 40))

# Player position
player_position = [400, 400]

# Player movement speed
movement_speed = 5

last_bullet_time = 0

frogs_available = 0

enemies = []

my_frogs = []

enemy_frogs = []

isinred = False

pyramid_locked = False

tp_speed = 0

frog_tps = 0

invs_a = 0

last_x_time = 0

rt_msg_1 = "WAITING"
rt_msg_2 = "*WARNINGS*"

ready_text = 'READY'

ready_status = False

ingame = False

render_distance = 1000

ready_color = (0, 255, 0)

player_health = 100

admins = []

inv_enemies = []

freedom = True

inv = False

gamestart_sound = pygame.mixer.Sound('sounds/on2.wav')

tp_sound = pygame.mixer.Sound('sounds/tp.wav')

bip_sound = pygame.mixer.Sound('sounds/menu1.wav')

enter_sound = pygame.mixer.Sound('sounds/enter.wav')

# Bullet image
bullet_image = pygame.image.load('assets/fireball.png')
bullet_image = pygame.transform.scale(bullet_image, (20, 20))

frog_image = pygame.image.load('assets/frogo.png')
frog_image = pygame.transform.scale(frog_image, (30, 30))

enemy_frog_image = pygame.image.load('assets/enemy_frogo.png')
enemy_frog_image = pygame.transform.scale(enemy_frog_image, (30, 30))


IDLE_STATE = 0
ATTACK_STATE_1 = 1
ATTACK_STATE_2 = 2

# Define avatar animations
idle_image = pygame.image.load('SoloSprites/Idle_1.png')
attack_image_1 = pygame.image.load('SoloSprites/Attack_3.png')
attack_image_2 = pygame.image.load('SoloSprites/Attack_4.png')

player_avatar_states = {
    IDLE_STATE: idle_image,
    ATTACK_STATE_1: attack_image_1,
    ATTACK_STATE_2: attack_image_2,
}

ENEMY_IDLE_STATE = IDLE_STATE
ENEMY_ATTACK_STATE_1 = ATTACK_STATE_1
ENEMY_ATTACK_STATE_2 = ATTACK_STATE_2

current_avatar_state = IDLE_STATE
avatar_state_start_time = 0
avatar_state_duration = 100



# List to store bullet positions and their creation time
bullets = []

enemy_bullets = []


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect(server_address)
except:
    print('MAIN SERVER IS DOWN')
    sys.exit()

def draw_linear_gradient(start_color, end_color):

    colors_sum = 80

    rect_height = HEIGHT // colors_sum
    for i in range(colors_sum):
        # Calculate color at current position
        r = int(start_color[0] + (end_color[0] - start_color[0]) * (i / colors_sum))
        g = int(start_color[1] + (end_color[1] - start_color[1]) * (i / colors_sum))
        b = int(start_color[2] + (end_color[2] - start_color[2]) * (i / colors_sum))
        color = (r, g, b)

        # Draw a rectangle with the calculated color
        pygame.draw.rect(screen, color, (0, i * rect_height, WIDTH, rect_height))

def draw_light(screen, player_position):
    global render_distance

    # Get player coordinates
    player_x, player_y = player_position[0], player_position[1]

    # Set the radius of the lighting shade
    light_radius = render_distance

    # Create a surface for the lighting shade
    light_surface = pygame.Surface((2 * light_radius, 2 * light_radius), pygame.SRCALPHA)
    pygame.draw.circle(light_surface, (0, 0, 0, 35), (light_radius, light_radius), light_radius)

    # Blit the lighting shade onto the screen
    screen.blit(light_surface, (player_x - light_radius, player_y - light_radius))

def draw_health_bar():
    global enemies , inv_enemies , render_distance ,ingame


    health_bar_length = 50  # You can adjust the length of the health bar
    health_bar_height = 2


    health_percentage = max(player_health, 0) / 100.0
    health_bar_width = int(health_bar_length * health_percentage)

    # Draw the background of the health bar (empty)
    pygame.draw.rect(screen, (255, 0, 0), (player_position[0] - health_bar_length / 2, player_position[1] + 30, health_bar_length, health_bar_height))

    # Draw the filled portion of the health bar
    pygame.draw.rect(screen, (0, 255, 0), (player_position[0] - health_bar_length / 2, player_position[1] + 30, health_bar_width, health_bar_height))

    for enemy in enemies:
        if enemy['name'] not in inv_enemies:
            distance = math.sqrt((enemy['x'] - player_position[0]) ** 2 + (enemy['y']- player_position[1]) ** 2)
            if distance > render_distance and ingame:
                break
            health_percentage_n = max(enemy['health'], 0) / 100.0
            health_bar_width_n = int(health_bar_length * health_percentage_n)


            pygame.draw.rect(screen, (0, 0, 0), (enemy['x'] - health_bar_length / 2, enemy['y'] + 30, health_bar_length, health_bar_height))

        # Draw the filled portion of the health bar
            pygame.draw.rect(screen, (216, 227, 216), (enemy['x'] - health_bar_length / 2, enemy['y'] + 30, health_bar_width_n, health_bar_height))


def send_to_server(message):
    try:
        # Send the message to the server
        client_socket.sendall(message.encode())
    except Exception as e:
        print(f"Error sending data to the server: {e}")



# Function to get the list of current games (only room names) from the CSV file
def get_current_game_names():
    global rooms
    return rooms


# Function to check if a point is inside the purple rectangle
def is_point_inside_rect(x, y, rect, rectname):
    if rectname == 'purple':
        rect_size = 50 
    elif rectname == 'red':
        rect_size = 10 
    else:
        rect_size = 65
    rect = rect.inflate(rect_size, rect_size)
    avatar_rect = player_avatar.get_rect(center=(x, y))
    avatar_corners = [
        (avatar_rect.left, avatar_rect.top),
        (avatar_rect.right, avatar_rect.top),
        (avatar_rect.left, avatar_rect.bottom),
        (avatar_rect.right, avatar_rect.bottom),
    ]

    return all(rect.left < px < rect.right and rect.top < py < rect.bottom for px, py in avatar_corners)

current_enemy_avatar_state = ENEMY_IDLE_STATE
enemy_avatar_state_start_time = 0
enemy_avatar_state_duration = 100 




def draw_enemies():
    global inv_enemies  # You might not need to declare other globals if they are set elsewhere in your code

    for enemy in enemies:
        # Update enemy avatar state based on elapsed time
        enemy['el_time'] = time.time() - enemy['start_state_time']

        # Calculate distance between player and enemy
        distance = math.sqrt((enemy['x'] - player_position[0]) ** 2 + (enemy['y'] - player_position[1]) ** 2)

        # Check if enemy is within render distance and the game is in progress
        if distance <= render_distance or not ingame:
            # Check if it's time to transition to the next state
            if enemy['avatar_state'] == ENEMY_ATTACK_STATE_1 and enemy['el_time'] >= 0.1:
                # Transition to ENEMY_ATTACK_STATE_2 after 100ms
                enemy['avatar_state'] = ENEMY_ATTACK_STATE_2
                enemy['start_state_time'] = time.time()

            elif enemy['avatar_state'] == ENEMY_ATTACK_STATE_2 and enemy['el_time'] >= 0.1:
                # Transition to IDLE_STATE after another 100ms
                enemy['avatar_state'] = IDLE_STATE
                enemy['start_state_time'] = time.time()

            # Get the enemy avatar image based on the current state
            enemy_avatar = player_avatar_states[enemy['avatar_state']]
            enemy_avatar = pygame.transform.scale(enemy_avatar, (40, 40))

            # Draw the enemy avatar on the screen


            # Display the name of the enemy above the avatar
            if enemy['name'] not in inv_enemies:
                enemy_rect = enemy_avatar.get_rect(center=(enemy['x'], enemy['y']))
                screen.blit(enemy_avatar, enemy_rect)
                font = pygame.font.Font('empire.otf', 24)  # You can adjust the font size
                text = font.render(enemy['name'], True, RED)  # White color, you can adjust
                text_rect = text.get_rect(center=(enemy['x'], enemy['y'] - 30))  # Adjust the vertical offset (e.g., -10 pixels)
                screen.blit(text, text_rect)

        





def draw_fraw():
    global my_frogs

    # Get the dimensions of the gameroom
    gameroom_left, gameroom_top, gameroom_width, gameroom_height = gameroom_rect
    gameroom_right = gameroom_left + gameroom_width - 30
    gameroom_bottom = gameroom_top + gameroom_height - 30

    for i in range(len(my_frogs)):
        x, y, direction, frog_time = my_frogs[i]

        # Update frog position
        new_x = x + direction[0] * 5 
        new_y = y + direction[1] * 5
        

        # Check boundaries and make the frog bounce back
        if new_x < gameroom_left:
            new_x = gameroom_left + (gameroom_left - new_x)
            direction = (-direction[0], direction[1])  # Invert x direction
        elif new_x > gameroom_right:
            new_x = gameroom_right - (new_x - gameroom_right)
            direction = (-direction[0], direction[1])  # Invert x direction

        if new_y < gameroom_top:
            new_y = gameroom_top + (gameroom_top - new_y)
            direction = (direction[0], -direction[1])  # Invert y direction
        elif new_y > gameroom_bottom:
            new_y = gameroom_bottom - (new_y - gameroom_bottom)
            direction = (direction[0], -direction[1])  # Invert y direction

        my_frogs[i] = (new_x, new_y, direction, frog_time)

    




    # Draw the frogs
    for index, frog in enumerate(my_frogs, start=1):
        textc = str(index) 
        textc_surface = font.render(textc, True, (255, 255, 255))
        screen.blit(frog_image, (int(frog[0]), int(frog[1])))
        screen.blit(textc_surface, (int(frog[0]) + 12, int(frog[1]) - 15))



time_frog_dmg = 0

def draw_enemy_frogs():
    global enemy_frogs, time_frog_dmg

    current_time = time.time()
    player_radius = 20

    # Get the dimensions of the gameroom
    gameroom_left, gameroom_top, gameroom_width, gameroom_height = gameroom_rect
    gameroom_right = gameroom_left + gameroom_width - 30
    gameroom_bottom = gameroom_top + gameroom_height - 30

    for i in range(len(enemy_frogs)):
        x, y, direction, frog_time = enemy_frogs[i]

        # Update enemy frog position
        new_x = x + direction[0] * 5
        new_y = y + direction[1] * 5

        distance = math.sqrt((new_x - player_position[0]) ** 2 + (new_y - player_position[1]) ** 2)

        if distance < player_radius and current_time - time_frog_dmg > 0.3:
            # Collision detected, handle it as needed (e.g., game over)
            print("Player collided with enemy frog!", time_frog_dmg)
            message = json.dumps({"action": "touch_frog", "player": username})
            send_to_server(message)

            time_frog_dmg = current_time  # Update the last damage time

        # Check boundaries and make the enemy frog bounce back
        if new_x < gameroom_left:
            new_x = gameroom_left + (gameroom_left - new_x)
            direction = (-direction[0], direction[1])  # Invert x direction
        elif new_x > gameroom_right:
            new_x = gameroom_right - (new_x - gameroom_right)
            direction = (-direction[0], direction[1])  # Invert x direction

        if new_y < gameroom_top:
            new_y = gameroom_top + (gameroom_top - new_y)
            direction = (direction[0], -direction[1])  # Invert y direction
        elif new_y > gameroom_bottom:
            new_y = gameroom_bottom - (new_y - gameroom_bottom)
            direction = (direction[0], -direction[1])  # Invert y direction

        enemy_frogs[i] = (new_x, new_y, direction, frog_time)

    # Draw the enemy frogs
    for enemy_frog in enemy_frogs:
        screen.blit(enemy_frog_image, (int(enemy_frog[0]), int(enemy_frog[1])))

rooms= []

errc = 0

def receive_messages():
    global rooms ,current_state, freedom, starttpspeed ,  opengates , render_distance, invs_a ,frog_tps ,pyramid_locked, username, ready_color ,ready_text ,ready_status ,room_name, selected_room, enemies , ingame , enemy_frogs , current_enemy_avatar_state , enemy_avatar_state_start_time , player_health , errc , admins , tp_speed ,rt_msg_1 ,rt_msg_2 ,player_position ,inv , inv_enemies ,frogs_available

    while True:
        try:
            data = client_socket.recv(5024).decode('utf-8')
            if not data:
                break

            message = json.loads(data)

            print(message)                         #  Shows message upon receiving

            if "action" in message:
                if message["action"] == "player_join_data":
                    
                    player_list = message.get('players', [])
                    starttpspeed = message.get('tpspeed')
                    tp_speed = starttpspeed
                    player_coordinates = message.get('coordinates', {})
                    print(player_coordinates)###all
                    frogs_available = message['abilities'].get('frogs')
                    render_distance = message.get('rn_dn')



                    for player in player_list:
                        if player != username:
                            x = player_coordinates[player].get('x')
                            y = player_coordinates[player].get('y')
                            phealth = player_coordinates[player].get('health')
                            
                            enemy_info = {'name': player, 'x': x, 'y': y , 'health' : phealth ,'avatar_state' : ENEMY_IDLE_STATE ,'start_state_time': 0 ,'el_time' : 0}
                            enemies.append(enemy_info)

                elif message["action"] == "player_moved":
                    moved_username = message.get('username')
                    new_x = message.get('newx')
                    new_y = message.get('newy')

                    # Update the position of the corresponding enemy
                    for enemy in enemies:
                        if enemy['name'] == moved_username:
                            enemy['x'] = new_x
                            enemy['y'] = new_y
                elif message["action"] == "player_joined":
                            player = message.get('player')
                            x = 400
                            y = 400
                            starthealth = 100
                            
                            enemy_info = {'name': player, 'x': x, 'y': y , 'health' : starthealth ,'avatar_state' : ENEMY_IDLE_STATE ,'start_state_time': time.time() ,'el_time' : 0}
                            enemies.append(enemy_info)
                elif message["action"] == "shot":
                    # Handle enemy shot
                    bullet_start = (message.get("shotx"), message.get("shoty"))
                    bullet_end = (message.get("targetx"), message.get("targety"))

                    shooter = message.get('player')

                    if bullet_start and bullet_end:
                        for enemy in enemies:
                            if enemy['name'] == shooter:
                                try:
                                    # Check if the current state is not already ATTACK_STATE_1
                                    if enemy['avatar_state'] != ENEMY_ATTACK_STATE_1:
                                        enemy['avatar_state'] = ENEMY_ATTACK_STATE_1
                                        enemy['start_state_time'] = time.time()
                                        #print(f"Updated enemy avatar state to {current_enemy_avatar_state} at {enemy_avatar_state_start_time}")

                                    bullet_direction = pygame.math.Vector2(bullet_end[0] - bullet_start[0], bullet_end[1] - bullet_start[1]).normalize()
                                    enemy_bullets.append((bullet_start[0], bullet_start[1], bullet_direction, time.time()))  # Add creation time
                                except ValueError:
                                    pass
                elif message['action'] == 'dmged':
                    death = str(message.get('death'))

                    dmg = message.get('dmg')
                    wounded = message.get('player')
                    if wounded == username:
                        player_health -= dmg
                    else:
                        for enemy in enemies:
                            if enemy['name'] == wounded:
                                enemy['health'] -= dmg
                                print(f'-{dmg} health to {wounded}. Enemy health: {enemy["health"]}')
                    print(death)
                    if (death == 'True') & (wounded == username):
                        pygame.quit()
                        sys.exit()



                elif message['action'] == 'admin_list':
                    admins = message.get('admins')
                    rooms = message.get('rooms')
                elif message['action'] == 'player_left':
                    quiter = message.get('username')
                    print(f"{quiter} left the game.")
                    for enemy in enemies:
                        if enemy['name'] == quiter:
                            enemies.remove(enemy)
                            print(f"Removed {quiter} from the list of enemies.")
                elif message['action'] == 'psofos':
                        print('PSOFOSOSOSOSOSOSO')
                        pygame.quit()
                        sys.exit()
                elif message["action"] == "s_msg":
                    ch = message['channel']
                    cmsg = message['msg']
                    if ch == 1:
                        rt_msg_1 = str(cmsg)
                    else: 
                        rt_msg_2 = cmsg

                    if str(cmsg) == 'GAME STARTS':
                        gamestart_sound.play()
                    elif str(cmsg) == 'YOU WON':
                        ingame = False
                        ready_status = False
                        tp_speed = starttpspeed
                        ready_text = 'READY'
                        ready_color = REAL_GREEN
                        player_health = 100

                elif message["action"] == "force_tp":
                    players_loc = message.get('players_loc', {})
                    ingame = True
                    freedom = True

                    try:
                        frogs = message['frogs']
                        frogs_available = frogs
                    except:
                        pass#no froggs passed

                    for player_name, coordinates in players_loc.items():
                        x_coordinate = coordinates['x']
                        y_coordinate = coordinates['y']
                        if player_name == username:
                            player_position = [x_coordinate , y_coordinate]
                            frog_tps = message["tps"]
                            invs_a = message["invs"]
                            frogs_available = message["frogs"]
                        else:
                            for enemy in enemies:
                                if enemy['name'] == player_name:
                                    enemy['x'] = x_coordinate
                                    enemy['y'] = y_coordinate
                                    enemy['avatar_state'] = IDLE_STATE
                                    enemy['start_state_time'] = time.time()
                                    enemy['el_time'] = 0
                elif message["action"] == "speed_change":
                    newspeed = message['newspeed']
                    tp_speed = newspeed
                elif message["action"] == "goinv":
                    invs_a -= 1
                    inv = True
                elif message["action"] == "noinv":
                    
                    inv = False
                elif message["action"] == "enemy_inv":
                    inver = message['player']
                    inv_enemies.append(inver)
                    print(inv_enemies)
                elif message["action"] == "enemy_not_inv":
                    uninver = message['player']
                    inv_enemies.remove(uninver)
                    print(inv_enemies)
                elif message["action"] == "frog_send":
                    received_dt = message['frog_data']
                    x, y, direction_tuple, current_time_key_x = received_dt
                    frogs_direction = pygame.math.Vector2(direction_tuple[0], direction_tuple[1])
                 
                    try:
                        enemy_frogs.append((x,y - 15, frogs_direction, current_time_key_x))  # Add creation time
                    except ValueError:
                        pass
                elif message["action"] == "locked":
                    pyramid_locked = True
                    time.sleep(3)
                    pyramid_locked = False
                elif message["action"] == "enpowered":
                    frogs_available += 10
                    invs_a += 8
                    frog_tps += 5
                    tp_speed = message["new_speed"]
                elif message["action"] == "gates":
                    opengates = message["status"]

        except Exception as e:
            errc = errc + 1
            print(f"Error receiving data from the server: {e}")
            print('|ERROR COUNT|' , errc , data)
            continue
            

# Start the message receiver thread
message_receiver_thread = threading.Thread(target=receive_messages)
message_receiver_thread.start()

frog_select = 0

last_action_time = 0

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False



        elif event.type == pygame.KEYDOWN and current_state == STATE_GAMEROOM:
            if hasattr(event, 'key') and pygame.K_0 <= event.key <= pygame.K_9:
                current_time = pygame.time.get_ticks()
                if current_time - last_action_time >= 500:
                    last_action_time = current_time 


                    realkey = (int(event.key) - 48)
                    frog_select = realkey

                    for index, frog in enumerate(my_frogs, start=1):
                        if index == frog_select:
                            x, y, direction, frog_time = frog
                            tp_sound.play()

                    try:
                        message = json.dumps({"action": "frogtp_try", "username": username, "location": {'x': x, 'y': y}})
                        send_to_server(message)
                    except:
                        print('fail num pressed')
                        pass

            if event.key == KEY_X:
                if (frogs_available) > 0 and (isinred == False) and (ingame == True):
                    current_time = time.time()
                    time_since_last_x = current_time - last_x_time

                    if time_since_last_x >= 0.4:  # frog attack speed
                        # Update the last key press time


                        frogs_start = player_position.copy()
                        mouse_x, mouse_y = pygame.mouse.get_pos()

                        try:
                        # Calculate frogs_direction with correct order
                            frogs_direction = pygame.math.Vector2(mouse_x - frogs_start[0], mouse_y - frogs_start[1]).normalize()
                            frogspeed = 2.5

                            frogs_direction *= frogspeed

                        
                            my_frogs.append((frogs_start[0], frogs_start[1] - 15, frogs_direction, current_time))  # Add creation time
                            last_frog_time = current_time  # Update the last frog time
                        except ValueError:
                            pass

                        dt = (frogs_start[0], frogs_start[1] - 15, (frogs_direction.x, frogs_direction.y), current_time)


                        message =json.dumps({"action": "frog" , "frog_data": dt ,"username": username})
                        send_to_server(message)

                        frogs_available -= 1
                else:
                    rt_msg_2 = 'NO FROGS'
                    print(frogs_available)

            # Check if key is pressed #INVISIBILITY
            if event.key == KEY_C:
                current_time_key_c = pygame.time.get_ticks()
                time_difference = current_time_key_c - last_key_press_time

                if time_difference >= 500:  # 500 ms
                    # Update the last key press time
                    last_key_press_time = current_time_key_c

                    # Your existing code to handle the key press
                    message = json.dumps({"action": "inv_try", "username": username, "room_name": room_name})
                    send_to_server(message)
                else:
                    print('SPAM KEY C') #spam count

        elif event.type == pygame.KEYDOWN and current_state == STATE_USERNAME_ENTRY:
            if event.key == pygame.K_RETURN and username.strip():
                # Move to the next state if a non-empty username is entered
                enter_sound.play()
                current_state = STATE_MENU
            elif event.key == pygame.K_BACKSPACE:
                # Handle backspace for username input
                username = username[:-1]
            elif event.type == pygame.KEYDOWN and event.unicode.isalnum():
                # Handle alphanumeric input for username
                username += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == STATE_MENU:
                # Check if the mouse click is inside the JOIN GAME or CREATE GAME button
                
                if event.button == 3: #bug prevent
                    break
                if join_game_rect.collidepoint(event.pos):
                    #print("JOIN GAME button clicked!")
                    room_names_list = get_current_game_names()
                    current_state = STATE_JOIN_GAME
                    bip_sound.play()
                #elif create_game_rect.collidepoint(event.pos):
                    #print("CREATE GAME button clicked!")
                 #   current_state = STATE_CREATE_GAME

            elif current_state == STATE_JOIN_GAME:
                # Check if the mouse click is inside a room name panel
                for i, room_rect in enumerate(room_rects):
                    if room_rect.collidepoint(event.pos):
                        selected_room = room_names_list[i]

                        message = json.dumps({"action": "join_room", "username": username, "room_name": room_name})
                        send_to_server(message)
                        bip_sound.play()
                        current_state = STATE_GAMEROOM

            elif current_state == STATE_CREATE_GAME:
                # Handle events specific to the CREATE GAME state
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and False:#to delete
                    print("Room Name submitted:", room_name)
                    create_room(room_name, username)
                    current_state = STATE_MENU
                    room_name = ""
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                    room_name = room_name[:-1]
                elif event.type == pygame.KEYDOWN and event.unicode.isalnum():
                    room_name += event.unicode

            elif current_state == STATE_GAMEROOM:
                # Handle left-click to attack
                if event.button == 1:
                    if is_point_inside_rect(*event.pos, button_rect, 'button'):
                        if ready_status == False :
                            ready_status = True
                            ready_text = 'UNREADY'
                            ready_color = RED


                            if ingame == False:
                                ready = json.dumps({"action": "ready", "username": username ,"room_name": room_name})
                                send_to_server(ready)
                            freedom = False
                            #print('readyu')
                            break
                        else:
                            ready_status = False
                            ready_text = 'READY'
                            ready_color = REAL_GREEN
                            freedom = True


                            unready = json.dumps({"action": "unready", "username": username ,"room_name": room_name})
                            send_to_server(unready)
                            #print('unreadyu')
                            break
                    elif is_point_inside_rect(*event.pos, lock_b_rect, 'button'):#lock key pressed
                        
                        button_player_distance = pygame.math.Vector2(player_position[0] - event.pos[0], player_position[1] - event.pos[1]).length()
                        if button_player_distance < 160:
                            locktry = json.dumps({"action": "try_lock", "username": username ,"room_name": room_name})
                            send_to_server(locktry)
                            break
                        else:
                            rt_msg_2 = f'TOO FAR({int(button_player_distance)})'
                        break
                    current_time = time.time()
                    time_since_last_bullet = current_time - last_bullet_time

                    # Check if enough time has passed since the last bullet
                    if time_since_last_bullet >= 0.25 and freedom == True:  # 
                        print(f"|X| Player {username} attacked at {event.pos}")

                        current_avatar_state = ATTACK_STATE_1
                        avatar_state_start_time = current_time
                        

                        # Shoot a bullet in the direction of the click
                        bullet_start = player_position.copy()
                        bullet_end = event.pos
                        bulmessage = json.dumps({"action": "piu", "username": username, "targetx": event.pos[0], "targety": event.pos[1], "room_name": room_name})
                        send_to_server(bulmessage)
                        try:
                            bullet_direction = pygame.math.Vector2(bullet_end[0] - bullet_start[0], bullet_end[1] - bullet_start[1]).normalize()
                            bullets.append((bullet_start[0], bullet_start[1] - 15, bullet_direction, current_time))  # Add creation time
                            last_bullet_time = current_time  # Update the last bullet time
                        except ValueError:
                            pass

                # Handle right-click to teleport the player avatar
                elif event.button == 3 :
                    if freedom and not (pyramid_locked and isinred):

                        if is_point_inside_rect(*event.pos, small_box_rect, 'red') | is_point_inside_rect(*event.pos, purple_rect, 'purple'):
                            tpdistance = pygame.math.Vector2(player_position[0] - event.pos[0],
                                                    player_position[1] - event.pos[1]).length()

                            if tpdistance < tp_speed:
                                if is_point_inside_rect(*event.pos, small_box_rect, 'red') and opengates:
                                    if isinred == False: #opengates:
                                        pyra = json.dumps({"action": "pyramid", "username": username, "room_name": room_name , 'stat' : 'inside'})
                                        send_to_server(pyra)
                                        isinred = True
                                else:
                                    if isinred == True:
                                        pyra = json.dumps({"action": "pyramid", "username": username, "room_name": room_name, 'stat' : 'outside'})
                                        send_to_server(pyra)
                                        isinred = False
                                
                                if is_point_inside_rect(*event.pos, small_box_rect, 'red') and opengates == False:
                                    break

                                player_position = list(event.pos)
                                #print(f"|>| Player {username} teleported to {event.pos}")
                                movemessage = json.dumps({"action": "player_move", "username": username, "newx": event.pos[0], "newy": event.pos[1], "room_name": room_name})
                                send_to_server(movemessage)
                            else:
                                rt_msg_2 = f"TOO FAR({int(tpdistance)})"
                    else:
                        rt_msg_2 = 'CANT MOVE'



    # Update player avatar state based on elapsed time
    if current_avatar_state == ATTACK_STATE_1 and time.time() - avatar_state_start_time >= avatar_state_duration / 1000:
        current_avatar_state = ATTACK_STATE_2
        avatar_state_start_time = time.time()
    elif current_avatar_state == ATTACK_STATE_2 and time.time() - avatar_state_start_time >= avatar_state_duration / 1000:
        current_avatar_state = IDLE_STATE


    # Drawing
    draw_linear_gradient((61, 0, 66), (4, 5, 5))         #(61, 0, 66), (40, 66, 66)

    if current_state == STATE_USERNAME_ENTRY:
        # Display username input
        font2 = pygame.font.Font('empire.otf', 85)

        username_text = font.render("Enter Your Username", True, TEXT_COLOR)
        username_rect = username_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))  # Adjusted vertical position
        screen.blit(username_text, username_rect)

        input_text = font2.render(username, True, (98, 0, 179))
        input_rect = input_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))  # Adjusted vertical position
        screen.blit(input_text, input_rect)

    elif current_state == STATE_MENU:
        purple_rect = pygame.Rect(WIDTH // 2 - 320, HEIGHT // 2 - 320, 640, 640)
        border_thickness = 5  # Adjust the thickness of the border
        pygame.draw.rect(screen, PURP, purple_rect, border_radius=0)
        pygame.draw.rect(screen, TEXT_COLOR, purple_rect, border_thickness, border_radius=0)

        join_game_button = font.render("JOIN GAME", True, TEXT_COLOR)
        join_game_rect = join_game_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(join_game_button, join_game_rect)

        if username in admins:

            create_game_button = font.render("CREATE GAME", True, (89, 0, 3))
            create_game_rect = create_game_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(create_game_button, create_game_rect)

    elif current_state == STATE_JOIN_GAME:
        room_rects = []
        for i, room_name in enumerate(room_names_list):
            room_panel = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 200 + i * 60, 400, 50)
            pygame.draw.rect(screen, PURP, room_panel, border_radius=0)
            room_text = font.render(room_name, True, TEXT_COLOR)
            room_text_rect = room_text.get_rect(center=room_panel.center)
            screen.blit(room_text, room_text_rect)
            room_rects.append(room_panel)

    elif current_state == STATE_CREATE_GAME:
        input_text = font.render("Room Name: " + room_name, True, TEXT_COLOR)
        input_rect = input_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(input_text, input_rect)

    elif current_state == STATE_GAMEROOM:
        
        

        # gameroom main box
        gameroom_width = 700
        gameroom_height = 700
        gameroom_rect = pygame.Rect(WIDTH // 2 - gameroom_width // 2, HEIGHT // 2 - gameroom_height // 2, gameroom_width, gameroom_height)
        border_thickness = 8  # Adjust the thickness of the border
        map_img_t =pygame.transform.scale(map_img, (gameroom_width + 30, gameroom_height + 30))
        #pygame.draw.rect(screen, (128, 30, 5), gameroom_rect, border_radius=0)
        
        map_position = (gameroom_rect.topleft[0] - 15, gameroom_rect.topleft[1] - 15)

        screen.blit(map_img_t, map_position)
        #pygame.draw.rect(screen, (0,0,0), gameroom_rect, border_thickness, border_radius=0)



        # small red box Right
        small_box_width = 150
        small_box_height = 150
        small_box_rect = pygame.Rect(WIDTH // 2 + 250 + 120, HEIGHT // 2 - small_box_height // 2, small_box_width, small_box_height)
        # Draw the small box first and then draw its border
        pygame.draw.rect(screen, WEIRD, small_box_rect)
        b_th_pyr = 4
        pygame.draw.rect(screen, (0, 255, 200), small_box_rect, b_th_pyr)

        # small lcok box Right
        lock_b_width = 50
        lock_b_height = 50
        lock_b_rect = pygame.Rect(WIDTH // 2 + 250 + 170, HEIGHT // 2 - small_box_height // 2 - 90, lock_b_width, lock_b_height)
        # Draw the small box first and then draw its border
        if pyramid_locked:
            lock_color = (122, 0, 0)
        else:
            lock_color = (96, 96, 102)
        pygame.draw.rect(screen, lock_color, lock_b_rect)

        lock_path = "assets/lock.png"
        scaling_factor = 1
        lock_image = pygame.image.load(lock_path)
        lock_image = pygame.transform.scale(lock_image, (int(lock_b_width * scaling_factor) , int(lock_b_height * scaling_factor)))
        screen.blit(lock_image,  (lock_b_rect.x - 0, lock_b_rect.y + (lock_b_rect.height - lock_image.get_height()) // 2))

        # Load the pyramid image
        image_path = "assets/Pyramid.png"  # Replace with the path to your PNG image
        image = pygame.image.load(image_path)
        scaling_factor = 0.8  # Adjust as needed (e.g., 0.8 means 80% of the original size)
        image = pygame.transform.scale(image, (int(small_box_width * scaling_factor) , int(small_box_height * scaling_factor)))
        screen.blit(image,  (small_box_rect.x + 15, small_box_rect.y + (small_box_rect.height - image.get_height()) // 2))
        
        # Yellow box centered to the left
        if ingame:
            outoffset = 80          #to create free space for the player's abilities
        else:
            outoffset = 20

            
        yellow_box_width = 200
        yellow_box_height = 600
        yellow_box_rect = pygame.Rect(30, (HEIGHT // 2 - yellow_box_height // 2) + outoffset, yellow_box_width, yellow_box_height)
        pygame.draw.rect(screen, WEIRD, yellow_box_rect)


        ####
        gui_img_t =pygame.transform.scale(gui_img, (yellow_box_width + 100, yellow_box_height + 60))
        gui_position = (yellow_box_rect.topleft[0] - 15, yellow_box_rect.topleft[1] - 30)
        #screen.blit(gui_img_t, gui_position)

        if ingame == True:
            # stats box centered to the left
            stats_box_width = 160
            stats_box_height = 100
            stats_box_rect = pygame.Rect(30 + 15, (HEIGHT // 2 - stats_box_height // 2) - 300, stats_box_width , stats_box_height)
            pygame.draw.rect(screen, PURP, stats_box_rect)

            # First text: "frogs"
            text_surface = font.render(f"Frogs              {frogs_available} ", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(stats_box_rect.centerx - 0, stats_box_rect.top + stats_box_height // 6))
            screen.blit(text_surface, text_rect)

            # Second text: "tps"
            text_surface = font.render(f" Teleports         {frog_tps} ", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(stats_box_rect.centerx - 0, stats_box_rect.centery))
            screen.blit(text_surface, text_rect)

            # Third text: "invs"
            text_surface = font.render(f" Invisibles       {invs_a} ", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(stats_box_rect.centerx - 0, stats_box_rect.bottom - stats_box_height // 6))
            screen.blit(text_surface, text_rect)

        # First Inner box for content
        inner_box_width = 180
        inner_box_height = 100
        offset_from_top_first = 10  # Adjust the offset from the top for the first inner box
        inner_box_rect_first = pygame.Rect(yellow_box_rect.left + 10, yellow_box_rect.top + 10 + offset_from_top_first, inner_box_width, inner_box_height)
        pygame.draw.rect(screen, (235, 207, 255), inner_box_rect_first)

        # Second Inner box for content (200px lower than the first inner box)
        offset_from_top_second = 120  # Adjust the offset from the top for the second inner box
        inner_box_rect_second = pygame.Rect(yellow_box_rect.left + 10, yellow_box_rect.top + 10 + offset_from_top_second, inner_box_width, inner_box_height)
        pygame.draw.rect(screen, (235, 207, 255), inner_box_rect_second)

        # Render text "Health" in the first inner box
        plin_text = font.render("Players", True, RED)
        plin_text_rect = plin_text.get_rect(center=(inner_box_rect_second.centerx, inner_box_rect_second.centery - 20))
        screen.blit(plin_text, plin_text_rect.topleft)

        # Player health label in the first inner box
        plin_label = font.render(str( len(enemies) + 1), True, (0,0,0))
        plin_label_rect = plin_label.get_rect(center=(inner_box_rect_second.centerx, inner_box_rect_second.centery + 20))
        screen.blit(plin_label, plin_label_rect.topleft)

        # Render text "Room" in the second inner box
        room_text = font.render("Room", True, RED)
        room_text_rect = room_text.get_rect(center=(inner_box_rect_first.centerx, inner_box_rect_first.centery - 20))
        screen.blit(room_text, room_text_rect.topleft)

        # Room label in the second inner box
        room_label_text = font.render(str(room_name), True, (0,0,0))
        room_label_text_rect = room_label_text.get_rect(center=(inner_box_rect_first.centerx, inner_box_rect_first.centery + 20))
        screen.blit(room_label_text, room_label_text_rect.topleft)

        # Third | speed
        offset_from_top_third = 230  # Adjust the offset from the top for the second inner box
        inner_box_rect_third = pygame.Rect(yellow_box_rect.left + 10, yellow_box_rect.top + 10 + offset_from_top_third, inner_box_width, inner_box_height)
        pygame.draw.rect(screen, (235, 207, 255), inner_box_rect_third)

        # Render text "Speed" in the third inner box
        speed_text = font.render("Speed", True, RED)
        speed_text_rect = room_text.get_rect(center=(inner_box_rect_third.centerx, inner_box_rect_third.centery - 20))
        screen.blit(speed_text, speed_text_rect.topleft)

        # Speed label in the third inner box
        speed_label_text = font.render(str(tp_speed), True, (0,0,0))
        speed_label_text_rect = room_label_text.get_rect(center=(inner_box_rect_third.centerx + 20, inner_box_rect_third.centery + 20))
        screen.blit(speed_label_text, speed_label_text_rect.topleft)

        # Fourth | server message
        offset_from_top_fourth = 410  # Adjust the offset 
        inner_box_rect_fourth = pygame.Rect(yellow_box_rect.left + 10, yellow_box_rect.top + 10 + offset_from_top_fourth, inner_box_width, inner_box_height + 60)#60 biger
        pygame.draw.rect(screen, (54, 0, 26), inner_box_rect_fourth)

        # server message in the fourth inner box

        #server msg sizing width
        if len(rt_msg_1) > 10:
            rt1offset = 20
        elif len(rt_msg_1) > 5 :
            rt1offset = -4
        else:
            rt1offset = -30

        if len(rt_msg_2) > 12:
            rt2offset = 48
        elif len(rt_msg_2) > 6:
            rt2offset = 12
        else:
            rt2offset = 4

        srvmsg_label_text = font.render(rt_msg_1, True, (156, 202, 255))
        srvmsg_label_text_rect = room_label_text.get_rect(center=(inner_box_rect_fourth.centerx - rt1offset, inner_box_rect_fourth.centery - 50))
        screen.blit(srvmsg_label_text, srvmsg_label_text_rect.topleft)

        # server message2 in the fourth inner box
        srvmsg_label2_text = font.render(rt_msg_2, True, (255, 56, 56))
        srvmsg_label2_text_rect = room_label_text.get_rect(center=(inner_box_rect_fourth.centerx - rt2offset, inner_box_rect_fourth.centery + 30))
        screen.blit(srvmsg_label2_text, srvmsg_label2_text_rect.topleft)



        if ingame == False:
            # Button below all inner boxes
            button_width = 100
            button_height = 40
            button_rect = pygame.Rect(yellow_box_rect.left + (yellow_box_rect.width - button_width) // 2, inner_box_rect_third.bottom + 20, button_width, button_height)
            pygame.draw.rect(screen, (100, 100, 100), button_rect)  # Adjust the color of the button as needed

            # Render text on the button
            button_text = font.render(ready_text, True, ready_color)  # Adjust the text and color as needed
            button_text_rect = button_text.get_rect(center=button_rect.center)
            screen.blit(button_text, button_text_rect.topleft)




        # Update player avatar based on state
        player_avatar = player_avatar_states[current_avatar_state]
        player_avatar = pygame.transform.scale(player_avatar, (40, 40))
        avatar_rect = player_avatar.get_rect(center=(player_position[0], player_position[1]))

        sneaker_avatar = player_avatar.copy()
        sneaker_avatar.set_alpha(128)       # TRANSPARENCY 0 - 255

        if inv == True:
            screen.blit(sneaker_avatar, avatar_rect)
        else:
            screen.blit(player_avatar, avatar_rect)

        font = pygame.font.Font('empire.otf', 25)



        #USERNAME AND HEALTHBAR ATTACH
        username_text = font.render(username, True, (255, 255, 255)) 
        # Adjust the position of the username text 10px higher
        username_text_rect = username_text.get_rect(center=(player_position[0], player_position[1] - 30))  # Adjust the position as needed
        screen.blit(username_text, username_text_rect)


        draw_health_bar()


        draw_enemies()

        # Update and draw frogs
        draw_fraw()

        draw_enemy_frogs()
        # Update and draw bullets
        current_time = time.time()
        bullets = [(x + direction[0] * 10, y + direction[1] * 10, direction, bullet_time) for x, y, direction, bullet_time in bullets]
        for bullet in bullets:
            screen.blit(bullet_image, (bullet[0], bullet[1]))

        # Remove bullets that have existed for more than 0.3 seconds
        bullets = [bullet for bullet in bullets if current_time - bullet[3] <= 0.3]


        current_time = time.time()
        enemy_bullets = [(x + direction[0] * 10, y + direction[1] * 10, direction, bullet_time) for x, y, direction, bullet_time in enemy_bullets]
        for enemy_bullet in enemy_bullets:
            screen.blit(bullet_image, (enemy_bullet[0], enemy_bullet[1]))

        # Remove enemy bullets that have existed for more than 0.3 seconds
        enemy_bullets = [enemy_bullet for enemy_bullet in enemy_bullets if current_time - enemy_bullet[3] <= 0.2]

        # Remove frogs that have existed
        my_frogs = [frog for frog in my_frogs if current_time - frog[3] <= 6]
        enemy_frogs = [frog for frog in enemy_frogs if current_time - frog[3] <= 6]
        if ingame:
            draw_light(screen,player_position)
    pygame.display.flip()

    clock.tick(FPS)

# Quit Pygame
pygame.quit()
sys.exit()

