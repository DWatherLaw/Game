extends CharacterBody2D

const SPEED = 300.0

func _physics_process(delta):
	# Bewegung
	var direction = Vector2.ZERO
	
	if Input.is_action_pressed("ui_right"):
		direction.x += 1
	if Input.is_action_pressed("ui_left"):
		direction.x -= 1
	if Input.is_action_pressed("ui_down"):
		direction.y += 1
	if Input.is_action_pressed("ui_up"):
		direction.y -= 1
	
	velocity = direction.normalized() * SPEED
	move_and_slide()
	
	# Schießen
	if Input.is_action_just_pressed("ui_accept"):
		shoot()

func shoot():
	print("Schuss abgefeuert!")
	# Hier werden wir später Projektile erstellen
