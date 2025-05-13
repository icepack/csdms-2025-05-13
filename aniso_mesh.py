import numpy as np
import matplotlib.pyplot as plt
import firedrake
from firedrake import Constant, exp, sqrt, inner, outer, as_matrix, max_value
import animate

mesh = firedrake.UnitDiskMesh(3)
radius = 12e3
mesh.coordinates.dat.data[:] *= radius

cg1 = firedrake.FiniteElement("CG", "triangle", 1)
G = firedrake.TensorFunctionSpace(mesh, cg1)
g = animate.RiemannianMetric(G)

x = firedrake.SpatialCoordinate(mesh)
I = firedrake.Identity(2)

r_1 = Constant(6e3)
r_2 = Constant(10e3)
r = sqrt(inner(x, x))
α = Constant(100)
p = 4 * max_value(0, (r_2 - r) * (r - r_1)) / (r_1 * r_2)

δx = 1e3
expr = (I + α * p * outer(x, x) / (r_1 * r_2)) / δx**2

g.interpolate(expr)
g.set_parameters({"dm_plex_metric": {"hausdorff_number": 10.0}})
new_mesh = animate.adapt(mesh, g)
print(new_mesh.num_vertices())

with firedrake.CheckpointFile("aniso-mesh.h5", "w") as chk:
    chk.save_mesh(new_mesh)
