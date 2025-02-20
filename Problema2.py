from pyomo . environ import *
model = ConcreteModel ()

o = 2
d = 6
model.O = RangeSet (o) # Ciudades origen
model.D = RangeSet (d) # Ciudades destino
model.x = Var ( model.O , model.D , within = NonNegativeReals )

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
            (2,6):0.8,

}
model.cij = Var(model.O, model.D, within=NonNegativeReals, initialize=c_values)

model.obj = Objective ( expr = sum (c[i , j ] * model .x [i , j] for
i in model .I for j in model .J) , sense = minimize )