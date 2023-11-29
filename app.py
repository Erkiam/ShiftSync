from flask import Flask, render_template, request, redirect, url_for
import pyodbc
from datetime import datetime, timedelta

app = Flask(__name__)

server = 'tcp:shiftsyncdemo.database.windows.net,1433'
database = 'ShiftSync'
username = 'shiftsyncdemoadmin'
password = 'prU6dgo.eK67zZMc'
driver= '{ODBC Driver 18 for SQL Server}' 
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=Yes;TrustServerCertificate=no;Connection Timeout=30'
print(connection_string)
conn = pyodbc.connect(connection_string)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registration.html', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']

        insert_employee_into_db(first_name, last_name)

        return redirect(url_for('dashboard1'))

    return render_template('registration.html')


def insert_employee_into_db(first_name, last_name):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    query = "INSERT INTO dbo.Employee (FirstName, LastName) VALUES (?, ?)"
    cursor.execute(query, first_name, last_name)
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/card.html')
def card():
    return render_template('card.html')

@app.route('/current-calendar.html')
def current_calendar():
    return render_template('current-calendar.html')

@app.route('/post-availability.html')
def post_availability():
    return render_template('post-availability.html')

@app.route('/sign-in.html')
def sign_in():
    return render_template('sign-in.html')

@app.route('/sign-up.html')
def sign_up():
    return render_template('sign-up.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')


@app.route('/dashboard1.html')
def dashboard1():
    current_date = datetime.now().date()
    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    employee_dates = fetch_employee_dates(start_of_week, end_of_week)

    # Initialize dictionary with each day of the week
    dates = {start_of_week + timedelta(days=i): [] for i in range(7)}

    for ed in employee_dates:
        # Ensure the date is a datetime.date object
        date_key = ed['date']
        if isinstance(date_key, str):
            date_key = datetime.strptime(date_key, '%Y-%m-%d').date()

        # Check if the date is in the dates dictionary before appending
        if date_key in dates:
            dates[date_key].append(ed['name'])
        else:
            print(f"Date {date_key} not found in week range.")

    return render_template('dashboard1.html', dates=dates)



def fetch_employee_dates(start_of_week, end_of_week):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    query = """
    SELECT ec.Date, e.FirstName, e.LastName
    FROM dbo.EmployeeCalendar ec
    JOIN dbo.Employee e ON ec.EmployeeID = e.EmployeeID
    WHERE ec.Date BETWEEN ? AND ?;
    """
    cursor.execute(query, start_of_week, end_of_week)
    
    data = []
    for row in cursor:
        data.append({'date': row.Date, 'name': f"{row.FirstName} {row.LastName}"})

    cursor.close()
    conn.close()

    return data


@app.route('/date_selection', methods=['GET', 'POST'])
def date_selection():
    if request.method == 'POST':
        employee_id = request.form['employee']
        date = request.form['date']
        assign_date_to_employee(employee_id, date)
        return redirect(url_for('dashboard1'))

    employees = fetch_all_employees()
    return render_template('date_selection.html', employees=employees)

def assign_date_to_employee(employee_id, date):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    check_query = "SELECT COUNT(*) FROM dbo.EmployeeCalendar WHERE EmployeeID = ? AND Date = ?"
    cursor.execute(check_query, employee_id, date)
    if cursor.fetchone()[0] == 0:
        
        insert_query = "INSERT INTO dbo.EmployeeCalendar (EmployeeID, Date) VALUES (?, ?)"
        cursor.execute(insert_query, employee_id, date)
    else:
        pass

    conn.commit()
    cursor.close()
    conn.close()


def fetch_all_employees():
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    query = "SELECT EmployeeID, FirstName, LastName FROM dbo.Employee"
    cursor.execute(query)
    employees = [{'EmployeeID': row.EmployeeID, 'FirstName': row.FirstName, 'LastName': row.LastName} for row in cursor]
    
    cursor.close()
    conn.close()
    
    return employees



if __name__ == "__main__":
    app.run(debug=True)
 
