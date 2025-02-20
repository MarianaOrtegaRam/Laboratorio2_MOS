from pyomo . environ import *
model = ConcreteModel ()

o = 2
d = 6
model.O = RangeSet (o) # Ciudades origen
model.D = RangeSet (d) # Ciudades destino
model.x = Var ( model.O , model.D , within = NonNegativeReals )


model.obj = Objective ( expr = sum (c[i , j ] * model .x [i , j] for
i in model .I for j in model .J) , sense = minimize )