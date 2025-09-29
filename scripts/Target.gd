extends RigidBody3D

signal target_hit(target)

func _ready():
    # Rotes Material für Ziel
    var material = StandardMaterial3D.new()
    material.albedo_color = Color.RED
    $MeshInstance3D.material_override = material

func hit():
    # Signal senden wenn getroffen
    target_hit.emit(self)
