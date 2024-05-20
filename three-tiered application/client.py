import socket
import json

HOST = "" #Connect to server if it's on same network
PORT = 25565 #Need to input a server's port address
BROADCAST_PORT = 37020  # Port to broadcast for server discovery


#---------------------------------------------------------
#Functions

# Function to discover server IP
def discover_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.bind(("", BROADCAST_PORT))
        while True:
            data, addr = s.recvfrom(1024)
            try:
                message = json.loads(data.decode('utf-8'))
                if "host" in message and "port" in message:
                    return message["host"], message["port"]
            except json.JSONDecodeError:
                continue

# Discover server
HOST, PORT = discover_server()

def collectUnauthenticatedUserDetails(unitScores):
    print("\nEnter unit code and mark pairs (e.g., CSI3344, 82.4). Type 'done' when finished:")
    index = 1

    while True:
        entry = input("Enter unit code and mark: ").strip()
        if entry.upper() == 'DONE':
            if 16 <= len(unitScores) <= 30:
                break
            else:
                print(f"You have entered {len(unitScores)} unit scores. Please enter between 16 and 30 total.")
                continue

        try:
            unitCode, mark = entry.split(',')
            unitCode = unitCode.strip()
            mark = float(mark.strip())  # Clean up any spaces before converting
            if len(unitCode) <= 7 and 0.0 <= mark <= 100.0:
                # Check attempts and grades
                unit_attempts = [value.split(',')[0] for value in unitScores.values()]
                unit_fails = [value for value in unitScores.values() if value.split(',')[0] == unitCode and float(value.split(',')[1]) < 50.0]
                unit_passes = [value for value in unitScores.values() if value.split(',')[0] == unitCode and 50.0 <= float(value.split(',')[1]) < 60.0]
                unit_high_passes = [value for value in unitScores.values() if value.split(',')[0] == unitCode and float(value.split(',')[1]) >= 60.0]

                if unit_attempts.count(unitCode) >= 3:
                    print(f"You have already attempted unit {unitCode} three times. Cannot add another attempt.")
                    continue
                if len(unit_fails) > 2:
                    print(f"The unit {unitCode} has reached the maximum number of Fail grades. Cannot add another Fail attempt.")
                    continue
                if len(unit_passes) >= 1 and mark < 60.0:
                    print(f"The unit {unitCode} has reached the maximum number of Pass grades. Cannot add another Pass attempt.")
                    continue
                if len(unit_high_passes) >= 1 and mark >= 60.0:
                    print(f"The unit {unitCode} has already been passed with a higher grade. Cannot add another Pass attempt.")
                    continue
                
                unitScores[index] = f"{unitCode}, {mark}"  # Store index and combined string in the dictionary
                index += 1
            else:
                print("Invalid entry. Ensure the unit code is up to 7 characters and mark is between 0.0 and 100.0.")
        except ValueError:
            print("Invalid format. Please enter in the format: <unitCode>, <mark>")

    return unitScores

#---------------------------------------------------------
#Main Code Body
print("Welcome to the client application for the OUST Honors Enrolment Pre-assessment System")

#Collect the user's enrollment
print("\nAre you a former or current OUST student? (F / C / None): ")
enrollmentType = input("").strip().upper()

while enrollmentType not in ('F', 'C', 'NONE'): #Check for invalid input
    print(f"\n'{enrollmentType}' is not a valid option. Please select a valid input (F / C / None): ")
    enrollmentType = input("").strip().upper()

if enrollmentType not in ('F', 'NONE'):
    #If the user is a student, use this:
    print("Please enter your Student ID (8-digit number)")
else:
    #If the user is not a student, use this:
    print("Please enter your Person ID (8-digit number)")

while True:
    personID = input("").strip()
    if personID.isdigit() and len(personID) == 8:
        break
    else:
        print("Ensure that your ID is an 8-digit number.")


#Grab details for authentication 
print("\nPlease input your first name: ")
firstName = input("").strip().capitalize()

print("\nPlease input your last name: ")
lastName = input("").upper()

print("\nPlease input your OUST email address: ")
while True:
    emailAddress = input("").strip()
    if emailAddress.endswith("@our.oust.edu.au"):
        break
    else:
        print("Invalid email address. Must be an OUST email address.")


print("\nPlease input your mobile number: ")
while True:
    mobileNumber = input("").strip()
    if mobileNumber.isdigit() and len(mobileNumber) == 10:
        break
    else:
        print("Mobile Number must be a 10-digit number.")

#Format the data into a JSON Dictionary
userDataToAuthenticate = {
    'requestType': 'Auth',
    "personID": personID,
    "firstName": firstName,
    "lastName": lastName,
    "emailAddress": emailAddress,
    "mobileNumber": mobileNumber
}

authJsonData = json.dumps(userDataToAuthenticate).encode('utf-8')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(authJsonData)
    serverResponse = s.recv(1024)

#Recieve authentication back from the server
if serverResponse.decode('utf-8') == "Authentication successful.":
    print(f"\n{firstName} {lastName} (PersonID: {personID}) is AUTHENTICATED.")

    userDataToEvaluate = {
    'requestType': 'Eval',
    "personID": personID,
    "firstName": firstName,
    "lastName": lastName,
    "emailAddress": emailAddress,
    "mobileNumber": mobileNumber
    }

    evalJsonData = json.dumps(userDataToEvaluate).encode('utf-8')

    #Pass all non student data to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(evalJsonData)
        #Recieve assessment results from server
        ResultResponse = s.recv(1024)
        print(ResultResponse.decode('utf-8'))

else:
    print(f"'\n{firstName} {lastName}' (PersonID: {personID}) is NOT AUTHENTICATED.")
    #If user is NOT a student, collect person ID and a series of unit scores in <unit_code, mark> pair. Number of scores should be between 16 - 30 including Fail (score < 50) and duplicate unit marks if the student did the same unit multiple times.
    #Unit code can be a string up to 7-characters. Mark is a float between 0.0 and 100.0 inclusive.
    unitScores = {
        'requestType': 'UnAuthUnitScore', #add request ("UnAuthUnitScores")
        'personID': personID
    }
    unitScores = collectUnauthenticatedUserDetails(unitScores) 
    
    unitScoresJsonData = json.dumps(unitScores).encode('utf-8')

    #Pass all non student data to the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(unitScoresJsonData)

        #Recieve assessment results from server
        ResultResponse = s.recv(1024)
        print(f"\n{ResultResponse.decode('utf-8')}")

input('\nEnter to exit...')