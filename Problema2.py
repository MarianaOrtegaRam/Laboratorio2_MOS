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