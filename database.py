import psycopg2


def openConnection():
    myHost = "awsprddbs4836.shared.sydney.edu.au"
    userid = "y25s1c9120_taye0567"
    passwd = "sHYKj7XW"

    conn = None
    try:
        conn = psycopg2.connect(
            database=userid,
            user=userid,
            password=passwd,
            host=myHost
        )
    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)
    return conn



def checkLogin(login, password):
    connection = openConnection()
    if connection is None:
        return None

    try:
        with connection.cursor() as cursor:
            # Use callproc to call loginUser function
            cursor.callproc('loginUser', (login, password))

            # get the result of first line
            row = cursor.fetchone()
            return list(row) if row else None

    except psycopg2.Error as sqle:
        print("psycopg2.Error: " + str(sqle.pgerror))
        return None

    finally:
        connection.close()


def getCarSalesSummary():
    connection = openConnection()
    if connection is None:
        return None

    try:
        with connection.cursor() as cursor:
            # use callproc calls a SQL function with no parameters
            cursor.callproc('getCarSalesSummary')

            # get result set
            results = cursor.fetchall()

            # The field names correspond to the order of columns returned in the database function
            attributes = ["make", "model", "availableUnits", "soldUnits", "soldTotalPrices", "lastPurchaseAt"]

            # Initially construct a dictionary list
            set_dict = [dict(zip(attributes, row)) for row in results]

            # Secondary processing field format: Amounts are rounded to two decimal places, and empty dates are replaced with empty strings
            for row in set_dict:
                row["soldTotalPrices"] = f"{row['soldTotalPrices']:.2f}" if row["soldTotalPrices"] != 0 else "0"
                row["lastPurchaseAt"] = row["lastPurchaseAt"] or ""

            print(set_dict)
            return set_dict

    except psycopg2.Error as sqle:
        print("psycopg2.Error: " + str(sqle.pgerror))
        return None

    finally:
        connection.close()

def findCarSales(searchString):
    connection = openConnection()
    if connection is None:
        return None

    try:
        with connection.cursor() as cursor:
            # 调用 SQL 函数 findCarSales
            cursor.callproc('findCarSales', (searchString,))
            results = cursor.fetchall()

            # 字段名与 SQL 函数的返回顺序对应
            attributes = [
                'carsale_id', 'make', 'model', 'builtYear', 'odometer',
                'price', 'isSold', 'sale_date', 'buyer', 'salesperson'
            ]

            # 构建字典列表
            set_dict = [dict(zip(attributes, row)) for row in results]

            # 格式化价格和日期
            for row in set_dict:
                row["price"] = f"{row['price']:.2f}"
                row["sale_date"] = row["sale_date"] or ""

            print(set_dict)  # 可注释掉
            return set_dict

    except psycopg2.Error as sqle:
        print("psycopg2.Error: " + str(sqle.pgerror))
        return None

    finally:
        connection.close()

def addCarSale(make, model, builtYear, odometer, price):
    conn = openConnection()
    if conn is None:
        print("Failed to connect to the database.")
        return False

    curs = None
    try:
        odometer = int(odometer)
        price = float(price)
        ###check>0
        if odometer <= 0:
            print("Invalid odometer value:", odometer)
            return False
        if price <= 0:
            print("Invalid price value:", price)
            return False

        curs = conn.cursor()

        # 使用 callproc 调用 SQL 函数
        curs.callproc('addCarSale', (
            str(make).upper(),
            str(model).lower(),
            builtYear,
            odometer,
            price
        ))

        result = curs.fetchone()
        conn.commit()

        if result and result[0] is True:
            print("Car sale record added successfully.")
            return True
        else:
            print("Failed to insert car sale record (SQL function returned FALSE).")
            return False

    except psycopg2.Error as sqle:
        print("psycopg2.Error:", sqle)
        return False

    except ValueError:
        print("Conversion error: odometer or price is not a valid number.")
        return False

    finally:
        if curs:
            curs.close()
        if conn:
            conn.close()



def ymd_to_dmy(date_str):
    # date_str: 'YYYY-MM-DD'
    if date_str and len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        parts = date_str.split('-')
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
    return date_str  # If the format is incorrect, return the original string directly.



def updateCarSale(carsaleid, customer_id, salesperson_id, saledate):
    # Make sure the date is in the format 'DD-MM-YYYY'.
    saledate_dmy = ymd_to_dmy(saledate)
    print("DEBUG: updateCarSale called with:", carsaleid, customer_id, salesperson_id, saledate_dmy)
    conn = openConnection()
    if conn is None:
        print("Failed to connect to the database.")
        return False
    cur = conn.cursor()
    try:
        cur.callproc('updateCarSale', (carsaleid, customer_id, salesperson_id, saledate_dmy))
        conn.commit()
        result = cur.fetchone()
        print("DEBUG: SQL function result:", result)
        return bool(result[0]) if result else False
    except Exception as e:
        print("Exception:", e)
        return False
    finally:
        cur.close()
        conn.close()