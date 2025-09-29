extends CharacterBody3D

@export var speed = 5.0
@export var jump_velocity = 4.5
@export var mouse_sensitivity = 0.002

@onready var camera = $Camera3D
@onready var raycast = $Camera3D/RayCast3D

var gravity = ProjectSettings.get_setting("physics/3d/default_gravity")

func _ready():
    # Maus sperren
    Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _input(event):
    if event is InputEventMouseMotion:
        # Maus-Look für Ego-Perspektive
        rotate_y(-event.relative.x * mouse_sensitivity)
        camera.rotate_x(-event.relative.y * mouse_sensitivity)
        camera.rotation.x = clamp(camera.rotation.x, -PI/2, PI/2)
    
    if event.is_action_pressed("shoot"):
        shoot()

func _physics_process(delta):
    # Schwerkraft anwenden
    if not is_on_floor():
        velocity.y -= gravity * delta

    # Sprung
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity

    # Bewegung
    var input_dir = Vector2()
    if Input.is_action_pressed("move_left"):
        input_dir.x -= 1
    if Input.is_action_pressed("move_right"):
        input_dir.x += 1
    if Input.is_action_pressed("move_forward"):
        input_dir.y += 1
    if Input.is_action_pressed("move_backward"):
        input_dir.y -= 1
    
    var direction = (transform.basis * Vector3(input_dir.x, 0, -input_dir.y)).normalized()
    if direction:
        velocity.x = direction.x * speed
        velocity.z = direction.z * speed
    else:
        velocity.x = move_toward(velocity.x, 0, speed)
        velocity.z = move_toward(velocity.z, 0, speed)

    move_and_slide()

func shoot():
    # Raycast für sofortige Treffer-Erkennung
    if raycast.is_colliding():
        var collider = raycast.get_collider()
        if collider.has_method("hit"):
            collider.hit()
