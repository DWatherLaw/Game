extends Node3D

@export var target_scene: PackedScene = preload("res://scenes/Target.tscn")
@export var bullet_scene: PackedScene = preload("res://scenes/Bullet.tscn")

var targets = []
var score = 0

func _ready():
    # Maus für FPS-Steuerung sperren
    Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
    
    # Ziele spawnen
    spawn_targets()

func spawn_targets():
    # 5-10 Ziele an zufälligen Positionen spawnen
    var target_count = randi_range(5, 10)
    
    for i in target_count:
        var target = target_scene.instantiate()
        
        # Zufällige Position innerhalb der Arena (25x25)
        var x = randf_range(-20, 20)
        var z = randf_range(-20, 20)
        var y = randf_range(1, 5)  # Verschiedene Höhen
        
        target.position = Vector3(x, y, z)
        target.target_hit.connect(_on_target_hit)
        
        add_child(target)
        targets.append(target)

func _on_target_hit(target):
    score += 100
    targets.erase(target)
    target.queue_free()
    
    print("Treffer! Score: ", score)
    
    # Neue Ziele spawnen wenn alle zerstört
    if targets.size() == 0:
        spawn_targets()

func _input(event):
    if event.is_action_pressed("ui_cancel"):
        # ESC zum Beenden
        get_tree().quit()
