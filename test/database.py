# database.py
import psycopg2

def checkLogin(conn, username, password):
    """
    Call the stored function checkLogin to verify credentials.
    Username match is case-insensitive.
    Returns True if valid, else False.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT checkLogin(%s, %s);", (username, password))
        result = cur.fetchone()
        return bool(result[0]) if result else False

def getCarSalesSummary(conn):
    """
    Call the stored function getCarSalesSummary() to retrieve
    the summary of car sales, ordered by make and model ascending.
    Returns a list of rows (tuples).
    """
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM getCarSalesSummary();")
        return cur.fetchall()

def findCarSales(conn, salespersonID, keyword):
    """
    Call the stored function findCarSales for the given salesperson and keyword.
    Returns matching car sale records (or all if keyword empty), ordered by sale date.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM findCarSales(%s, %s);", (salespersonID, keyword))
        return cur.fetchall()

def addCarSale(conn, makeCode, modelCode, builtYear, odometer, price, isSold, buyerID, salespersonID, saleDate):
    """
    Calls addCarSale(...) to insert a new car sale with validation [oai_citation:8‡file-c41wthy61kgsrv7wcehwnp](file://file-C41wthy61kGsrV7wcEhwNP#:~:text=Can%20correctly%20add%20all%20valid,car%20sale).
    On success returns the new CarSaleID; on invalid data an exception is raised.
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT addCarSale(%s, %s, %s, %s, %s, %s, %s, %s, %s);",
            (makeCode, modelCode, builtYear, odometer, price, isSold, buyerID, salespersonID, saleDate)
        )
        new_id = cur.fetchone()[0]
    conn.commit()
    return new_id

def updateCarSale(conn, carSaleID, makeCode, modelCode, builtYear, odometer, price, isSold, buyerID, salespersonID, saleDate):
    """
    Calls updateCarSale(...) to update an existing sale with validation [oai_citation:9‡file-c41wthy61kgsrv7wcehwnp](file://file-C41wthy61kGsrV7wcEhwNP#:~:text=Update).
    On success returns the CarSaleID; on invalid data an exception is raised.
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT updateCarSale(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
            (carSaleID, makeCode, modelCode, builtYear, odometer, price, isSold, buyerID, salespersonID, saleDate)
        )
        updated_id = cur.fetchone()[0]
    conn.commit()
    return updated_id