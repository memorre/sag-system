import psycopg2

def run_sql_script():
    with open("SAGschema.sql", "r") as f:
        sql = f.read()

    conn = psycopg2.connect(
        database="y25s1c9120_taye0567",
        user="y25s1c9120_taye0567",
        password="sHYKj7XW",
        host="awsprddbs4836.shared.sydney.edu.au"
    )
    cur = conn.cursor()
    try:
        # 一次性执行整个脚本
        cur.execute(sql)
        conn.commit()
        print("✅ Database initialized successfully.")
    except Exception as e:
        print("💥 SQL execution failed:", e)
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_sql_script()