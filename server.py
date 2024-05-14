import socket
import json


# import StudentInfoTable
def readStudentInfoDetails():
    with open("StudentInfoTable.json", "r") as StudentInfoFile:
        studentDetails = json.load(StudentInfoFile)
     # DEBUG   print(studentDetails) 
    return studentDetails
# DEBUG readStudentInfoDetails()

# import CourseInfoTable
def readCourseInfoDetails():
    with open("CourseInfoTable.json", "r") as CourseInfoFile:
        CourseInfoDetails = json.load(CourseInfoFile)
      # DEBUG  print(CourseInfoDetails) 
    return CourseInfoDetails
# DEBUG readCourseInfoDetails()

# import StudentUnitTable
def readStudentUnitDetails():
    with open("StudentUnitInfo.json", "r") as StudentUnitFile:
        StudentUnitDetails = json.load(StudentUnitFile)
       # DEBUG print(StudentUnitDetails) # DEBUG
    return StudentUnitDetails
# DEBUG readStudentUnitDetails()




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


# Calculate amount of courses failed


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


def StudentRecord(readStudentUnitDetails, userData):
    if "personID" in userData:
        personID = userData["personID"]
        individualRecord = {}
        for records in readStudentUnitDetails():
            if records["personID"] == personID:
                individualRecord[records["unitCode"]] = records["resultScore"]

        print(f"Student Record: {individualRecord}")
        return individualRecord
    else:
        individualRecord = {}
        for key, value in userData.items():
            parts = value.split(",") # Separate the unitcodes and marks
            if len(parts) == 2:
                # Extract the key (part before the comma) and value (part after the comma)
                unitCode = parts[0].strip()
                mark = parts[1].strip() # Convert mark to float
                individualRecord[unitCode] = mark
            else:
                print(f"Invalid format for value: {value}")

        print(f"Student Record: {individualRecord}")
        return(individualRecord)


def StudentFailureRecord(readStudentUnitDetails, userData):
    if "personID" in userData:
        personID = userData["personID"]
        individualRecord = {}
        for records in readStudentUnitDetails():
            if records["personID"] == personID and records["resultGrade"] == "F":
                unitCode = records["unitCode"]
                if unitCode in individualRecord:
                    # Increment the count of times this unit has been failed
                    individualRecord[unitCode] += 1
                else:
                    # Initialize the count for this unit
                    individualRecord[unitCode] = 1

        print(f"Student unit failures: {individualRecord}")
        return individualRecord
    

    # POSSIBLE FIX FOR THIS - RATHER THAN SENDING UNITCODES and MARKS AS A KEY/VALUE PAIR - SEND THEM BOTH UNDER VALUES THEN SEPERATE THEM VIA THE ","  

    else: # Handles unitData input
        individualRecord = {}

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


def authenticateClient(userDataToSend):
    # Load data from JSON file
    with open("StudentInfoTable.json", "r", encoding="utf-8") as StudentInfoFile:
        studentDetails = json.load(StudentInfoFile)
         
    
    for record in studentDetails:

        # Check if all provided details match the corresponding record
        if all(record[key] == userDataToSend[key] for key in userDataToSend.keys()):
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
                response = authenticateClient(userData)

            elif userData.get("requestType") == "Eval":
                userData.pop("requestType", None)
                unitScoreList = StudentRecord(readStudentUnitDetails, userData)
                unitFailed = StudentFailureRecord(readStudentUnitDetails, userData)
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

                unitScoreList = StudentRecord(readStudentUnitDetails, unitData)
                unitFailed = StudentFailureRecord(readStudentUnitDetails, unitData)
                response = honorEligibility(unitScoreList, unitFailed, personID)
                
        # Send the response back to the client
        conn.sendall(response.encode("utf-8"))

HOST = ""
PORT = 25565

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Server is listening...")

    while True:  # Main loop to accept connections
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        handleClientContinuously(conn)  # Handle the client in a separate function

        print("Ready for new connection...")