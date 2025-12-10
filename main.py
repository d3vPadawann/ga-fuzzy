import cv2
import numpy as np
import pygad
import math

# --- CONFIGURAÇÕES DO AMBIENTE ---
TRACK_IMAGE_PATH = 'circuit1.png'
OUTPUT_VIDEO_PATH = 'resultado_final.mp4'
NUM_SENSORS = 5
NUM_RULES = 10 

class CarSimulation:
    def __init__(self, track_path):
        self.original_map = cv2.imread(track_path, cv2.IMREAD_GRAYSCALE)
        if self.original_map is None:
            raise FileNotFoundError(f"Imagem {track_path} não encontrada.")
        
        _, self.track = cv2.threshold(self.original_map, 127, 255, cv2.THRESH_BINARY)
        self.h, self.w = self.track.shape
        self.start_x, self.start_y = self.find_start_point()
        self.reset()

    def find_start_point(self):
        mid_x = self.w // 4
        for y in range(self.h):
            if self.track[y, mid_x] == 255:
                return mid_x, y + 20
        return 50, 50

    def reset(self):
        self.x = float(self.start_x)
        self.y = float(self.start_y)
        self.angle = 0 
        self.alive = True
        self.distance_traveled = 0
        self.steps = 0
        # Memória de setores visitados
        self.visited_sectors = set()
        self.total_rotation = 0.0

    def get_sensors(self):
        readings = []
        sensor_endpoints = [] 
        
        for s_angle in [-45, -22.5, 0, 22.5, 45] :
            rad = math.radians(self.angle + s_angle)
            dist = 0
            for d in range(1, 100 + 1):
                tx = int(self.x + math.cos(rad) * d)
                ty = int(self.y + math.sin(rad) * d)
                
                if tx < 0 or tx >= self.w or ty < 0 or ty >= self.h:
                    dist = d
                    break
                if self.track[ty, tx] == 0: 
                    dist = d
                    break
                dist = d
            readings.append(dist)
            ex = int(self.x + math.cos(rad) * dist)
            ey = int(self.y + math.sin(rad) * dist)
            sensor_endpoints.append((ex, ey))
            
        return readings, sensor_endpoints

    def step(self, steering):
        if not self.alive: return

        self.total_rotation += abs(steering)

        self.angle += steering
        rad = math.radians(self.angle)
        
        current_speed = 5 
        
        new_x = self.x + math.cos(rad) * current_speed
        new_y = self.y + math.sin(rad) * current_speed

        ix, iy = int(new_x), int(new_y)
        
        # Verifica colisão
        if ix < 0 or ix >= self.w or iy < 0 or iy >= self.h or self.track[iy, ix] == 0:
            self.alive = False
        else:
            self.x = new_x
            self.y = new_y
            self.distance_traveled += current_speed
            self.steps += 1
            
            sector = (int(self.x // 20), int(self.y // 20))
            self.visited_sectors.add(sector)

# --- LÓGICA FUZZY ---
def fuzzy_membership(value, set_idx):
    centers = [0, 30, 50, 75, 100]
    c = centers[set_idx]
    if set_idx == 0: 
        if value <= 0: return 1.0
        if value >= 25: return 0.0
        return (25 - value) / 25.0
    elif set_idx == 4:
        if value >= 100: return 1.0
        if value <= 75: return 0.0
        return (value - 75) / 25.0
    else:
        if value <= c - 25 or value >= c + 25: return 0.0
        if value < c: return (value - (c - 25)) / 25.0
        return ((c + 25) - value) / 25.0

def evaluate_fuzzy_system(sensors, genome):
    output_activations = [0.0] * 5 
    genes_per_rule = NUM_SENSORS + 1
    for r in range(NUM_RULES):
        rule_start = r * genes_per_rule
        rule_genes = genome[rule_start : rule_start + genes_per_rule]
        antecedent_activation = 1.0
        rule_active = False 
        for i, s_val in enumerate(sensors):
            req_level = int(rule_genes[i])
            if req_level < 5: 
                mu = fuzzy_membership(s_val, req_level)
                antecedent_activation = min(antecedent_activation, mu)
                rule_active = True
        if rule_active and antecedent_activation > 0:
            out_action = int(rule_genes[NUM_SENSORS]) % 5
            output_activations[out_action] = max(output_activations[out_action], antecedent_activation)
    outputs_center = [-20, -10, 0, 10, 20] 
    
    numerator = 0.0
    denominator = 0.0
    for i in range(5):
        numerator += output_activations[i] * outputs_center[i]
        denominator += output_activations[i]
    if denominator == 0: return 0 
    return numerator / denominator

def run_simulation_visual(genome, title="Simulacao", record=False, writer=None):
    sim_env.reset()
    
    while sim_env.alive and sim_env.steps < 1500: # Max steps para não ficar infinito
        sensors, sensor_points = sim_env.get_sensors()
        steering = evaluate_fuzzy_system(sensors, genome)
        sim_env.step(steering)
        
        display = cv2.cvtColor(sim_env.track, cv2.COLOR_GRAY2BGR)
        cx, cy = int(sim_env.x), int(sim_env.y)
        cv2.circle(display, (cx, cy), 6, (0, 0, 255), -1) 
        for i, point in enumerate(sensor_points):
            dist = sensors[i]
            color = (0, 255, 0) if dist > 50 else (255, 0, 0)
            cv2.line(display, (cx, cy), point, color, 1)

        info_text = f"{title} | Dist: {int(sim_env.distance_traveled)}"
        cv2.putText(display, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        cv2.imshow("Treinamento Fuzzy", display)
        
        if record and writer:
            writer.write(display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            sim_env.alive = False 

# --- ALGORITMO GENÉTICO ---
try:
    sim_env = CarSimulation(TRACK_IMAGE_PATH)
except Exception as e:
    print(e)
    exit()

def fitness_func(ga_instance, solution, solution_idx):
    sim_env.reset()
    max_steps = 1500 
    
    for _ in range(max_steps):
        sensors, _ = sim_env.get_sensors()
        steering = evaluate_fuzzy_system(sensors, solution)
        sim_env.step(steering)
        if not sim_env.alive: break
            
    exploration_score = len(sim_env.visited_sectors) * 10 
    stability_penalty = sim_env.total_rotation * 0.5
    time_penalty = sim_env.steps * 0.1
    final_fitness = exploration_score - stability_penalty - time_penalty
    return max(final_fitness, 0.0)
    
def on_generation(ga_instance):
    best_solution, best_fitness, _ = ga_instance.best_solution()
    gen = ga_instance.generations_completed
    print(f"Geração {gen} - Melhor Fitness: {best_fitness:.2f} (Visualizando...)")
    
    run_simulation_visual(best_solution, title=f"Geracao {gen} (Melhor)")

num_genes = NUM_RULES * (NUM_SENSORS + 1)
gene_space = []
for _ in range(NUM_RULES):
    for _ in range(NUM_SENSORS):
        gene_space.append({'low': 0, 'high': 6})
    gene_space.append({'low': 0, 'high': 5})

ga_instance = pygad.GA(
    num_generations=20, 
    num_parents_mating=4,
    fitness_func=fitness_func,
    sol_per_pop=20,
    num_genes=num_genes,
    gene_type=int,
    gene_space=gene_space,
    parent_selection_type="rank",
    crossover_type="single_point",
    mutation_type="random",
    mutation_percent_genes=10,
    on_generation=on_generation, 
    keep_parents=2
)

if __name__ == "__main__":
    print("Iniciando Evolução... Abrindo janela treinamento fuzzy.")
    ga_instance.run()

    print("\nTreinamento Finalizado - Salvando video de melhor geracao")
    best_solution, best_fitness, _ = ga_instance.best_solution()
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = 30.0
    video_writer = cv2.VideoWriter(OUTPUT_VIDEO_PATH, fourcc, fps, (sim_env.w, sim_env.h))
    
    run_simulation_visual(best_solution, title="Melhor", record=True, writer=video_writer)
    
    video_writer.release()
    cv2.destroyAllWindows()
    print(f"Vídeo salvo em: {OUTPUT_VIDEO_PATH}")