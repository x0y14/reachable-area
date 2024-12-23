import sqlite3

def main():
    dbname = "../backend/engine/cache.db"
    conn = sqlite3.connect(dbname)

    cur = conn.cursor()
    cur.execute(
        """
        create table if not exists routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            is_bus_route INTEGER,
            from_ TEXT,
            to_ TEXT,
            time_required INTEGER,
            transfer INTEGER,
            fare INTEGER,
            distance INTEGER,
            check (from_ <> to_),
            unique (is_bus_route, from_, to_, time_required, transfer, fare, distance)
        );
        """
    )
    conn.commit()

    cur.execute(
        """
        create table if not exists isochrones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coordinate_lng real not null,
            coordinate_lat real not null,
            web_request JSON,
            web_response JSON,
            unique ( coordinate_lng, coordinate_lat,  web_request, web_response )
        );
        """
    )

    conn.close()

if __name__ == "__main__":
    main()