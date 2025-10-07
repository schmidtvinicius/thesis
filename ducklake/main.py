import duckdb

def init_db(con: duckdb.DuckDBPyConnection):
    cursor = con.cursor()

def main():
    con = duckdb.connect(config={"allow_unsigned_extensions": "true"})
    con.execute("FORCE INSTALL ducklake; LOAD ducklake;")
    con.execute(
        "ATTACH 'ducklake:events_ducklake.db' AS events_ducklake (DATA_INLINING_ROW_LIMIT 10);")
    init_db(con)


if __name__ == "__main__":
    main()
