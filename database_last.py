import psycopg2
from datetime import datetime

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
    conn = openConnection()
    cur = conn.cursor()


    cur.execute("""
        SELECT UserName, FirstName, LastName
        FROM Salesperson
        WHERE LOWER(UserName)=LOWER(%s) AND Password=%s
    """, (login, password))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return list(row) if row else None




def getCarSalesSummary():
    conn = openConnection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            mk.MakeName,
            md.ModelName,
            COUNT(*) FILTER (WHERE cs.IsSold=FALSE) AS AvailableUnits,
            COUNT(*) FILTER (WHERE cs.IsSold=TRUE)  AS SoldUnits,
            ROUND(COALESCE(SUM(cs.Price) FILTER (WHERE cs.IsSold=TRUE), 0), 2) AS TotalSales,
            TO_CHAR(MAX(cs.SaleDate) FILTER (WHERE cs.IsSold=TRUE), 'DD-MM-YYYY') AS LastPurchasedAt
        FROM CarSales cs
        JOIN Make mk ON cs.MakeCode = mk.MakeCode
        JOIN Model md ON cs.ModelCode = md.ModelCode
        GROUP BY mk.MakeName, md.ModelName
        ORDER BY mk.MakeName, md.ModelName;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            'make': row[0],
            'model': row[1],
            'availableUnits': row[2],
            'soldUnits': row[3],
            'soldTotalPrices': f"{row[4]:.2f}" if row[4] != 0 else "0",
            'lastPurchaseAt': row[5] or ''
        }
        for row in rows
    ]


def findCarSales(searchString):
    pat = f"%{searchString.lower()}%"
    conn = openConnection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            cs.CarSaleID,
            mk.MakeName,
            md.ModelName,
            cs.BuiltYear,
            cs.Odometer,
            ROUND(cs.Price, 2),
            cs.IsSold,
            TO_CHAR(cs.SaleDate,'DD-MM-YYYY'),
            COALESCE(cu.FirstName || ' ' || cu.LastName, ''),
            COALESCE(sp.FirstName || ' ' || sp.LastName, '')
        FROM CarSales cs
        JOIN Make mk ON cs.MakeCode = mk.MakeCode
        JOIN Model md ON cs.ModelCode = md.ModelCode
        LEFT JOIN Customer cu ON cs.BuyerID = cu.CustomerID
        LEFT JOIN Salesperson sp ON cs.SalespersonID = sp.UserName
        WHERE (
            LOWER(mk.MakeName) LIKE %s OR
            LOWER(md.ModelName) LIKE %s OR
            LOWER(cu.FirstName || ' ' || cu.LastName) LIKE %s OR
            LOWER(sp.FirstName || ' ' || sp.LastName) LIKE %s
        )
        AND (
            cs.IsSold = FALSE OR 
            (cs.IsSold = TRUE AND cs.SaleDate >= CURRENT_DATE - INTERVAL '3 years')
        )
        ORDER BY cs.IsSold, cs.SaleDate, mk.MakeName, md.ModelName;
    """, (pat, pat, pat, pat))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for row in rows:
        result.append({
            'carsale_id': row[0],
            'make': row[1],
            'model': row[2],
            'builtYear': row[3],
            'odometer': row[4],
            'price': f"{row[5]:.2f}",
            'isSold': row[6],
            'sale_date': row[7] or '',
            'buyer': row[8],
            'salesperson': row[9]
        })

    return result


def addCarSale(make, model, builtYear, odometer, price):
    conn = openConnection()
    if conn is None:
        print("Failed to connect to the database.")
        return False

    curs = None
    try:
        odometer = int(odometer)
        price = float(price)

        if odometer <= 0:
            print("❌ Invalid odometer value:", odometer)
            return False
        if price <= 0:
            print("❌ Invalid price value:", price)
            return False

        curs = conn.cursor()
        insert_query = """
            INSERT INTO CarSales (MakeCode, ModelCode, BuiltYear, Odometer, Price, IsSold, BuyerID, SalespersonID, SaleDate)
            VALUES (%s, %s, %s, %s, %s, FALSE, %s, %s, %s)
        """
        curs.execute(insert_query, (
            str(make).upper(),
            str(model).lower(),
            builtYear,
            odometer,
            price,
            None,
            None,
            None
        ))
        conn.commit()
        print("✅ Car sale record added successfully.")
        return True

    except psycopg2.Error as sqle:
        print("psycopg2.Error:", sqle)
        return False

    except ValueError:
        print("❌ Conversion error: odometer or price is not a valid number.")
        return False

    finally:
        if curs:
            curs.close()
        if conn:
            conn.close()


def updateCarSale(carsaleid, customer_id, salesperson_id, saledate):
    print("🟢 updateCarSale() called")
    conn = openConnection()
    cur = conn.cursor()
    try:
        print("DEBUG - Input Parameters:")
        print("  CarSaleID:", carsaleid)
        print("  CustomerID:", customer_id)
        print("  SalespersonID:", salesperson_id)
        print("  Sale Date (input):", saledate)

        try:
            date_obj = datetime.strptime(saledate, "%Y-%m-%d")
            saledate = date_obj.strftime("%d-%m-%Y")
            print("✅ Reformatted Sale Date (DD-MM-YYYY):", saledate)
        except ValueError:
            print("❌ Invalid date format. Expected 'YYYY-MM-DD'. Got:", saledate)
            return False

        cur.execute("""
            SELECT COUNT(*) FROM Customer
            WHERE LOWER(CustomerID) = LOWER(%s)
        """, (customer_id,))
        if cur.fetchone()[0] == 0:
            print(f"❌ Customer ID '{customer_id}' not found.")
            return False
        print("✅ Customer ID is valid.")

        cur.execute("""
            SELECT COUNT(*) FROM Salesperson
            WHERE LOWER(UserName) = LOWER(%s)
        """, (salesperson_id,))
        if cur.fetchone()[0] == 0:
            print(f"❌ Salesperson username '{salesperson_id}' not found.")
            return False
        print("✅ Salesperson username is valid.")

        cur.execute("SELECT TO_DATE(%s, 'DD-MM-YYYY') > CURRENT_DATE", (saledate,))
        is_future = cur.fetchone()
        if is_future and is_future[0]:
            print("❌ Sale date is in the future.")
            return False
        print("✅ Sale date is valid.")

        cur.execute("""
            UPDATE CarSales
            SET BuyerID = %s,
                SalespersonID = %s,
                SaleDate = TO_DATE(%s, 'DD-MM-YYYY'),
                IsSold = TRUE
            WHERE CarSaleID = %s
        """, (customer_id, salesperson_id, saledate, carsaleid))

        print("DEBUG - cur.rowcount after update:", cur.rowcount)

        if cur.rowcount == 0:
            print("⚠️ No changes made: ID not found or data unchanged.")
            conn.commit()
            return True

        conn.commit()
        print("✅ Update committed.")
        return True

    except Exception as e:
        conn.rollback()
        print("‼️ ERROR in updateCarSale:", str(e))
        return False

    finally:
        cur.close()
        conn.close()
        print("🔚 Database connection closed.")