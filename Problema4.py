from pyomo.environ import *
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

# Definición del modelo
model = ConcreteModel()

# Conjuntos
model.N = RangeSet(1, 7)  # Nodos

# Parámetros: coordenadas de los nodos
coordenadas = {
    1: (20, 6), 2: (22, 1), 3: (9, 2), 4: (3, 25),
    5: (21, 10), 6: (29, 2), 7: (14, 12)
}

# Función para calcular la distancia euclidiana
def distancia(i, j):
    return np.sqrt((coordenadas[i][0] - coordenadas[j][0])**2 +
                   (coordenadas[i][1] - coordenadas[j][1])**2)

# Generar matriz de costos y definir enlaces válidos
E = {}
costo = {}
for i in model.N:
    for j in model.N:
        if i != j:
            d = distancia(i, j)
            if d <= 20:  # Restricción de distancia máxima
                E[(i, j)] = 1
                costo[(i, j)] = d

# Conjunto de enlaces válidos
model.E = Set(initialize=E.keys())

# Parámetros
model.cij = Param(model.E, initialize=costo)

# Variables de decisión
model.x = Var(model.E, within=Binary)

# Función objetivo: minimizar el costo total de la ruta
model.obj = Objective(expr=sum(model.x[i, j] * model.cij[i, j] for (i, j) in model.E), sense=minimize)

# Restricciones
model.origen = Constraint(expr=sum(model.x[4, j] for j in model.N if (4, j) in model.E) == 1)
model.destino = Constraint(expr=sum(model.x[i, 6] for i in model.N if (i, 6) in model.E) == 1)

# Conservación de flujo
model.flujo = ConstraintList()
for i in model.N:
    if i not in [4, 6]:
        model.flujo.add(sum(model.x[i, j] for j in model.N if (i, j) in model.E) -
                        sum(model.x[j, i] for j in model.N if (j, i) in model.E) == 0)

# Resolver el modelo
solver = SolverFactory('glpk')
solver.solve(model)

# Mostrar resultados
print("Ruta de mínimo costo:")
costo_total = 0
aristas_seleccionadas = []
for (i, j) in model.E:
    if model.x[i, j].value > 0.5:
        print(f"{i} -> {j} con costo {model.cij[i, j]:.2f}")
        costo_total += model.cij[i, j]
        aristas_seleccionadas.append((i, j))
print(f"Costo total: {costo_total:.2f}")

# Visualización del grafo con diferentes estilos
plt.figure(figsize=(10, 8))
G = nx.Graph()
for nodo, coord in coordenadas.items():
    G.add_node(nodo, pos=coord)

pos = nx.spring_layout(G, seed=42)  # Distribución más dinámica

# Dibujar nodos
nx.draw_networkx_nodes(G, pos, node_size=700, node_color="lightblue")
nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")

# Dibujar aristas seleccionadas con diferentes estilos
for (i, j) in aristas_seleccionadas:
    plt.plot([coordenadas[i][0], coordenadas[j][0]], [coordenadas[i][1], coordenadas[j][1]],
             linestyle='dashed', color='green', linewidth=2)

plt.xlabel("Coordenada X")
plt.ylabel("Coordenada Y")
plt.title("Camino Mínimo resaltado entre los Nodos 4 y 6")
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()
