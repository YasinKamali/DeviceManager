import asyncio
from colorama import Fore, Style, init
from pyrogram import Client, raw
from pyrogram.raw import functions
from pyrogram.errors import FreshResetAuthorisationForbidden

print("For more information and the source code, visit the GitHub repository: https://github.com/YasinKamali")

# Initialize colorama for colored terminal output
init(autoreset=True)

# Get API credentials and session name from the user
api_id = int(input("Enter your API ID: ").strip())
api_hash = input("Enter your API Hash: ").strip()
session_name = input("Enter the name of your session file: ").strip()

# Ensure that .session is not included (Pyrogram adds it automatically)
if session_name.endswith(".session"):
    session_name = session_name[:-8]

# Initialize the Client with the provided session name and credentials
app = Client(
    session_name,  # Pyrogram handles the .session extension automatically
    api_id=api_id,
    api_hash=api_hash
)

print(Fore.GREEN + "Client initialized successfully!")


async def main():
    try:
        # Start the app
        await app.start()

        # Fetch the list of authorizations (devices)
        sessions: raw.types.account.Authorizations = await app.invoke(functions.account.GetAuthorizations())

        me = None  # Variable to store the current device (the one you are using)
        devices = []  # List to store all the devices

        # Display the device list with styling
        print(Fore.YELLOW + "\nDevice List:")

        # Enumerate through the sessions and display each device
        for idx, session in enumerate(sessions.authorizations, start=1):
            # Append the session (device) to the devices list
            devices.append(session)

            # Check if the current session is your own device
            if session.current:
                me = session
                print(Fore.GREEN + f"{idx}. (Your Device) {session.device_model} - {session.system_version} ({session.platform})")
            else:
                print(Fore.CYAN + f"{idx}. {session.device_model} - {session.system_version} ({session.platform})")

        # If the current device is found, print its details
        if me:
            print(Fore.RED + f"\nYour Current Device: {me.device_model} - {me.system_version} ({me.platform})\n")

        # Ask the user which device they would like to remove
        print(Fore.YELLOW + "Which device would you like to remove?")
        print("1. All devices except your own")
        print("2. All devices")
        print("3. Only your device")
        print("4. A specific device by number")

        # Loop to handle user input for device removal
        while True:
            try:
                # Get the user's choice for removing devices
                choice = input("Enter your choice: ")

                if choice == '1':
                    # Remove all devices except the current one
                    print(Fore.RED + "\nRemoving all devices except your own...")
                    for session in sessions.authorizations:
                        if not session.current:
                            await app.invoke(functions.account.ResetAuthorization(hash=session.hash))
                            print(Fore.GREEN + f"Device {session.device_model} has been removed.")
                    break

                elif choice == '2':
                    # Remove all devices
                    print(Fore.RED + "\nRemoving all devices...")
                    for session in sessions.authorizations:
                        await app.invoke(functions.account.ResetAuthorization(hash=session.hash))
                        print(Fore.GREEN + f"Device {session.device_model} has been removed.")
                    break

                elif choice == '3':
                    # Remove only the current device
                    print(Fore.RED + "\nRemoving only your current device...")
                    if me:
                        await app.invoke(functions.account.ResetAuthorization(hash=me.hash))
                        print(Fore.GREEN + f"Your device {me.device_model} has been removed.")
                    break

                elif choice == '4':
                    # Ask the user to select a specific device by number
                    while True:
                        try:
                            # Get the device number from the user
                            device_number = int(input("Enter the device number you want to remove: "))
                            if 1 <= device_number <= len(devices):
                                session = devices[device_number - 1]
                                await app.invoke(functions.account.ResetAuthorization(hash=session.hash))
                                print(Fore.GREEN + f"Device {session.device_model} has been removed.")
                                break
                            else:
                                print(Fore.RED + "Invalid device number. Please enter a valid number.")
                        except ValueError:
                            print(Fore.RED + "Please enter a valid number.")
                    break

                else:
                    # If the user enters an invalid choice
                    print(Fore.RED + "Invalid choice. Please choose a valid option.")
            except FreshResetAuthorisationForbidden:
                # Handle the error where Telegram doesn't allow removing other sessions when the current session was logged in recently
                print(Fore.RED + "Error: You can't reset other sessions because your current session was logged in recently.")
                break

    except Exception as e:
        # Catch any unexpected errors and print a message
        print(Fore.RED + f"An unexpected error occurred: {e}")


# Run the app
asyncio.run(main())
