import numpy as np


def transform_to_robotroot(points, transformation) -> list[dict]:
    transformed_points = []

    for point in points:
        # Homogene Koordinate erstellen
        vector = np.array([point["X"], point["Y"], point["Z"], 1])

        # Transformation ausführen
        transformed_point = transformation @ vector

        transformed_points.append(transformed_point[:4])

    return transformed_points


if __name__ == "__main__":
    points = [
        {
            "Move": "G1",
            "X": 1,
            "Y": 1,
            "Z": 0,
            "E_Rel": 95.493,
            "Layer": 0,
            "Type": "wall_inner",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 1,
            "Y": 1,
            "Z": 1,
            "E_Rel": 95.493,
            "Layer": 0,
            "Type": "wall_inner",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G0",
            "X": 1,
            "Y": 2,
            "Z": 0,
            "E_Rel": 0,
            "Layer": 0,
            "Type": "travel",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G0",
            "X": 1,
            "Y": 2,
            "Z": 1,
            "E_Rel": 0,
            "Layer": 0,
            "Type": "travel",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 1,
            "Y": 3,
            "Z": 0,
            "E_Rel": 57.326,
            "Layer": 0,
            "Type": "surface",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 1,
            "Y": 3,
            "Z": 1,
            "E_Rel": 57.326,
            "Layer": 0,
            "Type": "surface",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 1,
            "Y": 4,
            "Z": 0,
            "E_Rel": 57.326,
            "Layer": 0,
            "Type": "surface",
            "Layer_Height": 15.0,
        },
        {
            "Move": "G1",
            "X": 1,
            "Y": 4,
            "Z": 1,
            "E_Rel": 57.326,
            "Layer": 0,
            "Type": "surface",
            "Layer_Height": 15.0,
        },
    ]

    transformation = np.array(
        [
            [1.00000e00, 0.00000e00, 0.00000e00, 1.5e03],
            [0.00000e00, 1.00000e00, 0.00000e00, -2.2e03],
            [0.00000e00, 0.00000e00, 1.00000e00, 2.5e02],
            [0.00000e00, 0.00000e00, 0.00000e00, 1.00000e00],
        ]
    )

    transformed_points = transform_to_robotroot(points, transformation)
    for line in transformed_points:
        print(line)
