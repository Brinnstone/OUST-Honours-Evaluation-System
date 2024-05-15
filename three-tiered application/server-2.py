import socket
import json
import sqlite3

#-------------------------------------------
#Initialising the Database

def createTables(cursor):
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS studentInfo (
        RecordNo TEXT PRIMARY KEY,
        personID TEXT,
        firstName TEXT,
        lastName TEXT,
        emailAddress TEXT,
        mobileNumber TEXT,
        courseCode TEXT,
        unitAttempted INTEGER,
        unitCompleted INTEGER,
        courseStatus TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS courseInfo (
        RecordNo INTEGER PRIMARY KEY,
        courseCode TEXT,
        courseTitle TEXT,
        yearStartOffer INTEGER,
        yearEndOffer TEXT,
        courseCoordinatorName TEXT,
        courseCoordinatorEmailAddress TEXT,
        courseCoordinatorMobileNumber INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS studentUnitInfo (
        RecordNo TEXT PRIMARY KEY,
        personID TEXT,
        unitCode TEXT,
        unitTitle TEXT,
        resultScore REAL,
        resultGrade TEXT,
        FOREIGN KEY (personID) REFERENCES students(personID),
        FOREIGN KEY (unitCode) REFERENCES units(unitCode)
    )
    ''')

def loadJSONData(cursor, jsonFile, tableName):
    with open(jsonFile, 'r', encoding='utf-8') as file:
        data = json.load(file)
        keys = data[0].keys()
        questionMarks = ', '.join(['?'] * len(keys))
        query = f'INSERT OR IGNORE INTO {tableName} ({", ".join(keys)}) VALUES ({questionMarks})'
        for entry in data:
            cursor.execture(query, tuple(entry.values()))
#-------------------------------------------

def initialiseDatabase():
    connection = sqlite3.connect("OSCLR.db")
    cursor = connection.cursor()

    createTables(cursor)

    loadJSONData(cursor, 'StudentInfoTable.json', 'studentInfo')
    loadJSONData(cursor, 'CourseInfoTable.json', 'courseInfo')
    loadJSONData(cursor, 'StudentUnitInfo.json', 'studentUnitInfo')

    connection.commit()
    return connection, cursor


def handleServer1Continuously(conn, dbCursor):
    while True:  # Keep the connection open to handle multiple requests
        data = conn.recv(1024)
        if not data:
            print("\nNo data received, closing connection.")
            break
                
        request = json.loads(data.decode("utf-8"))
        print(f"Recieved request from server-1: {request}")

        # Process the request and query the database
        if request["requestType"] == "getStudentDetails":
            personID = request["personID"]
            dbCursor.execute('SELECT * FROM studentInfo WHERE personID = ?', (personID,))
            student_details = dbCursor.fetchone()
            response = json.dumps(student_details) if student_details else json.dumps({"error": "Student not found"})
        
        elif request["requestType"] == "getCourseInfo":
            courseCode = request["courseCode"]
            dbCursor.execute('SELECT * FROM courseInfo WHERE courseCode = ?', (courseCode,))
            course_info = dbCursor.fetchone()
            response = json.dumps(course_info) if course_info else json.dumps({"error": "Course not found"})
        
        elif request["requestType"] == "getStudentUnitInfo":
            personID = request["personID"]
            dbCursor.execute('SELECT * FROM studentUnitInfo WHERE personID = ?', (personID,))
            student_unit_info = dbCursor.fetchall()
            response = json.dumps(student_unit_info) if student_unit_info else json.dumps({"error": "Student unit info not found"})
        
        else:
            response = json.dumps({"error": "Unknown request type"})
        
        # Send the response back to server-1
        conn.sendall(response.encode("utf-8"))

dbConnection, dbCursor = initialiseDatabase()

HOST = ""
PORT = 25565

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Server-2 is listening...")

    while True:  # Main loop to accept connections
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        handleServer1Continuously(conn)  # Handle sever-1 in a separate function

        print("Ready for new connection...")

    dbConnection.close()