import os
import subprocess

def run_two_tiered_application():
    # Change directory to the two-tiered application folder
    os.chdir('two-tiered application')

    # Run the server.py and client.py scripts
    subprocess.run(['python', 'server.py'])
    subprocess.run(['python', 'client.py'])

def run_three_tiered_application():
    # Change directory to the three-tiered application folder
    os.chdir('three-tiered application')

    # Run the server-2.py, server-1.py, and client.py scripts in order
    subprocess.run(['python', 'server-2.py'])
    subprocess.run(['python', 'server-1.py'])
    subprocess.run(['python', 'client.py'])

def main():
    print("Select the application to run:")
    print("1. Two-tiered application")
    print("2. Three-tiered application")
    choice = input("Enter the number of your choice: ")

    if choice == '1':
        run_two_tiered_application()
    elif choice == '2':
        run_three_tiered_application()
    else:
        print("Invalid choice. Please select either 1 or 2.")

if __name__ == "__main__":
    main()
