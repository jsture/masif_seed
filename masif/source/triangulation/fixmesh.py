import numpy as np
from numpy.linalg import norm
import pymesh

"""
fixmesh.py: Regularize a protein surface mesh. 
- based on code from the PyMESH documentation. 
"""


def fix_mesh(mesh, resolution, detail="normal"):
    bbox_min, bbox_max = mesh.bbox;
    diag_len = norm(bbox_max - bbox_min);
    if detail == "normal":
        target_len = diag_len * 5e-3;
    elif detail == "high":
        target_len = diag_len * 2.5e-3;
    elif detail == "low":
        target_len = diag_len * 1e-2;
    
    target_len = 1.2 # resolution
    #print("Target resolution: {} mm".format(target_len));
    # PGC 2017: Remove duplicated vertices first
    mesh, _ = pymesh.remove_duplicated_vertices(mesh, 0.001)
# 120181 has valance 4
# Warning: Complex edge loop detected!  Vertex 29429 has valance 4
# Warning: Complex edge loop detected!  Vertex 25799 has valance 4
# Warning: Complex edge loop detected!  Vertex 30796 has valance 4

    count = 0;
    print("Removing degenerated triangles")
    mesh, __ = pymesh.remove_degenerated_triangles(mesh, 100);
    mesh, __ = pymesh.split_long_edges(mesh, target_len);
    num_vertices = mesh.num_vertices;
    while True:
        foo = [120181, 29429, 25799, 30796]
        mesh, info = pymesh.collapse_short_edges(mesh, 1e-6);
        try:
            print(info)
            print(mesh.vertices[foo])
        except:
            try:
              print(mesh.vertices[foo[1:]])
            except:
                print("balls")
        mesh, info = pymesh.collapse_short_edges(mesh, target_len,
                preserve_feature=True);
        print(info)
        mesh, info = pymesh.remove_obtuse_triangles(mesh, 150.0, 100);
        print(info)
                
        if mesh.num_vertices == num_vertices:
            break;

        num_vertices = mesh.num_vertices;
        #print("#v: {}".format(num_vertices));
        count += 1;
        if count > 10: break;

    mesh = pymesh.resolve_self_intersection(mesh);
    mesh, __ = pymesh.remove_duplicated_faces(mesh);
    mesh = pymesh.compute_outer_hull(mesh);
    mesh, __ = pymesh.remove_duplicated_faces(mesh);
    mesh, __ = pymesh.remove_obtuse_triangles(mesh, 179.0, 5);
    mesh, __ = pymesh.remove_isolated_vertices(mesh);
    mesh, _ = pymesh.remove_duplicated_vertices(mesh, 0.001)
    
    return mesh
