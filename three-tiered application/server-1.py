import socket
import json

#Communicate with Server-2
def sendToServer2(request):
    HOST = "127.0.0.1"
    PORT = 25566

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps(request).encode("utf-8"))
        data = s.recv(10240) #Accepts upto 10kb of data
        response = json.loads(data.decode("utf-8"))

    return response

# Calculate averages
def calculateCourseAverage(marks, unitCode):
    totalMarks = 0
    for mark in marks:
        # Convert each mark from string to float
        convertMarks = float(mark)
        totalMarks += convertMarks


    unitAmount = len(unitCode)
    courseAverage = totalMarks / unitAmount
    return round(courseAverage, 2)

# Average of best 8 scores 
def calculateBest8Average(unitScoreList):
    best8Average = sorted(unitScoreList.items(), key=lambda x: x[1], reverse=True)[:8]

    best8AverageDict = dict(best8Average)
    return best8AverageDict

# evaluate eligibility
# Recieve a list of unit code, score
def honorEligibility(unitScoreList, unitFailed, personID):
    courseAverage = calculateCourseAverage(unitScoreList.values(), unitScoreList.keys())
    best8Average = calculateBest8Average(unitScoreList)

    if len(unitScoreList) <= 15: # Checks if the student completed 15 or less units
        return f"{personID} : {courseAverage}, completed less than 16 units!\nDoes not qualify for honors study!"
    
    elif sum(unitFailed.values()) >= 6: # Checks if there are 6 or more “Fail” results,
        return f"{personID} : {courseAverage}, with 6 or more Fails!\nDoes not qualify for honors study!"
    
    elif courseAverage >= 70: # Checks if the course average is greater than or equal to 70
        return f"{personID} : {courseAverage}, qualifies for honors study!"
    
    elif 65 <= courseAverage < 70 & best8Average >= 80: # Checks if the course average is less than 70 and greater than or equal to 65, but the average of the best 8 scores is greater than or equal to 80
        return f"{personID} : {courseAverage} : {best8Average}, qualifies for honors study!"
    
    elif 65 <= courseAverage < 70 & best8Average > 80: # Checks if the course average is less than 70 and greater than or equal to 65, and the average of the best 8 scores is less than 80
        return f"{personID} : {courseAverage} : {best8Average}, May have a good chance! Needs further assessment!"
    
    elif 60 <= courseAverage < 65 & best8Average >= 80: # Checks if the course average is less than 65 and greater than or equal to 60, but the average of best 8 scores is 80 or higher
        return f"{personID} : {courseAverage} : {best8Average}, May have a good chance! Must be carefully reassessed and get the coordinator's permission!"
    
    else:
        return f"{personID} : {courseAverage}, Does not qualify for honors study!"


def StudentRecord(userData):
    
    individualRecord = {}

    if isinstance(userData, dict):
        for key, value in userData.items():
            parts = value.split(",")  # Separate the unit codes and marks
            if len(parts) == 2:
                unitCode = parts[0].strip()
                mark = parts[1].strip()
                individualRecord[unitCode] = mark
            else:
                print(f"Invalid format for value: {value}")

    elif isinstance(userData, list):
        for record in userData:
            if len(record) >= 5:
                unitCode = record[2].strip()  # Unit code is the 3rd element
                mark = str(record[4]).strip()  # Result score is the 5th element
                individualRecord[unitCode] = mark
            else:
                print(f"Invalid format for record: {record}")

    print(f"Student Record: {individualRecord}")
    return individualRecord


def StudentFailureRecord(userData):
    individualRecord = {}

    if isinstance(userData, dict):
            for key, value in userData.items():
                parts = value.split(",") # Separate the unitcodes and marks
                if len(parts) == 2:
                    unitCode = parts[0].strip()
                    mark = float(parts[1].strip())
                    if mark < 50.0:
                        if unitCode in individualRecord:
                            # Increment the count of times this unit has been failed
                            individualRecord[unitCode] += 1
                        else:
                            # Initialize the count for this unit
                            individualRecord[unitCode] = 1
                else:
                    print(f"Invalid format for value: {value}")

            print(f"Student unit failures: {individualRecord}")
            return individualRecord
    elif isinstance(userData, list):
        # Handle userData as a list of lists
        for record in userData:
            if len(record) >= 5:
                unitCode = record[2].strip()  # Unit code is the 3rd element
                mark = float(record[4])  # Result score is the 5th element
                if mark < 50.0:
                    if unitCode in individualRecord:
                        # Increment the count of times this unit has been failed
                        individualRecord[unitCode] += 1
                    else:
                        # Initialize the count for this unit
                        individualRecord[unitCode] = 1
            else:
                print(f"Invalid format for record: {record}")

    print(f"Student unit failures: {individualRecord}")
    return individualRecord


def authenticateClient(userData, comparisonData):
    # Check if userData is a dictionary and contains the 'error' key
    if isinstance(userData, dict):
        if userData.get('error') == "Student not found":
            print("Authentication failed.")
            return "Authentication failed."
    
    elif isinstance(userData, list):
        # Define the keys for the user data dictionary
        user_keys = ["personID", "firstName", "lastName", "emailAddress", "mobileNumber", "courseCode", "unitAttempted", "unitCompleted", "courseStatus"]
        
        # Remove the first element (record number) and convert the list to a dictionary
        print("Original userData:", userData)
        userData = dict(zip(user_keys, userData[1:]))
        
        # Remove unnecessary keys from userData
        keys_to_remove = ["courseCode", "unitAttempted", "unitCompleted", "courseStatus"]
        for key in keys_to_remove:
            userData.pop(key, None)
        
        # Remove the requestType from comparisonData
        comparisonData.pop("requestType", None)
        
        print("Processed userData:", userData)
        print("Processed comparisonData:", comparisonData)
        
        if not isinstance(comparisonData, dict):
            print("Authentication failed. Invalid data format.")
            return "Authentication failed."

        if all(userData.get(key) == comparisonData.get(key) for key in userData.keys()):
            print("Authentication successful.")
            return "Authentication successful."
    
    print("Authentication failed.")
    return "Authentication failed."



def handleClientContinuously(conn):
    while True:  # Keep the connection open to handle multiple requests
        data = conn.recv(1024)
        if not data:
            print("\nNo data received, closing connection.")
            break
        
        # Seperates auth + eval from unit data  
        tempData = json.loads(data.decode("utf-8"))
        if tempData["requestType"] != "UnAuthUnitScore":
            userData = tempData
            print("Received data from client:", userData)

            if userData.get("requestType") == "Exit":
                print("Exit command received, closing connection.")
                break

            elif userData.get("requestType") == "Auth":
                userData.pop("requestType", None)
                userData["requestType"] = "getStudentDetails" #Changing the request type to be handled within Server-2
                retrievedData = sendToServer2(userData)
                print(retrievedData)
                response = authenticateClient(retrievedData, userData)

            elif userData.get("requestType") == "Eval":
                userData.pop("requestType", None)
                userData["requestType"] = "getStudentUnitInfo" #Changing the request type to be handled within Server-2
                retrievedData = sendToServer2(userData)
                unitScoreList = StudentRecord(retrievedData)
                unitFailed = StudentFailureRecord(retrievedData)
                personID = userData["personID"]
                response = honorEligibility(unitScoreList, unitFailed, personID)
            else:
                response = "Unknown request"

        else:
            unitData = tempData
            # Receives unitCode + unitResult + mark of an unregistered user
            if unitData.get("requestType") == "UnAuthUnitScore":
                unitData.pop("requestType", None)
                personID = unitData["personID"]
                unitData.pop("personID", None)

                unitScoreList = StudentRecord(unitData)
                unitFailed = StudentFailureRecord(unitData)
                response = honorEligibility(unitScoreList, unitFailed, personID)
                
        # Send the response back to the client
        conn.sendall(response.encode("utf-8"))

import threading
import time

# Constants
BROADCAST_IP = '255.255.255.255'
BROADCAST_PORT = 25565
SERVER_PORT = 25565

# Function to broadcast the server's IP address
def broadcast_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            message = json.dumps({"host": socket.gethostbyname(socket.gethostname()), "port": SERVER_PORT})
            s.sendto(message.encode('utf-8'), (BROADCAST_IP, BROADCAST_PORT))
            time.sleep(2)  # Broadcast every 2 seconds

# Start broadcasting in a separate thread
threading.Thread(target=broadcast_ip, daemon=True).start()



HOST = ""
PORT = 25565

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Server-1 is listening...")

    while True:  # Main loop to accept connections
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        handleClientContinuously(conn)  # Handle the client in a separate function

        print("Ready for new connection...")