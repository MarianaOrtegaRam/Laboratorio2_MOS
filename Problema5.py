from pyomo.environ import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

# Función para cargar la matriz de costos desde un archivo CSV
def cargar_matriz_costos(archivo):
    df = pd.read_csv(archivo, index_col=0)
    return df.values

# Selección del archivo según el tamaño del problema
tamano_problema = 10  # Cambia este valor según el caso de prueba
archivos = {
    5: "cost_matrix_5_nodes_2.5_spread.csv",
    10: "cost_matrix_10_nodes_1.5_spread.csv",
    15: "cost_matrix_15_nodes_2.5_spread.csv",
    20: "cost_matrix_20_nodes_0.5_spread.csv",
    50: "cost_matrix_50_nodes_1.0_spread.csv",
    100: "cost_matrix_100_nodes_0.5_spread.csv"
}

archivo_costos = archivos[tamano_problema]
cost_matrix = cargar_matriz_costos(archivo_costos)
num_localidades = cost_matrix.shape[0]
num_equipos = 3  # Número de equipos de inspección

# Definición del modelo
model = ConcreteModel()

# Conjuntos
model.N = RangeSet(0, num_localidades - 1)  # Localidades
model.K = RangeSet(1, num_equipos)  # Equipos

# Parámetros
model.c = Param(model.N, model.N, initialize={(i, j): cost_matrix[i, j] if j < cost_matrix.shape[1] else 9999 for i in range(num_localidades) for j in range(num_localidades)}, mutable=True)

# Variables de decisión
model.x = Var(model.N, model.N, model.K, within=Binary)  # Si el equipo k viaja de i a j
model.u = Var(model.N, model.K, within=NonNegativeReals)  # Para evitar subtours

# Función objetivo: Minimizar la distancia total recorrida
model.obj = Objective(expr=sum(model.c[i, j] * model.x[i, j, k] for i in model.N for j in model.N if i != j for k in model.K), sense=minimize)

# Restricciones
# Cada equipo debe salir exactamente una vez desde la localidad 0
model.salida = ConstraintList()
for k in model.K:
    model.salida.add(sum(model.x[0, j, k] for j in model.N if j != 0) == 1)

# Cada equipo debe regresar exactamente una vez a la localidad 0
model.regreso = ConstraintList()
for k in model.K:
    model.regreso.add(sum(model.x[i, 0, k] for i in model.N if i != 0) == 1)

# Cada localidad debe ser visitada exactamente una vez por algún equipo
model.visita = ConstraintList()
for j in model.N:
    if j != 0:
        model.visita.add(sum(model.x[i, j, k] for i in model.N if i != j for k in model.K) == 1)

# Restricción de flujo: Lo que entra a una localidad debe salir
model.flujo = ConstraintList()
for k in model.K:
    for j in model.N:
        if j != 0:
            model.flujo.add(sum(model.x[i, j, k] for i in model.N if i != j) - sum(model.x[j, i, k] for i in model.N if i != j) == 0)

# Equilibrar la carga de trabajo entre equipos (ajuste de balanceo)
model.balanceo = ConstraintList()
for k in model.K:
    model.balanceo.add(sum(model.x[i, j, k] for i in model.N for j in model.N if i != j) >= (num_localidades // num_equipos) - 1)
    model.balanceo.add(sum(model.x[i, j, k] for i in model.N for j in model.N if i != j) <= (num_localidades // num_equipos) + 1)

# Subtours - Miller-Tucker-Zemlin Formulation
model.subtour = ConstraintList()
for i in model.N:
    for j in model.N:
        if i != j and i != 0 and j != 0:
            for k in model.K:
                model.subtour.add(model.u[i, k] - model.u[j, k] + num_localidades * model.x[i, j, k] <= num_localidades - 1)

# Resolver el modelo
solver = SolverFactory('glpk')
solver.solve(model)

# Visualización de rutas mejorada
plt.figure(figsize=(10, 8))
G = nx.DiGraph()
colors = {1: "red", 2: "blue", 3: "green"}  # Colores por equipo
for i in range(num_localidades):
    for j in range(num_localidades):
        for k in range(1, num_equipos + 1):
            if model.x[i, j, k].value is not None and model.x[i, j, k].value > 0.5:
                G.add_edge(i, j, label=f'Eq{k}', color=colors[k])

pos = nx.spring_layout(G, seed=42)
edges = G.edges()
colors = [G[u][v]['color'] for u, v in edges]
nx.draw(G, pos, with_labels=True, node_size=700, node_color="lightblue", edgecolors="black", edge_color=colors, width=2.0)
labels = nx.get_edge_attributes(G, 'label')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
plt.title("Rutas Óptimas para Equipos de Inspección")
plt.show()

# Mostrar solución
print("Rutas óptimas:")
for i in range(num_localidades):
    for j in range(num_localidades):
        for k in range(1, num_equipos + 1):
            if model.x[i, j, k].value is not None and model.x[i, j, k].value > 0.5:
                print(f"Equipo {k}: {i} -> {j}, Costo: {model.c[i, j].value:.2f}")
