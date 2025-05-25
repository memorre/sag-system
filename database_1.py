import psycopg2
from datetime import datetime

def openConnection():
    myHost = "awsprddbs4836.shared.sydney.edu.au"
    userid = "y25s1c9120_taye0567"
    passwd = "sHYKj7XW"
    conn = None
    try:
        conn = psycopg2.connect(database=userid, user=userid, password=passwd, host=myHost)
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
            mk.MakeCode,
            mk.MakeName,
            md.ModelCode,
            md.ModelName,
            -- 这里只查基础信息，统计信息用函数实现
            TO_CHAR(MAX(cs.SaleDate) FILTER (WHERE cs.IsSold=TRUE), 'DD-MM-YYYY') AS LastPurchasedAt
        FROM CarSales cs
        JOIN Make mk ON cs.MakeCode = mk.MakeCode
        JOIN Model md ON cs.ModelCode = md.ModelCode
        GROUP BY mk.MakeCode, mk.MakeName, md.ModelCode, md.ModelName
        ORDER BY mk.MakeName, md.ModelName;
    """)
    rows = cur.fetchall()
    result = []
    for row in rows:
        make_code, make_name, model_code, model_name, last_purchase = row
        # 调用SQL函数查询统计数据
        cur.execute("SELECT get_available_units(%s, %s)", (make_code, model_code))
        available = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM CarSales WHERE MakeCode=%s AND ModelCode=%s AND IsSold=TRUE", (make_code, model_code))
        sold = cur.fetchone()[0]
        cur.execute("SELECT get_total_sales(%s, %s)", (make_code, model_code))
        total_sales = cur.fetchone()[0]
        result.append({
            'make': make_name,
            'model': model_name,
            'availableUnits': available,
            'soldUnits': sold,
            'soldTotalPrices': f"{total_sales:.2f}" if total_sales != 0 else "0",
            'lastPurchaseAt': last_purchase or ''
        })
    cur.close()
    conn.close()
    return result

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
        # 检查make和model有效性
        curs.execute("SELECT COUNT(*) FROM Make WHERE UPPER(MakeName)=UPPER(%s)", (make,))
        if curs.fetchone()[0] == 0:
            print(f"❌ Make '{make}' not found.")
            return False
        curs.execute("SELECT COUNT(*) FROM Model WHERE LOWER(ModelName)=LOWER(%s)", (model,))
        if curs.fetchone()[0] == 0:
            print(f"❌ Model '{model}' not found.")
            return False
        # 获取MakeCode, ModelCode
        curs.execute("SELECT MakeCode FROM Make WHERE UPPER(MakeName)=UPPER(%s)", (make,))
        makecode = curs.fetchone()[0]
        curs.execute("SELECT ModelCode FROM Model WHERE LOWER(ModelName)=LOWER(%s)", (model,))
        modelcode = curs.fetchone()[0]
        insert_query = """
        INSERT INTO CarSales (MakeCode, ModelCode, BuiltYear, Odometer, Price, IsSold, BuyerID, SalespersonID, SaleDate)
        VALUES (%s, %s, %s, %s, %s, FALSE, %s, %s, %s)
        """
        curs.execute(insert_query, (makecode, modelcode, builtYear, odometer, price, None, None, None))
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
        try:
            date_obj = datetime.strptime(saledate, "%Y-%m-%d")
            saledate_str = date_obj.strftime("%d-%m-%Y")
        except ValueError:
            print("❌ Invalid date format. Expected 'YYYY-MM-DD'. Got:", saledate)
            return False
        # 调用函数校验customer
        cur.execute("SELECT is_valid_customer(%s)", (customer_id,))
        if not cur.fetchone()[0]:
            print(f"❌ Customer ID '{customer_id}' not found.")
            return False
        # 校验销售人员
        cur.execute("SELECT COUNT(*) FROM Salesperson WHERE LOWER(UserName) = LOWER(%s)", (salesperson_id,))
        if cur.fetchone()[0] == 0:
            print(f"❌ Salesperson username '{salesperson_id}' not found.")
            return False
        # 校验日期（不可是未来）
        cur.execute("SELECT TO_DATE(%s, 'DD-MM-YYYY') > CURRENT_DATE", (saledate_str,))
        is_future = cur.fetchone()
        if is_future and is_future[0]:
            print("❌ Sale date is in the future.")
            return False
        # 用存储过程登记售出
        cur.execute("SELECT record_car_sale(%s, %s, %s, TO_DATE(%s, 'DD-MM-YYYY'))", (carsaleid, customer_id, salesperson_id, saledate_str))
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