-- SAGschema.sql

SET datestyle = 'ISO, DMY';

-- 1. Drop all objects to avoid conflicts
DROP TABLE IF EXISTS CarSales CASCADE;
DROP TABLE IF EXISTS Model CASCADE;
DROP TABLE IF EXISTS Make CASCADE;
DROP TABLE IF EXISTS Customer CASCADE;
DROP TABLE IF EXISTS Salesperson CASCADE;

DROP FUNCTION IF EXISTS checkLogin(VARCHAR, VARCHAR);
DROP FUNCTION IF EXISTS loginUser(VARCHAR, VARCHAR);
DROP FUNCTION IF EXISTS getCarSalesSummary();
DROP FUNCTION IF EXISTS findCarSales(VARCHAR, VARCHAR);
DROP FUNCTION IF EXISTS addCarSale(VARCHAR, VARCHAR, INTEGER, INTEGER, NUMERIC, BOOLEAN, VARCHAR, VARCHAR, DATE);
DROP FUNCTION IF EXISTS updateCarSale(INTEGER, VARCHAR, VARCHAR, INTEGER, INTEGER, NUMERIC, BOOLEAN, VARCHAR, VARCHAR, DATE);

-- 2. Create tables

CREATE TABLE Salesperson (
    UserName VARCHAR(10) PRIMARY KEY,
    Password VARCHAR(20) NOT NULL,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    UNIQUE(FirstName, LastName)
);

CREATE TABLE Customer (
    CustomerID VARCHAR(10) PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Mobile VARCHAR(20) NOT NULL
);

CREATE TABLE Make (
    MakeCode VARCHAR(5) PRIMARY KEY,
    MakeName VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE Model (
    ModelCode VARCHAR(10) PRIMARY KEY,
    ModelName VARCHAR(20) UNIQUE NOT NULL,
    MakeCode VARCHAR(10) NOT NULL REFERENCES Make(MakeCode)
);

CREATE TABLE CarSales (
    CarSaleID SERIAL PRIMARY KEY,
    MakeCode VARCHAR(10) NOT NULL REFERENCES Make(MakeCode),
    ModelCode VARCHAR(10) NOT NULL REFERENCES Model(ModelCode),
    BuiltYear INTEGER NOT NULL CHECK (BuiltYear BETWEEN 1950 AND EXTRACT(YEAR FROM CURRENT_DATE)),
    Odometer INTEGER NOT NULL CHECK (Odometer >= 0),
    Price DECIMAL(10,2) NOT NULL CHECK (Price >= 0),
    IsSold BOOLEAN NOT NULL,
    BuyerID VARCHAR(10) REFERENCES Customer(CustomerID),
    SalespersonID VARCHAR(10) REFERENCES Salesperson(UserName),
    SaleDate DATE
);

-- 3. Insert sample data

INSERT INTO Salesperson VALUES
    ('jdoe', 'Pass1234', 'John', 'Doe'),
    ('brown', 'Passwxyz', 'Bob', 'Brown'),
    ('ksmith1', 'Pass5566', 'Karen', 'Smith');

INSERT INTO Customer VALUES
    ('c001', 'David', 'Wilson', '4455667788'),
    ('c899', 'Eva', 'Taylor', '5566778899'),
    ('c199', 'Frank', 'Anderson', '6677889900'),
    ('c910', 'Grace', 'Thomas', '7788990011'),
    ('c002', 'Stan', 'Martinez', '8899001122'),
    ('c233', 'Laura', 'Roberts', '9900112233'),
    ('c123', 'Charlie', 'Davis', '7712340011'),
    ('c321', 'Jane', 'Smith', '9988990011'),
    ('c211', 'Alice', 'Johnson', '7712222221');

INSERT INTO Make VALUES
    ('MB', 'Mercedes Benz'),
    ('TOY', 'Toyota'),
    ('VW', 'Volkswagen'),
    ('LEX', 'Lexus'),
    ('LR', 'Land Rover');

INSERT INTO Model (ModelCode, ModelName, MakeCode) VALUES
    ('aclass', 'A Class', 'MB'),
    ('cclass', 'C Class', 'MB'),
    ('eclass', 'E Class', 'MB'),
    ('camry', 'Camry', 'TOY'),
    ('corolla', 'Corolla', 'TOY'),
    ('rav4', 'RAV4', 'TOY'),
    ('defender', 'Defender', 'LR'),
    ('rangerover', 'Range Rover', 'LR'),
    ('discosport', 'Discovery Sport', 'LR'),
    ('golf', 'Golf', 'VW'),
    ('passat', 'Passat', 'VW'),
    ('troc', 'T Roc', 'VW'),
    ('ux', 'UX', 'LEX'),
    ('gx', 'GX', 'LEX'),
    ('nx', 'NX', 'LEX');

INSERT INTO CarSales (MakeCode, ModelCode, BuiltYear, Odometer, Price, IsSold, BuyerID, SalespersonID, SaleDate) VALUES
    ('MB', 'cclass', 2020, 64210, 72000.00, TRUE, 'c001', 'jdoe', '2024-03-01'),
    ('MB', 'eclass', 2019, 31210, 89000.00, FALSE, NULL, NULL, NULL),
    ('TOY', 'camry', 2021, 98200, 37200.00, TRUE, 'c123', 'brown', '2023-12-07'),
    ('TOY', 'corolla', 2022, 65000, 35000.00, TRUE, 'c910', 'jdoe', '2024-09-21'),
    ('LR', 'defender', 2018, 115000, 97000.00, FALSE, NULL, NULL, NULL),
    ('VW', 'golf', 2023, 22000, 33000.00, TRUE, 'c233', 'jdoe', '2023-11-06'),
    ('LEX', 'nx', 2020, 67000, 79000.00, TRUE, 'c321', 'brown', '2025-01-01'),
    ('LR', 'discosport', 2021, 43080, 85000.00, TRUE, 'c211', 'ksmith1', '2021-01-27'),
    ('TOY', 'rav4', 2019, 92900, 48000.00, FALSE, NULL, NULL, NULL),
    ('MB', 'aclass', 2022, 47000, 57000.00, TRUE, 'c199', 'jdoe', '2025-03-01'),
    ('LEX', 'ux', 2023, 23000, 70000.00, TRUE, 'c899', 'brown', '2023-01-01'),
    ('VW', 'passat', 2020, 63720, 42000.00, FALSE, NULL, NULL, NULL),
    ('MB', 'eclass', 2021, 12000, 155000.00, TRUE, 'c002', 'ksmith1', '2024-10-01'),
    ('LR', 'rangerover', 2017, 60000, 128000.00, FALSE, NULL, NULL, NULL),
    ('TOY', 'camry', 2025, 10, 49995.00, FALSE, NULL, NULL, NULL),
    ('LR', 'discosport', 2022, 53000, 89900.00, FALSE, NULL, NULL, NULL),
    ('MB', 'cclass', 2023, 55000, 82100.00, FALSE, NULL, NULL, NULL),
    ('MB', 'aclass', 2025, 5, 78000.00, FALSE, NULL, NULL, NULL),
    ('MB', 'aclass', 2015, 8912, 12000.00, TRUE, 'c199', 'jdoe', '2020-03-11'),
    ('TOY', 'camry', 2024, 21000, 42000.00, FALSE, NULL, NULL, NULL),
    ('LEX', 'gx', 2025, 6, 128085.00, FALSE, NULL, NULL, NULL),
    ('MB', 'eclass', 2019, 99220, 105000.00, FALSE, NULL, NULL, NULL);

-- 4. Stored procedures / functions

-- Login: check username/password, returns user info
DROP FUNCTION IF EXISTS loginUser(VARCHAR, VARCHAR);

CREATE OR REPLACE FUNCTION loginUser(p_username varchar, p_password varchar)
RETURNS TABLE(user_name varchar, first_name varchar, last_name varchar) AS $$
BEGIN
    RETURN QUERY
    SELECT
        UserName AS user_name,
        FirstName AS first_name,
        LastName AS last_name
    FROM Salesperson
    WHERE lower(UserName) = lower(p_username)
      AND Password = p_password;
END;
$$ LANGUAGE plpgsql;

-- Check if login is valid, returns boolean
DROP FUNCTION IF EXISTS checkLogin(VARCHAR, VARCHAR);

CREATE OR REPLACE FUNCTION checkLogin(p_username VARCHAR, p_password VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM Salesperson
        WHERE lower(UserName) = lower(p_username)
          AND Password = p_password
    ) THEN
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Car sales summary
DROP FUNCTION IF EXISTS getCarSalesSummary();

CREATE OR REPLACE FUNCTION getCarSalesSummary()
RETURNS TABLE(
    make_name VARCHAR,
    model_name VARCHAR,
    available_units BIGINT,    -- 这里必须是 BIGINT
    sold_units BIGINT,         -- 这里也必须是 BIGINT
    total_sales NUMERIC,
    last_purchased DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        M.MakeName,
        Mo.ModelName,
        COUNT(*) FILTER (WHERE cs.IsSold = FALSE) AS available_units,
        COUNT(*) FILTER (WHERE cs.IsSold = TRUE) AS sold_units,
        COALESCE(SUM(cs.Price) FILTER (WHERE cs.IsSold = TRUE), 0) AS total_sales,
        MAX(cs.SaleDate) FILTER (WHERE cs.IsSold = TRUE) AS last_purchased
    FROM
        Model Mo
        JOIN Make M ON Mo.MakeCode = M.MakeCode
        LEFT JOIN CarSales cs ON cs.MakeCode = M.MakeCode AND cs.ModelCode = Mo.ModelCode
    GROUP BY
        M.MakeName, Mo.ModelName
    ORDER BY
        M.MakeName, Mo.ModelName;
END;
$$ LANGUAGE plpgsql;

-- Find car sales for a salesperson (by keyword)
DROP FUNCTION IF EXISTS findCarSales(VARCHAR, VARCHAR);

CREATE OR REPLACE FUNCTION findCarSales(p_salespersonID VARCHAR, p_keyword VARCHAR)
RETURNS TABLE(
    carsaleid INTEGER,
    make VARCHAR,
    model VARCHAR,
    builtYear INTEGER,
    odometer INTEGER,
    price NUMERIC,
    is_sold BOOLEAN,
    buyer_name VARCHAR,
    salesperson_name VARCHAR,
    sale_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cs.CarSaleID,
        M.MakeName,
        Mo.ModelName,
        cs.BuiltYear,
        cs.Odometer,
        cs.Price,
        cs.IsSold,
        (C.FirstName || ' ' || C.LastName) AS buyer_name,
        (S.FirstName || ' ' || S.LastName) AS salesperson_name,
        cs.SaleDate
    FROM CarSales cs
    JOIN Make M ON cs.MakeCode = M.MakeCode
    JOIN Model Mo ON cs.ModelCode = Mo.ModelCode
    LEFT JOIN Customer C ON cs.BuyerID = C.CustomerID
    LEFT JOIN Salesperson S ON cs.SalespersonID = S.UserName
    WHERE
        cs.SalespersonID = p_salespersonID
        AND (
            p_keyword IS NULL
            OR p_keyword = ''
            OR M.MakeName ILIKE '%' || p_keyword || '%'
            OR Mo.ModelName ILIKE '%' || p_keyword || '%'
            OR C.FirstName ILIKE '%' || p_keyword || '%'
            OR C.LastName ILIKE '%' || p_keyword || '%'
        )
    ORDER BY cs.SaleDate DESC;
END;
$$ LANGUAGE plpgsql;

-- Add car sale (with validation)
DROP FUNCTION IF EXISTS addCarSale(VARCHAR, VARCHAR, INTEGER, INTEGER, NUMERIC, BOOLEAN, VARCHAR, VARCHAR, DATE);

CREATE OR REPLACE FUNCTION addCarSale(
    p_makeCode VARCHAR,
    p_modelCode VARCHAR,
    p_builtYear INTEGER,
    p_odometer INTEGER,
    p_price NUMERIC,
    p_isSold BOOLEAN,
    p_buyerID VARCHAR,
    p_salespersonID VARCHAR,
    p_saleDate DATE
) RETURNS INTEGER AS $$
DECLARE newID INTEGER;
BEGIN
    IF p_builtYear < 1950 OR p_builtYear > EXTRACT(YEAR FROM CURRENT_DATE) THEN
        RAISE EXCEPTION 'Invalid BuiltYear %', p_builtYear;
    END IF;
    IF p_odometer < 0 THEN
        RAISE EXCEPTION 'Invalid Odometer %', p_odometer;
    END IF;
    IF p_price < 0 THEN
        RAISE EXCEPTION 'Invalid Price %', p_price;
    END IF;
    IF p_isSold THEN
        IF p_buyerID IS NULL OR p_salespersonID IS NULL OR p_saleDate IS NULL THEN
            RAISE EXCEPTION 'Missing buyer, salesperson, or sale date for sold car';
        END IF;
        IF p_saleDate > CURRENT_DATE THEN
            RAISE EXCEPTION 'SaleDate % cannot be in the future', p_saleDate;
        END IF;
    ELSE
        IF p_buyerID IS NOT NULL OR p_salespersonID IS NOT NULL OR p_saleDate IS NOT NULL THEN
            RAISE EXCEPTION 'BuyerID, SalespersonID, and SaleDate must be null for unsold car';
        END IF;
    END IF;
    INSERT INTO CarSales(
        MakeCode, ModelCode, BuiltYear, Odometer, Price, IsSold, BuyerID, SalespersonID, SaleDate
    ) VALUES (
        p_makeCode, p_modelCode, p_builtYear, p_odometer, p_price, p_isSold, p_buyerID, p_salespersonID, p_saleDate
    ) RETURNING CarSaleID INTO newID;
    RETURN newID;
END;
$$ LANGUAGE plpgsql;

-- Update car sale (with validation)
DROP FUNCTION IF EXISTS updateCarSale(INTEGER, VARCHAR, VARCHAR, INTEGER, INTEGER, NUMERIC, BOOLEAN, VARCHAR, VARCHAR, DATE);

CREATE OR REPLACE FUNCTION updateCarSale(
    p_carsaleID INTEGER,
    p_makeCode VARCHAR,
    p_modelCode VARCHAR,
    p_builtYear INTEGER,
    p_odometer INTEGER,
    p_price NUMERIC,
    p_isSold BOOLEAN,
    p_buyerID VARCHAR,
    p_salespersonID VARCHAR,
    p_saleDate DATE
) RETURNS INTEGER AS $$
DECLARE updatedID INTEGER;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM CarSales WHERE CarSaleID = p_carsaleID) THEN
        RAISE EXCEPTION 'CarSaleID % does not exist', p_carsaleID;
    END IF;
    IF p_builtYear < 1950 OR p_builtYear > EXTRACT(YEAR FROM CURRENT_DATE) THEN
        RAISE EXCEPTION 'Invalid BuiltYear %', p_builtYear;
    END IF;
    IF p_odometer < 0 THEN
        RAISE EXCEPTION 'Invalid Odometer %', p_odometer;
    END IF;
    IF p_price < 0 THEN
        RAISE EXCEPTION 'Invalid Price %', p_price;
    END IF;
    IF p_isSold THEN
        IF p_buyerID IS NULL OR p_salespersonID IS NULL OR p_saleDate IS NULL THEN
            RAISE EXCEPTION 'Missing buyer, salesperson, or sale date for sold car (update)';
        END IF;
        IF p_saleDate > CURRENT_DATE THEN
            RAISE EXCEPTION 'SaleDate % cannot be in the future (update)', p_saleDate;
        END IF;
    ELSE
        IF p_buyerID IS NOT NULL OR p_salespersonID IS NOT NULL OR p_saleDate IS NOT NULL THEN
            RAISE EXCEPTION 'BuyerID, SalespersonID, and SaleDate must be null for unsold car (update)';
        END IF;
    END IF;
    UPDATE CarSales
    SET MakeCode = p_makeCode,
        ModelCode = p_modelCode,
        BuiltYear = p_builtYear,
        Odometer = p_odometer,
        Price = p_price,
        IsSold = p_isSold,
        BuyerID = p_buyerID,
        SalespersonID = p_salespersonID,
        SaleDate = p_saleDate
    WHERE CarSaleID = p_carsaleID
    RETURNING CarSaleID INTO updatedID;
    RETURN updatedID;
END;
$$ LANGUAGE plpgsql;

-- END of file