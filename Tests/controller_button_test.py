from inputs import get_gamepad


def main():
    print("Listening for L1, L2, R1, R2 button presses...")
    while True:
        events = get_gamepad()
        for event in events:
            # L1 and R1 are digital buttons
            if event.ev_type == "Key":
                if event.code == "BTN_TL" and event.state == 1:
                    print("L1 pressed")
                elif event.code == "BTN_TR" and event.state == 1:
                    print("R1 pressed")

            # L2 and R2 are analog triggers
            elif event.ev_type == "Absolute":
                if event.code == "ABS_Z" and event.state > 0:
                    print("L2 pressed")
                elif event.code == "ABS_RZ" and event.state > 0:
                    print("R2 pressed")


if __name__ == "__main__":
    main()
