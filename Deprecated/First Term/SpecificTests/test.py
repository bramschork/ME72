import pygame

# Initialize pygame and the joystick module
pygame.init()
pygame.joystick.init()

# Check for connected joysticks
if pygame.joystick.get_count() == 0:
    print("No joystick detected. Please connect a controller.")
    pygame.quit()
    exit()

# Initialize the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Get number of axes
num_axes = joystick.get_numaxes()
print(f"Joystick Name: {joystick.get_name()}")
print(f"Number of Axes: {num_axes}")

# Print the axes values continuously
print("Move the joystick to see the axis values (Ctrl+C to exit).")

try:
    while True:
        # Process pygame events
        pygame.event.pump()
        
        # Print each axis value
        for i in range(num_axes):
            axis_value = joystick.get_axis(i)
            print(f"Axis {i}: {axis_value:.2f}")
        
        # Separate updates
        print("-" * 30)
        pygame.time.wait(500)  # Wait 500ms between updates
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    pygame.quit()
