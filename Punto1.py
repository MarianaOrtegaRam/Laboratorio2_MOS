from pyomo.environ import *
from pyomo.opt import SolverFactory
import matplotlib.pyplot as plt
import numpy as np

Model = ConcreteModel()

# Conjuntos --------------------------------------

Model.R = RangeSet(1, 5)  # Recursos: 1=Alimentos, 2=Medicinas, 3=Equipos Médicos, 4=Agua Potable, 5=Mantas
Model.A = RangeSet(1, 3)        # Aviones: 1, 2, 3


# Parámetros -------------------------------------------------------

Model.v = Param(Model.R, initialize={1: 3.33, 2: 20.00, 3: 6.00, 4: 3.33, 5: 4.00})  # Valor por KG
Model.p = Param(Model.R, initialize={1: 15000, 2: 5000, 3: 20000, 4: 18000, 5: 10000})  # Peso en KG
Model.vol = Param(Model.R, initialize={1: 8, 2: 2, 3: 10, 4: 12, 5: 6})  # Volumen en m^3
Model.P = Param(Model.A, initialize={1: 30000, 2: 40000, 3: 50000})  # Capacidad máxima de peso de los aviones
Model.V = Param(Model.A, initialize={1: 25, 2: 30, 3: 35})  # Capacidad máxima de volumen de los aviones


# Variable de decisión --------------------------

Model.x = Var(Model.R, Model.A, within=NonNegativeReals)


# Función objetivo ------------------------------

Model.obj = Objective(expr=sum(Model.v[i] * Model.x[i, j] for i in Model.R for j in Model.A), sense=maximize)


# Restricciones ------------------------------------------------------

# Restricción de capacidad de peso en los aviones
Model.weight_capacity = ConstraintList()
for j in Model.A:
    Model.weight_capacity.add(expr=(sum(Model.p[i] * Model.x[i, j] for i in Model.R) <= Model.P[j]))

# Restricción de capacidad de volumen en los aviones
Model.volume_capacity = ConstraintList()
for j in Model.A:
    Model.volume_capacity.add(expr=(sum(Model.vol[i] * Model.x[i, j] for i in Model.R) <= Model.V[j]))

# Restricción de disponibilidad de recursos 
Model.resource_availability = ConstraintList()
for i in Model.R:
    Model.resource_availability.add(expr=(sum(Model.x[i, j] for j in Model.A) <= Model.p[i]))

# Restricción de indivisibilidad de equipos médicos
""" Model.incompatibility = ConstraintList()
for i in Model.R:
    if i == 3:
        Model.incompatibility.add(expr=((Model.x[i, j])),within=NonNegativeIntegers)
 """
# Restricción de seguridad de medicamentos
Model.safety_medications = ConstraintList()
Model.safety_medications.add(expr = Model.x[2, 1] == 0)

# Restricción de incompatibilidad equipos médicos y agua
Model.incompatibility = ConstraintList()
for j in Model.A:
    Model.incompatibility.add(expr = Model.x[3, j] + Model.x[4, j] == 0)

# Solver ----------------------------------------

solver=SolverFactory('glpk')
solver.solve(Model)

Model.display()

# ----------------- GRÁFICO -----------------

# Obtener los valores de la solución
recursos = list(Model.R)
aviones = list(Model.A)

# Crear una matriz para almacenar la cantidad de cada recurso en cada avión
asignaciones = np.zeros((len(recursos), len(aviones)))

for i in recursos:
    for j in aviones:
        asignaciones[i-1, j-1] = Model.x[i, j].value if Model.x[i, j].value is not None else 0  # Asegurar que no haya None

# Graficar
plt.figure(figsize=(10, 6))

for i in range(len(recursos)):
    plt.plot(aviones, asignaciones[i], marker='o', linestyle='-', label=f'Recurso {i+1}')

plt.xlabel('Aviones')
plt.ylabel('Cantidad de recurso asignado')
plt.title('Distribución de recursos en los aviones')
plt.xticks(aviones)
plt.legend()
plt.grid()

# Mostrar gráfico
plt.show()