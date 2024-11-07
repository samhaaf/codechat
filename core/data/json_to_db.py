import sys
import json
import psycopg2
from collections import OrderedDict
from psycopg2.extras import execute_values

def write_json_to_db(json_path):
    with open(json_path) as f:
        data = json.load(f, object_pairs_hook=OrderedDict)

    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432'
        )

        cur = conn.cursor()

        for table, rows in data.items():
            if not rows:
                continue

            columns = ', '.join(f'{key}' for key in rows[0].keys())
            values = [tuple(
                json.dumps(v) if isinstance(v, dict) else v
                for v in row.values()
            ) for row in rows]

            query = f'INSERT INTO "logscale"."{table}" ({columns}) VALUES %s'

            execute_values(cur, query, values)

            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Data write error.\n\tQuery: {query}\n\tValues:{values[:1]}\n\tError: {error}")
        if conn is not None:
            conn.rollback()
        sys.exit(1)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    write_json_to_db(sys.argv[1])
