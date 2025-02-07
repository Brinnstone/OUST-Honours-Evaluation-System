import socket
import json
import sqlite3

#-------------------------------------------
# Initialising the Database
# This function creates the tables / structure that are used in the database
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

# This function loads the data from the json files into the database
def loadJSONData(cursor, jsonFile, tableName):
    with open(jsonFile, 'r', encoding='utf-8') as file:
        data = json.load(file)
        keys = data[0].keys()
        questionMarks = ', '.join(['?'] * len(keys))
        query = f'INSERT OR IGNORE INTO {tableName} ({", ".join(keys)}) VALUES ({questionMarks})'
        for entry in data:
            cursor.execute(query, tuple(entry.values()))
#-------------------------------------------

# This function in initialise the database by creating the tables and inputting the data from the JSON files into the database.
def initialiseDatabase():
    connection = sqlite3.connect("OSCLR.db")
    cursor = connection.cursor()

    createTables(cursor)

    loadJSONData(cursor, 'StudentInfoTable.json', 'studentInfo')
    loadJSONData(cursor, 'CourseInfoTable.json', 'courseInfo')
    loadJSONData(cursor, 'StudentUnitInfo.json', 'studentUnitInfo')

    connection.commit()
    return connection, cursor

# This function handles the connection between the server-1 and itself (server-2)
def handleServer1Request(conn, dbCursor):
    try:
        while True:  # Keep the connection open to handle multiple requests
            data = conn.recv(1024)
            if not data:
                print("\nNo data received, closing connection.")
                break

            request = json.loads(data.decode("utf-8"))
            print(f"Received request from server-1: {request}")

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
                response = json.dumps([{"error": "Unknown request type"}])

            conn.sendall(response.encode("utf-8"))
            print(response)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

dbConnection, dbCursor = initialiseDatabase()

HOST = "127.0.0.1"
PORT = 25566

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Server-2 is listening...")

    while True:
        try:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            handleServer1Request(conn, dbCursor)  # Handle server-1 in a separate function
        except Exception as e:
            print(f"An error occurred while accepting a connection: {e}")

        print("Ready for new connection...")

    dbConnection.close()