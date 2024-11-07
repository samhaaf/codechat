import psycopg2
import psycopg2.extras
from .query_template import process_query_template
from .connect import get_connection


def execute(query, values=None, conn=None, commit=True, templated=True):
    """
    Execute a query using psycopg2 execute, handle errors,
    and return the results as a list of dictionaries.
    """
    conn = conn or get_connection()
    results = []
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        # Process the custom templated query
        if templated and '!' in query:
            query, values = process_query_template(query, values)

        # Execute the processed query with the processed values
        if processed_values is None:
            cursor.execute(query)
        else:
            cursor.execute(query, values)

        if commit:
            conn.commit()

        if cursor.description:
            return [dict(row) for row in cursor.fetchall()]
        else:
            return None

    except (psycopg2.OperationalError, psycopg2.Error) as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
