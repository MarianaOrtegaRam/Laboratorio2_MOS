from pyomo . environ import *
model = ConcreteModel ()

o = 2
d = 6
model.O = RangeSet (o) # Ciudades origen
model.D = RangeSet (d) # Ciudades destino
model.x = Var (model.O,model.D, within = NonNegativeReals)

c_values = {(1,1):0,
            (1,2):2.5,
            (1,3):1.6,
            (1,4):1.4,
            (1,5):0.8,
            (1,6):1.4,
            (2,1):2.5,
            (2,2):0,
            (2,3):2.0,
            (2,4):1.0,
            (2,5):1.0,
            (2,6):0.8}

l_values ={1: 550,
           2:700}

d_values ={1:125,
           2:175,
           3:225,
           4:250,
           5:225,
           6:200}

model.cij = Param(model.O, model.D, within=NonNegativeReals, initialize=c_values)
model.li = Param(model.O, within=NonNegativeReals, initialize=l_values)
model.dj = Param(model.D, within=NonNegativeReals, initialize=d_values)

model.obj = Objective (expr= sum (model.cij[i,j] * model.x[i,j] for i in model.O for j in model.D), sense= minimize )

model.suministro = ConstraintList ()
for i in model.O:
    model.suministro.add(sum( model.x[i,j] for j in model.D) <= model.li[i])

model.demanda = ConstraintList ()
for j in model.D :
    model.demanda.add(sum(model.x[i,j] for i in model.O ) == model.dj[j])

model.restricciones_prohibidas = ConstraintList()
model.restricciones_prohibidas.add(model.x[1,1] == 0)
model.restricciones_prohibidas.add(model.x[2,2] == 0)

from pyomo . opt import SolverFactory
solver = SolverFactory ('glpk')
solver.solve (model)

for i in model.O :
    for j in model.D :
        print ( f"x[{i},{j}]={model.x[i,j].value}" )

print("_____________MODIFICACIÓN DE DISPONIBILIDAD __________________")

#Modificación de l_values
model2 = ConcreteModel ()
model2.O = RangeSet (o) # Ciudades origen
model2.D = RangeSet (d) # Ciudades destino
model2.x = Var (model.O,model.D, within = NonNegativeReals)

l_values2 ={1: 600,
           2:650}

model2.li = Param(model2.O, within=NonNegativeReals, initialize=l_values2)
model2.cij = Param(model2.O, model2.D, within=NonNegativeReals, initialize=c_values)

model2.dj = Param(model2.D, within=NonNegativeReals, initialize=d_values)


model2.obj = Objective (expr= sum (model2.cij[i,j] * model2.x[i,j] for i in model2.O for j in model2.D), sense= minimize )

model2.suministro = ConstraintList ()
for i in model2.O:
    model2.suministro.add(sum( model2.x[i,j] for j in model2.D) <= model2.li[i])

model2.demanda = ConstraintList ()
for j in model2.D :
    model2.demanda.add(sum(model2.x[i,j] for i in model2.O ) == model2.dj[j])

model2.restricciones_prohibidas = ConstraintList()
model2.restricciones_prohibidas.add(model2.x[1,1] == 0)
model2.restricciones_prohibidas.add(model2.x[2,2] == 0)

from pyomo . opt import SolverFactory
solver2 = SolverFactory ('glpk')
solver2.solve (model2)

for i in model2.O :
    for j in model2.D :
        print ( f"x[{i},{j}]={model2.x[i,j].value}" )


import networkx as nx
import matplotlib.pyplot as plt

def plot_transportation(model, title="Flujo de Transporte"):
    G = nx.DiGraph()
    pos = {}  # Posiciones de los nodos para dibujar el gráfico

    # Definir nodos de origen y destino
    origenes = {1: "Bogotá", 2: "Medellín"}
    destinos = {1: "Cali", 2: "Barranquilla", 3: "Pasto", 4: "Tunja", 5: "Chía", 6: "Manizales"}

    # Agregar nodos
    for i in origenes:
        G.add_node(origenes[i], pos=(0, i))  # Orígenes a la izquierda
    for j in destinos:
        G.add_node(destinos[j], pos=(1, j))  # Destinos a la derecha

    # Agregar aristas con flujo
    edges = []
    edge_labels = {}
    for i in model.O:
        for j in model.D:
            flow = model.x[i, j].value
            if flow > 0:  # Solo mostramos flujos positivos
                G.add_edge(origenes[i], destinos[j], weight=flow)
                edges.append((origenes[i], destinos[j]))
                edge_labels[(origenes[i], destinos[j])] = f"{flow:.1f} tons"

    # Dibujar la red
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="lightblue", font_size=10, edge_color="gray")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)

    plt.title(title)
    plt.show()

# Llamar a la función después de resolver el modelo
plot_transportation(model, title="Flujo de Transporte Original")


import numpy as np

# Datos antes y después (ajústalos con los resultados del modelo)
destinos = ["Cali", "Barranquilla", "Pasto", "Tunja", "Chía", "Manizales"]
antes_bogota = [0, 175, 225, 0, 150, 0]
antes_medellin = [125, 0, 0, 250, 75, 200]
despues_bogota = [0, 200, 250, 0, 180, 0]  # Valores de la nueva ejecución
despues_medellin = [125, 0, 0, 250, 45, 200]  # Ajusta con la nueva solución

x = np.arange(len(destinos))
width = 0.4

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(x - width/2, antes_bogota, width, label="Bogotá (Antes)", color="blue", alpha=0.6)
ax.bar(x + width/2, despues_bogota, width, label="Bogotá (Después)", color="blue", hatch="/")

ax.bar(x - width/2, antes_medellin, width, bottom=antes_bogota, label="Medellín (Antes)", color="orange", alpha=0.6)
ax.bar(x + width/2, despues_medellin, width, bottom=despues_bogota, label="Medellín (Después)", color="orange", hatch="\\")

ax.set_xlabel("Ciudades Destino")
ax.set_ylabel("Toneladas Transportadas")
ax.set_title("Comparación de Transporte Antes y Después")
ax.set_xticks(x)
ax.set_xticklabels(destinos)
ax.legend()

plt.show()


