import carla
import time
import math
import random
import pygame
import sys
import os
import socket
import struct
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
from carla import Color, DebugHelper
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

class AEBDataLogger:
    def __init__(self, max_points=500):
        self.max_points = max_points
        self.time_data = deque(maxlen=max_points)
        self.distance_data = deque(maxlen=max_points)
        self.ttc_data = deque(maxlen=max_points)
        self.ego_speed_data = deque(maxlen=max_points)
        self.front_speed_data = deque(maxlen=max_points)
        self.aeb_status_data = deque(maxlen=max_points)
        self.start_time = time.time()
        
        # Configuration du dossier de sauvegarde
        self.figures_dir = r"C:\Users\thaoudi\Pictures\Figures_de_AEB"
       
        
        # Chemin du logo
        self.logo_path = r"C:\Users\thaoudi\Pictures\Camera Roll\téléchargement (1).png"
        
        # Nom du fichier avec timestamp pour éviter les écrasements
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.plot_filename = os.path.join(self.figures_dir, f"aeb_scenario1_plots_{timestamp}.png")
        
        # Configuration matplotlib pour mode interactif
        plt.ion()
        self.setup_plots()
        

    def setup_plots(self):
        """Configuration des graphiques avec fond blanc"""
        plt.style.use('default')
        self.fig = plt.figure(figsize=(14, 12))
        
        # Création des subplots avec une disposition verticale
        self.ax1 = plt.subplot2grid((4, 1), (0, 0))  # En haut
        self.ax2 = plt.subplot2grid((4, 1), (1, 0))  # Bas
        self.ax3 = plt.subplot2grid((4, 1), (2, 0))  # Plus bas
        self.ax4 = plt.subplot2grid((4, 1), (3, 0))  # Plus plus bas
        
        self.fig.suptitle('Scénario 1 AEB  – Analyse temps réel C2C', fontsize=16, color='black')
        
        # Configuration des axes avec fond blanc
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.set_facecolor('white')
            ax.grid(True, alpha=0.3)
        
        # Graphique 1 (en haut) - Distance
        self.ax1.set_title('Distance C2C', color='blue', x=0.0, y=1.05)
        self.ax1.set_ylabel('Distance (m)')
        self.ax1.set_ylim(0, 50)
        self.ax1.axhline(y=5, color='red', linestyle='--', alpha=0.7, label='Seuil de danger')
        
        # Graphique 2 (bas) - TTC
        self.ax2.set_title('Time to Collision (TTC)', color='green')
        self.ax2.set_ylabel('TTC (s)')
        self.ax2.set_ylim(0, 10)
        self.ax2.axhline(y=2, color='red', linestyle='--', alpha=0.7, label='TTC critique')
        
        # Graphique 3 (plus bas) - Vitesses
        self.ax3.set_title('Vitesses des véhicules', color='purple')
        self.ax3.set_ylabel('Speed (km/h)')
        self.ax3.set_ylim(0, 100)
        
        # Graphique 4 (plus plus bas) - Statut AEB
        self.ax4.set_title('AEB Status', color='red')
        self.ax4.set_xlabel('Time (s)')
        self.ax4.set_ylabel('AEB Active')
        self.ax4.set_ylim(-0.5, 1.5)
        
        # Initialisation des lignes
        self.line_distance, = self.ax1.plot([], [], 'b-', linewidth=2, label='Distance')
        self.line_ttc, = self.ax2.plot([], [], 'g-', linewidth=2, label='TTC')
        self.line_ego_speed, = self.ax3.plot([], [], 'r-', linewidth=2, label='Ego Speed')
        self.line_front_speed, = self.ax3.plot([], [], 'b-', linewidth=2, label='Front Speed')
        self.line_aeb_status, = self.ax4.plot([], [], 'k-', linewidth=3, label='AEB Active')
        
        # Légendes
        self.ax1.legend(loc='upper right')
        self.ax2.legend(loc='upper right')
        self.ax3.legend(loc='upper right')
        
      
        
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.01)
        
    def add_data(self, distance, ttc, ego_speed, front_speed, aeb_active):
        current_time = time.time() - self.start_time
        self.time_data.append(current_time)
        self.distance_data.append(distance)
        self.ttc_data.append(min(ttc, 10))
        self.ego_speed_data.append(ego_speed * 3.6)
        self.front_speed_data.append(front_speed * 3.6)
        self.aeb_status_data.append(1 if aeb_active else 0)
        
        if len(self.time_data) % 5 == 0:
            self.update_plots()
    
    def update_plots(self):
        if len(self.time_data) < 2:
            return
            
        try:
            times = list(self.time_data)
            
            self.line_distance.set_data(times, list(self.distance_data))
            self.line_ttc.set_data(times, list(self.ttc_data))
            self.line_ego_speed.set_data(times, list(self.ego_speed_data))
            self.line_front_speed.set_data(times, list(self.front_speed_data))
            self.line_aeb_status.set_data(times, list(self.aeb_status_data))
            
            if times:
                max_time = max(times)
                for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                    ax.set_xlim(max(0, max_time - 30), max_time + 2)
                    ax.relim()
                    ax.autoscale_view(scalex=False)
            
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            plt.pause(0.001)
            
        except Exception as e:
            print(f"Erreur mise à jour graphiques: {e}")

    def save_plots(self):
            # Vérification finale du dossier
            if not os.path.exists(self.figures_dir):
                os.makedirs(self.figures_dir)
            
            # Sauvegarde de la figure principale
            self.fig.savefig(self.plot_filename, dpi=300, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
            print(f"✓ Graphiques sauvegardés dans: {self.plot_filename}")
            
            # Sauvegarde également en PDF pour une meilleure qualité
            pdf_filename = self.plot_filename.replace('.png', '.pdf')
            self.fig.savefig(pdf_filename, dpi=300, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
            print(f"✓ Version PDF sauvegardée: {pdf_filename}")

def get_speed(vehicle):
    velocity = vehicle.get_velocity()
    return math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)

def get_obstacle_type(actor):
    if 'vehicle' in actor.type_id:
        return 'VEHICLE'
    elif 'walker' in actor.type_id:
        return 'PEDESTRIAN'
    elif 'bicycle' in actor.type_id:
        return 'BICYCLE'
    return 'UNKNOWN'

def draw_bounding_box(world, actor, color=Color(r=0, g=255, b=0)):
    debug = world.debug
    bb = actor.bounding_box
    transform = actor.get_transform()
    vertices = [
        carla.Location(x=-bb.extent.x, y=-bb.extent.y, z=-bb.extent.z),
        carla.Location(x=bb.extent.x, y=-bb.extent.y, z=-bb.extent.z),
        carla.Location(x=bb.extent.x, y=bb.extent.y, z=-bb.extent.z),
        carla.Location(x=-bb.extent.x, y=bb.extent.y, z=-bb.extent.z),
        carla.Location(x=-bb.extent.x, y=-bb.extent.y, z=bb.extent.z),
        carla.Location(x=bb.extent.x, y=-bb.extent.y, z=bb.extent.z),
        carla.Location(x=bb.extent.x, y=bb.extent.y, z=bb.extent.z),
        carla.Location(x=-bb.extent.x, y=bb.extent.y, z=bb.extent.z)
    ]
    vertices = [transform.transform(v) for v in vertices]
    edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]
    for edge in edges:
        debug.draw_line(vertices[edge[0]], vertices[edge[1]], thickness=0.1, color=color, life_time=0.1)

def setup_tcp_server(port=9001):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', port))
    sock.listen(1)
    print(f"En attente de connexion Simulink sur le port {port}...")
    connection, _ = sock.accept()
    connection.settimeout(0.1)
    print("Connexion Simulink établie!")
    return connection

def send_data(conn, data):
    try:
        values = [data['MIO_Distance'], data['MIO_Velocity'], data['Ego_Velocity']]
        for val in values:
            conn.sendall(struct.pack('d', float(val)))
        print(f"Données envoyées: {values}")
    except Exception as e:
        print(f"Erreur d'envoi: {e}")
        raise

def receive_data(conn):
    try:
        values = []
        for _ in range(4):
            try:
                data = conn.recv(8)
                if len(data) < 8:
                    print("Données incomplètes reçues, réessai...")
                    time.sleep(0.01)
                    continue
                values.append(struct.unpack('d', data)[0])
            except socket.timeout:
                print("Timeout en attente de données")
                return None
        result = {
            'egoCarStop': bool(round(values[0])),
            'FCW_Activate': bool(round(values[1])),
            'Deceleration': float(values[2]),
            'AEB_Status': bool(round(values[3]))
        }
        print(f"Données reçues: {result}")
        return result
    except Exception as e:
        print(f"Erreur de réception: {e}")
        return None

def load_hud_logo():
    """Charge le logo pour le HUD en supprimant le fond blanc"""
    logo_path = r"C:\Users\thaoudi\Pictures\Camera Roll\téléchargement (1).png"
    try:
        if os.path.exists(logo_path):
            logo_surface = pygame.image.load(logo_path).convert_alpha()
            
            # Redimensionner le logo pour le HUD
            logo_surface = pygame.transform.scale(logo_surface, (100, 35))
            
            # Créer une nouvelle surface avec transparence
            transparent_logo = pygame.Surface((100, 35), pygame.SRCALPHA)
            
            # Parcourir chaque pixel pour rendre le blanc transparent
            for x in range(logo_surface.get_width()):
                for y in range(logo_surface.get_height()):
                    pixel = logo_surface.get_at((x, y))
                    # Si le pixel est blanc ou presque blanc, le rendre transparent
                    if pixel[0] > 240 and pixel[1] > 240 and pixel[2] > 240:
                        transparent_logo.set_at((x, y), (0, 0, 0, 0))  # Transparent
                    else:
                        transparent_logo.set_at((x, y), pixel)
            
            return transparent_logo
        else:
            print(f"Logo HUD non trouvé à l'emplacement: {logo_path}")
            return None
    except Exception as e:
        print(f"Erreur lors du chargement du logo HUD: {e}")
        return None

def draw_hud(screen, font, ego_speed, throttle, brake, ttc, collision_status,
             aeb_status, fcw_active, obstacle_type="NONE", distance=0, logo_surface=None):
    screen.fill((0, 0, 0))
    
    # Affichage du logo en haut à gauche si disponible
    if logo_surface:
        screen.blit(logo_surface, (10, 10))
        y_start = 50  # Décaler le texte vers le bas
    else:
        y_start = 20
    
    y_pos = y_start
    lines = [
        ("AEB SCENARIO 1 - VEHICLE-TO-VEHICLE", (255, 255, 255)),
        ("=" * 35, (255, 255, 255)),
        (f"SPEED: {ego_speed:.1f} km/h", (255, 255, 255)),
        (f"DISTANCE: {distance:.1f} m", (255, 255, 0) if distance < 10 else (255, 255, 255)),
        (f"THROTTLE: {throttle:.2f}", (0, 255, 0) if throttle < 0.1 else (255, 255, 0)),
        (f"BRAKE: {brake:.2f}", (255, 0, 0) if brake > 0.1 else (255, 255, 255)),
        (f"TTC: {ttc:.2f} s", (255, 0, 0) if ttc < 2.0 else (255, 255, 0) if ttc < 5.0 else (0, 255, 0)),
        (f"AEB: {aeb_status}", (255, 0, 0) if aeb_status == "ACTIVE" else (0, 255, 0)),
        (f"FCW: {'ACTIVE' if fcw_active else 'INACTIVE'}", (255, 165, 0) if fcw_active else (255, 255, 255)),
        (f"OBSTACLE: {obstacle_type}", (255, 255, 0)),
        ("STATUS: COLLISION!" if collision_status else "STATUS: MONITORING",
         (255, 0, 0) if collision_status else (0, 255, 0)),
        ("GRAPHS: REAL-TIME PLOTTING", (0, 255, 255))
    ]
    for line, color in lines:
        text = font.render(line, True, color)
        screen.blit(text, (10, y_pos))
        y_pos += 22
    pygame.display.flip()

def initialize_carla():
    try:
        print("Connexion au serveur CARLA...")
        client = carla.Client('localhost', 2000)
        client.set_timeout(15.0)
        print("Chargement de Town03...")
        world = client.load_world('Town03')
        time.sleep(2)
        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05
        world.apply_settings(settings)
        
        # Configuration météo optimale pour Scénario 1
        weather = carla.WeatherParameters(
            cloudiness=0.0,
            precipitation=0.0,
            sun_altitude_angle=70.0,
            fog_density=0.0
        )
        world.set_weather(weather)
        print("Météo configurée: Conditions optimales (ensoleillé, sec)")
        
        return client, world
    except Exception as e:
        print(f"ERREUR d'initialisation CARLA: {e}")
        raise

def spawn_vehicles(world):
    try:
        print("Nettoyage des véhicules existants...")
        for actor in world.get_actors().filter('*vehicle*'):
            actor.destroy()
        time.sleep(1)
        blueprint_library = world.get_blueprint_library()
        
        # Configuration du scénario 1: Conditions optimales
        ego_spawn = carla.Transform(
            carla.Location(x=80.206383, y=7.808423, z=0.275307),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0)
        )
        front_car_spawn = carla.Transform(
            carla.Location(x=126.206383, y=7.808423, z=0.275307),
            carla.Rotation(pitch=0.0, yaw=0.0, roll=0.0)
        )
        
        ego_bp = blueprint_library.find('vehicle.audi.tt')
        ego_vehicle = world.spawn_actor(ego_bp, ego_spawn)
        
        front_car_bp = blueprint_library.find('vehicle.tesla.model3')
        front_car = world.spawn_actor(front_car_bp, front_car_spawn)
        
        print("Scénario 1 configuré: Conditions météo optimales")
        return ego_vehicle, front_car
    except Exception as e:
        print(f"ERREUR de création des véhicules: {e}")
        raise

def main():
    try:
        # Initialisation des systèmes
        print("=== DÉMARRAGE AEB SCÉNARIO 1 ===")
        print("Initialisation pygame...")
        os.environ['SDL_VIDEO_WINDOW_POS'] = '100,100'
        pygame.init()
        screen = pygame.display.set_mode((400, 420))  # Ajusté pour le logo plus grand
        pygame.display.set_caption("AEB Scenario 1 Monitor")
        font = pygame.font.Font(None, 18)
        clock = pygame.time.Clock()
        
        # Chargement du logo pour le HUD
        hud_logo = load_hud_logo()
        
        # Initialisation CARLA
        client, world = initialize_carla()
        ego_vehicle, front_car = spawn_vehicles(world)
        
        # Initialisation du logger de données avec graphiques
        print("Initialisation des graphiques temps réel...")
        data_logger = AEBDataLogger()
        
        # Connexion TCP
        tcp_connection = setup_tcp_server(9001)
        
        # Variables de simulation
        collision_occurred = False
        aeb_status = "INACTIVE"
        fcw_active = False
        last_ttc = float('inf')
        ego_car_stop = False
        deceleration = 0.0
        obstacle_type = "NONE"
        
        print("=== SCÉNARIO 1 EN COURS: CONDITIONS OPTIMALES ===")

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Sauvegarde des graphiques en cours...")
                    data_logger.save_plots()
                    pygame.quit()
                    plt.close('all')
                    sys.exit()

            world.tick()
            
            # Calculs des métriques
            ego_speed = get_speed(ego_vehicle)
            front_car_speed = get_speed(front_car)
            distance = ego_vehicle.get_location().distance(front_car.get_location())
            obstacle_type = get_obstacle_type(front_car)
            
            # Visualisation
            draw_bounding_box(world, front_car, Color(r=255, g=165, b=0))
            
            # Calcul TTC
            relative_speed = ego_speed - front_car_speed
            ttc = distance / relative_speed if relative_speed > 0 else float('inf')
            last_ttc = ttc if ttc != float('inf') else last_ttc

            # Communication avec Simulink
            send_data(tcp_connection, {
                'MIO_Distance': distance,
                'MIO_Velocity': front_car_speed,
                'Ego_Velocity': ego_speed
            })

            sim_data = receive_data(tcp_connection)
            if sim_data:
                ego_car_stop = sim_data['egoCarStop']
                fcw_active = sim_data['FCW_Activate']
                deceleration = sim_data['Deceleration']
                aeb_status = "ACTIVE" if sim_data['AEB_Status'] else "INACTIVE"

            # Contrôle des véhicules
            front_car.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0))
            
            control = carla.VehicleControl()
            if ego_car_stop or collision_occurred:
                control.throttle = 0.0
                control.brake = 1.0
                aeb_status = "ACTIVE"
            else:
                control.throttle = max(0.3, 0.5 - deceleration)
                control.brake = deceleration

            ego_vehicle.apply_control(control)

            # Détection de collision
            if distance <= 2.0 and not collision_occurred:
                print(f"[COLLISION DÉTECTÉE] Distance: {distance:.1f}m | TTC: {ttc:.2f}s")
                collision_occurred = True

            # Enregistrement des données et mise à jour graphiques
            data_logger.add_data(distance, last_ttc, ego_speed, front_car_speed, 
                               aeb_status == "ACTIVE")

            # Mise à jour de l'affichage avec le logo
            draw_hud(screen, font, ego_speed * 3.6, control.throttle, control.brake,
                     last_ttc, collision_occurred, aeb_status, fcw_active, obstacle_type, distance, hud_logo)

            # Positionnement de la caméra
            spectator = world.get_spectator()
            ego_transform = ego_vehicle.get_transform()
            spectator.set_transform(carla.Transform(
                ego_transform.location + carla.Location(z=2, x=5, y=-10),
                carla.Rotation(pitch=0, yaw=90)))

            clock.tick(20)

    except KeyboardInterrupt:
        print("\nArrêt demandé par l'utilisateur")
        if 'data_logger' in locals():
            print("Sauvegarde des graphiques en cours...")
            data_logger.save_plots()
    except Exception as e:
        print(f"ERREUR: {e}")
    finally:
        print("Nettoyage des ressources...")
        if 'tcp_connection' in locals():
            tcp_connection.close()
        if 'world' in locals():
            print("Destruction des véhicules...")
            for actor in world.get_actors().filter('*vehicle*'):
                actor.destroy()
        if 'data_logger' in locals():
            print("Sauvegarde finale des graphiques...")
            data_logger.save_plots()
        pygame.quit()
        plt.close('all')
        print("Nettoyage terminé")

if __name__ == '__main__':
    print("=== DÉMARRAGE AEB SCÉNARIO 1  ===")
    main()