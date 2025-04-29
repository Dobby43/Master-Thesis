from pathlib import Path
import Rhino.Geometry as Rg
import Rhino.FileIO as Rfi
import Rhino.DocObjects as Rdo


def import_step_file_to_rhino_file(
    file_path: Path,
    target_point: list[float],
    target_3dm_path: Path,
    target_layer_name="robot",
):
    """
    DESCRIPTION:
    Imports a .3dm file (file_path) into an existing Rhino file (target_3dm_path),
    moves the contents around the origin to the target_point position, and adds the specified layer to it.

    :param file_path: Path to the .3dm file.
    :param target_point: Position of Robotroot relative to printbed origin (make sure x-axis and  y-axis of printbed and robot are parallel)
    :param target_3dm_path: Path to the .3dm file.
    :param target_layer_name: layer in which the robot file is imported to
    """

    # Load data from .3dm file
    robot_model = Rfi.File3dm.Read(str(file_path))
    rhino_file = Rfi.File3dm.Read(str(target_3dm_path))

    if not robot_model:
        print(f"[ERROR] File for Robot '{str(file_path)}' can't be read")
        return

    # Find target layer
    target_layer_index = next(
        (l for l in rhino_file.Layers if l.Name == target_layer_name), None
    ).Index

    # Find target point
    tp = Rg.Point3d(*target_point)

    # Calculate transformation necessary
    translation = Rg.Transform.Translation(Rg.Vector3d(tp))

    # Add geometry to file
    enumerator = robot_model.Objects.GetEnumerator()
    while enumerator.MoveNext():
        obj = enumerator.Current
        geom = obj.Geometry.Duplicate()
        if geom:
            geom.Transform(translation)
            attr = Rdo.ObjectAttributes()
            attr.LayerIndex = target_layer_index

            if isinstance(geom, Rg.Point):
                rhino_file.Objects.AddPoint(geom.Location, attr)
            elif isinstance(geom, Rg.Curve):
                rhino_file.Objects.AddCurve(geom, attr)
            elif isinstance(geom, Rg.Line):
                rhino_file.Objects.AddLine(geom, attr)
            elif isinstance(geom, Rg.Brep):
                rhino_file.Objects.AddBrep(geom, attr)
            elif isinstance(geom, Rg.Mesh):
                rhino_file.Objects.AddMesh(geom, attr)
            else:
                print(f"[WARNING] Geometry type {type(geom)} not supported")
                print(
                    "[INFO] Make sure robot.3dm file only consists of Points, Curves, Lines, Brep, Mesh\n"
                )

    # Save file
    rhino_file.Write(str(target_3dm_path), 8)
    print(
        f"[INFO] Robot from '{file_path}' imported in '{target_3dm_path}' onto layer '{target_layer_name}' at position {tp}.\n"
    )
