from fastapi import FastAPI
from pydantic import BaseModel
from database import get_db_connection

app = FastAPI()


class ExpenseCreate(BaseModel):
    title: str
    amount: float


@app.get("/")
def home():
    return {"message": "Expense Management API is running"}


@app.get("/expenses")
def get_expenses():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()

    cursor.close()
    connection.close()

    return expenses

@app.get("/expenses/total")
def get_total():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    total = result[0] if result[0] is not None else 0

    return {"total": total}


@app.post("/expenses")
def create_expense(expense: ExpenseCreate):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = "INSERT INTO expenses (title, amount) VALUES (%s, %s)"
    values = (expense.title, expense.amount)

    cursor.execute(query, values)
    connection.commit()

    expense_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return {
        "id": expense_id,
        "title": expense.title,
        "amount": expense.amount
    }

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = %s",
        (expense_id,)
    )

    connection.commit()

    deleted = cursor.rowcount

    cursor.close()
    connection.close()

    if deleted == 0:
        return {"message": "Expense not found"}

    return {"message": "Expense deleted successfully"}

@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, expense: ExpenseCreate):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE expenses
        SET title = %s, amount = %s
        WHERE id = %s
    """

    values = (expense.title, expense.amount, expense_id)

    cursor.execute(query, values)
    connection.commit()

    updated = cursor.rowcount

    cursor.close()
    connection.close()

    if updated == 0:
        return {"message": "Expense not found"}

    return {
        "id": expense_id,
        "title": expense.title,
        "amount": expense.amount
    }