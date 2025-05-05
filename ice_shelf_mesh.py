import gmsh

gmsh.initialize()

R = 200e3
δx = 5e3

geometry = gmsh.model.geo

x1 = geometry.add_point(-R, 0, 0, δx)
x2 = geometry.add_point(+R, 0, 0, δx)

center1 = geometry.add_point(0, 0, 0, δx)
center2 = geometry.add_point(0, -4 * R, 0, δx)

arcs = [
    geometry.add_circle_arc(x1, center1, x2),
    geometry.add_circle_arc(x2, center2, x1)
]

line_loop = geometry.add_curve_loop(arcs)
plane_surface = geometry.add_plane_surface([line_loop])

physical_lines = [geometry.add_physical_group(1, [arc]) for arc in arcs]
physical_surface = geometry.add_physical_group(2, [plane_surface])

geometry.synchronize()
gmsh.model.mesh.generate(2)
gmsh.write("ice-shelf.msh")
gmsh.finalize()
