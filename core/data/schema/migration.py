import sys
import json
import sql as sql_generator


def build_migration_sql(migration_steps):
    migration_sql = ""
    for step in migration_steps:
        match step['action']:
            case 'new_database':
                migration_sql += sql_generator.new_database(step['model'])
            case 'new_schema':
                migration_sql += sql_generator.new_schema(step['model'])
            case 'new_extension':
                migration_sql += sql_generator.new_extension(step['model'])
            case 'new_procedue':
                migration_sql += sql_generator.new_procedure(step['model'])
            case 'new_table':
                migration_sql += sql_generator.new_table(step['model'])
            case 'new_column':
                migration_sql += sql_generator.new_column(step['model'])
            case 'new_index':
                migration_sql += sql_generator.new_index(step['model'])
            case 'new_constraint':
                migration_sql += sql_generator.new_constraint(step['model'])
            case _:
                raise ('Unhandled migration_step action: ' + step['action'])
    return migration_sql


if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        migration_steps = json.load(f)
    print(build_migration_sql(migration_steps))
