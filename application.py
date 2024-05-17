import os
import subprocess

# This program was not designed to be ran in an IDE such as Visual Code. It is recommended to simply run the application.py file in the terminal

def twoTieredApplication():
    # Change directory to the two-tiered application folder
    os.chdir('two-tiered application')

    # Run the server.py and client.py scripts
    subprocess.Popen(["start", "cmd", "/k", "python", "server.py"], shell=True)
    subprocess.Popen(["start", "cmd", "/k", "python", "client.py"], shell=True)



def threeTieredApplication():
    # Change directory to the three-tiered application folder
    os.chdir('three-tiered application')

    # Run the server-1.py, server-2.py and client.py scripts
    subprocess.Popen(["start", "cmd", "/k", "python", "server-1.py"], shell=True)
    subprocess.Popen(["start", "cmd", "/k", "python", "server-2.py"], shell=True)
    subprocess.Popen(["start", "cmd", "/k", "python", "client.py"], shell=True)

while True:
    print("----------------------------------------------------------\nWelcome to the OUST Application Selector\nPlease Select '1' or '2' to Run the Designated Program: \n")
    print("1. Run Two-Tiered Application")
    print("2. Run Three-Tiered Application\n")
    choice = input("Enter: ")

    if choice == '1':
        twoTieredApplication()
        break
    elif choice == '2':
        threeTieredApplication()
        break
    else:
        print("\nInvalid. Please Input Either '1' or '2'.")
    