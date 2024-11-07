def new_database(model):
    sql = ""

    # Extensions
    for extension in model.get("extensions", []):
        sql += f"CREATE EXTENSION IF NOT EXISTS \"{extension}\";\n\n"

    # Tables
    table_order = get_valid_table_order(model['tables'])
    for table in table_order:
        sql += f"CREATE TABLE {table['name']} (\n"
        for col in table['columns']:
            col_str = f"    {col['name']} {col['type']}"
            if col.get('is_primary', False):
                col_str += " PRIMARY KEY"
            if not col.get('nullable', True):
                col_str += " NOT NULL"
            if col.get('references'):
                ref = col['references']
                col_str += f" REFERENCES {ref['table']}({ref['value']})"
            if col.get('default'):
                col_str += f" DEFAULT {col['default']}"

            sql += f"{col_str},\n"

        # Remove the trailing comma and add closing bracket
        sql = sql.rstrip(",\n") + "\n);\n\n"

    return sql


def get_valid_table_order(tables):
    unresolved = set([table['name'] for table in tables])
    resolved = set()
    resolved_order = []

    while unresolved:
        newly_resolved = set()

        for table_name in list(unresolved):
            table = next(table for table in tables if table['name'] == table_name)
            references = [col.get('references', {}).get('table', '') for col in table['columns']]
            if all((ref == '' or ref in resolved) for ref in references):
                resolved.add(table_name)
                newly_resolved.add(table_name)
                unresolved.remove(table_name)
                resolved_order.append(table)

        if not newly_resolved:
            raise ValueError("Circular dependency or missing reference among tables.")

    return resolved_order
