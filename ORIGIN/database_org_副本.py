#!/usr/bin/env python3
import psycopg2

#####################################################
##  Database Connection
#####################################################

'''
Connect to the database using the connection string
'''
def openConnection():
    # connection parameters - ENTER YOUR LOGIN AND PASSWORD HERE

    myHost = "awsprddbs4836.shared.sydney.edu.au"
    userid = "y25s1c9120_taye0567"
    passwd = "sHYKj7XW"
    
    # Create a connection to the database
    conn = None
    try:
        # Parses the config file and connects using the connect string
        conn = psycopg2.connect(database=userid,
                                    user=userid,
                                    password=passwd,
                                    host=myHost)

    except psycopg2.Error as sqle:
        print("psycopg2.Error : " + sqle.pgerror)
    
    # return the connection to use
    return conn

'''
Validate salesperson based on username and password
'''
def checkLogin(login, password):

    return ['jdoe', 'John', 'Doe']


"""
    Retrieves the summary of car sales.

    This method fetches the summary of car sales from the database and returns it 
    as a collection of summary objects. Each summary contains key information 
    about a particular car sale.

    :return: A list of car sale summaries.
"""
def getCarSalesSummary():
    return

"""
    Finds car sales based on the provided search string.

    This method searches the database for car sales that match the provided search 
    string. See assignment description for search specification

    :param search_string: The search string to use for finding car sales in the database.
    :return: A list of car sales matching the search string.
"""
def findCarSales(searchString):
    return

"""
    Adds a new car sale to the database.

    This method accepts a CarSale object, which contains all the necessary details 
    for a new car sale. It inserts the data into the database and returns a confirmation 
    of the operation.

    :param car_sale: The CarSale object to be added to the database.
    :return: A boolean indicating if the operation was successful or not.
"""
def addCarSale(make, model, builtYear, odometer, price):
    return

"""
    Updates an existing car sale in the database.

    This method updates the details of a specific car sale in the database, ensuring
    that all fields of the CarSale object are modified correctly. It assumes that 
    the car sale to be updated already exists.

    :param car_sale: The CarSale object containing updated details for the car sale.
    :return: A boolean indicating whether the update was successful or not.
"""
def updateCarSale(carsaleid, customer, salesperson, saledate):
    # 建立数据库连接
    conn = psycopg2.connect(
        database="y25s1c9120_pyan0746",
        user="y25s1c9120_pyan0746",
        password="x3MNc5aE",
        host="awsprddbs4836.shared.sydney.edu.au"
    )
    cur = conn.cursor()

    try:
        # 1. 验证 SaleDate 不是将来的时间
        cur.execute("SELECT TO_DATE(%s, 'DD-MM-YYYY') > CURRENT_DATE;", (saledate,))
        is_future = cur.fetchone()[0]
        if is_future:
            print("❌ 错误：不能使用未来的销售日期")
            conn.close()
            return False

        # 2. 验证 customer 是否存在
        cur.execute("SELECT COUNT(*) FROM Customer WHERE LOWER(CustomerID) = LOWER(%s);", (customer,))
        if cur.fetchone()[0] == 0:
            print("❌ 错误：买家不存在")
            conn.close()
            return False

        # 3. 验证 salesperson 是否存在
        cur.execute("SELECT COUNT(*) FROM Salesperson WHERE LOWER(UserName) = LOWER(%s);", (salesperson,))
        if cur.fetchone()[0] == 0:
            print("❌ 错误：销售员不存在")
            conn.close()
            return False

        # 4. 执行更新（将车标记为售出）
        cur.execute("""
            UPDATE CarSales
            SET BuyerID = %s,
                SalespersonID = %s,
                SaleDate = TO_DATE(%s, 'DD-MM-YYYY'),
                IsSold = TRUE
            WHERE CarSaleID = %s;
        """, (customer, salesperson, saledate, carsaleid))

        conn.commit()
        print("✅ 更新成功")
        return True

    except psycopg2.Error as e:
        print("数据库错误：", e)
        conn.rollback()
        return False

    finally:
        cur.close()
        conn.close()
