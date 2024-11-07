import copy

def extend_model(prev_model, next_model):
    if prev_model is None:
        prev_model = {}

    comp_model = copy.deepcopy(prev_model)
    migration_steps = []

    extend_warehouse(comp_model, next_model, migration_steps)

    return comp_model, migration_steps


def extend_warehouse(comp_model, next_model, migration_steps):
    extend_databases(
        comp_model.setdefault('databases', []),
        next_model.setdefault('databases', []),
        migration_steps,
        location = {}
    )


def extend_databases(comp_databases, next_databases, migration_steps, location):
    for next_database in next_databases:
        drop = next_database.get('$drop', False)
        name = next_database['name']
        if isinstance(name, dict):
            old_name = name['from']
            new_name = name['to']
        else:
            old_name = new_name = name

        new_location = copy.copy(location)
        new_location['database'] = new_name

        if drop:
            comp_databases = [d for d in comp_databases if d['name'] != old_name]
            migration_steps.append({
                'action': 'drop_database',
                'target': old_name,
                'location': new_location
            })
            continue

        if old_name in [d['name'] for d in comp_databases]:
            comp_database_ix = [i for i, d in enumerate(comp_databases) if d['name'] == old_name][0]
            extend_database(
                comp_databases[comp_database_ix],
                next_database,
                migration_steps,
                new_location
            )

        else:
            comp_databases.append(next_database)
            migration_steps.append({
                'action': 'new_database',
                'target': new_name,
                'location': new_location,
                'model': next_database
            })


def extend_database(comp_database, next_database, migration_steps, location):
    if isinstance(next_database['name'], dict):
        comp_database['name'] = next_database['name']['to']
        migration_steps.append({
            'action': 'rename_database',
            'location': location,
            **next_database['name']
        })

    extend_schemas(
        comp_database.setdefault('schemas', []),
        next_database.setdefault('schemas', []),
        migration_steps,
        location
    )


def extend_schemas(comp_schemas, next_schemas, migration_steps, location):
    for next_schema in next_schemas:
        drop = next_schema.get('$drop', False)
        name = next_schema['name']
        if isinstance(name, dict):
            old_name = name['from']
            new_name = name['to']
        else:
            old_name = new_name = name

        new_location = copy.copy(location)
        new_location['schema'] = new_name

        if drop:
            comp_schemas = [d for d in comp_schemas if d['name'] != old_name]
            migration_steps.append({
                'action': 'drop_schema',
                'target': old_name,
                'location': new_location
            })
            continue

        if old_name in [d['name'] for d in comp_schemas]:
            comp_schema_ix = [i for i, d in enumerate(comp_schemas) if d['name'] == old_name][0]
            extend_schema(
                comp_schemas[comp_schema_ix],
                next_schema,
                migration_steps,
                new_location
            )

        else:
            comp_schemas.append(next_schema)
            migration_steps.append({
                'action': 'new_schema',
                'target': new_name,
                'location': new_location,
                'model': next_schema
            })


def extend_schema(comp_schema, next_schema, migration_steps, location):
    if isinstance(next_schema['name'], dict):
        comp_schema['name'] = next_schema['name']['to']
        migration_steps.append({
            'action': 'rename_schema',
            'location': location,
            **next_schema['name']
        })

    extend_extensions(
        comp_schema.setdefault('extensions', []),
        next_schema.setdefault('extensions', []),
        migration_steps,
        location
    )
    extend_tables(
        comp_schema.setdefault('tables', []),
        next_schema.setdefault('tables', []),
        migration_steps,
        location
    )
    extend_procedures(
        comp_schema.setdefault('procedures', []),
        next_schema.setdefault('procedures', []),
        migration_steps,
        location
    )


def extend_extensions(comp_extensions, next_extensions, migration_steps, location):
    for next_extension in next_extensions:
        drop = next_extension.get('$drop', False)

        if drop:
            comp_extensions = [e for e in comp_extensions if e != next_extension]
            migration_steps.append({
                'action': 'drop_extension',
                'target': next_extension,
                'location': location
            })
            continue

        if next_extension in comp_extensions:
            continue
        else:
            comp_extensions.append(next_extension)
            migration_steps.append({
                'action': 'new_extension',
                'target': next_extension,
                'location': location
            })


def extend_tables(comp_tables, next_tables, migration_steps, location):
    for next_table in next_tables:
        drop = next_table.get('$drop', False)
        name = next_table['name']

        new_location = copy.copy(location)
        new_location['table'] = name

        if drop:
            comp_tables = [t for t in comp_tables if t['name'] != name]
            migration_steps.append({
                'action': 'drop_table',
                'target': name,
                'location': new_location
            })
            continue

        if name in [t['name'] for t in comp_tables]:
            comp_table_ix = [i for i, t in enumerate(comp_tables) if t['name'] == name][0]
            extend_table(comp_tables[comp_table_ix], next_table, migration_steps, new_location)
        else:
            comp_tables.append(next_table)
            migration_steps.append({
                'action': 'new_table',
                'target': name,
                'location': new_location
            })


def extend_table(comp_table, next_table, migration_steps, location):
    if isinstance(next_table['name'], dict):
        comp_table['name'] = next_table['name']['to']
        migration_steps.append({
            'action': 'rename_table',
            'location': location,
            **next_table['name']
        })

    extend_columns(
        comp_table.setdefault('columns', []),
        next_table.setdefault('columns', []),
        migration_steps,
        location
    )
    extend_constraints(
        comp_table.setdefault('constraints', []),
        next_table.setdefault('constraints', []),
        migration_steps,
        location
    )
    extend_indexes(
        comp_table.setdefault('indexes', []),
        next_table.setdefault('indexes', []),
        migration_steps,
        location
    )


def extend_procedures(comp_procedures, next_procedures, migration_steps, location):
    for next_procedure in next_procedures:
        drop = next_procedure.get('$drop', False)
        name = next_procedure['name']
        args = next_procedure.get('args', [])

        new_location = copy.copy(location)
        new_location['procedure'] = name

        if drop:
            comp_procedures = [
                p for p in comp_procedures if not (
                    p['name'] == name and
                    args_match(p.get('args', []), args)
                )
            ]
            migration_steps.append({
                'action': 'drop_procedure',
                'target': name,
                'location': new_location
            })
            continue

        found = False
        for i, comp_procedure in enumerate(comp_procedures):
            if (
                comp_procedure['name'] == name and
                args_match(comp_procedure.get('args', []), args)
            ):
                comp_procedures[i] = extend_procedure(
                    comp_procedure,
                    next_procedure,
                    migration_steps,
                    new_location
                )
                found = True
                break

        if not found:
            comp_procedures.append(next_procedure)
            migration_steps.append({
                'action': 'new_procedure',
                'target': next_procedure,
                'location': new_location
            })


def args_match(a1, a2):
    if len(a1) != len(a2):
        return False

    for arg1, arg2 in zip(a1, a2):
        if arg1['name'] != arg2['name']:
            return False

        if arg1['type'] != arg2['type']:
            return False

    return True


def extend_procedure(comp_procedure, next_procedure, migration_steps, location):
    if isinstance(next_procedure['name'], dict):
        comp_procedure['name'] = next_procedure['name']['to']
        migration_steps.append({
            'action': 'rename_procedure',
            'location': location,
            **next_procedure['name']
        })

    comp_procedure['sql'] = next_procedure['sql']
    comp_procedure['args'] = next_procedure.get('args', [])

    migration_steps.append({
        'action': 'modify_procedure',
        'target': comp_procedure,
        'location': location
    })
    return comp_procedure


def extend_columns(comp_columns, next_columns, migration_steps, location):
    for next_column in next_columns:
        new_location = copy.copy(location)
        new_location['column'] = next_column['name']

        drop = next_column.get('$drop', False)
        name = next_column['name']

        if drop:
            comp_columns = [c for c in comp_columns if c['name'] != name]
            migration_steps.append({
                'action': 'drop_column',
                'target': name,
                'location': new_location
            })
            continue

        if name in [c['name'] for c in comp_columns]:
            comp_column_ix = [i for i, c in enumerate(comp_columns) if c['name'] == name][0]
            extend_column(
                comp_columns[comp_column_ix],
                next_column,
                migration_steps,
                new_location
            )
        else:
            comp_columns.append(next_column)
            migration_steps.append({
                'action': 'new_column',
                'target': next_column,
                'location': new_location
            })


def extend_column(comp_column, next_column, migration_steps, location):
    if isinstance(next_column['name'], dict):
        comp_column['name'] = next_column['name']['to']
        migration_steps.append({
            'action': 'rename_column',
            'location': location,
            **next_column['name']
        })

    for key, value in next_column.items():
        comp_column[key] = value

    migration_steps.append({
        'action': 'modify_column',
        'target': comp_column,
        'location': location
    })


def extend_constraints(comp_constraints, next_constraints, migration_steps, location):
    for next_constraint in next_constraints:
        new_location = copy.copy(location)
        new_location['constraint'] = next_constraint['name']

        drop = next_constraint.get('$drop', False)
        name = next_constraint['name']

        if drop:
            comp_constraints = [c for c in comp_constraints if c['name'] != name]
            migration_steps.append({
                'action': 'drop_constraint',
                'target': name,
                'location': new_location
            })
            continue

        if name in [c['name'] for c in comp_constraints]:
            comp_constraint_ix = [i for i, c in enumerate(comp_constraints) if c['name'] == name][0]
            extend_constraint(
                comp_constraints[comp_constraint_ix],
                next_constraint,
                migration_steps,
                new_location
            )
        else:
            comp_constraints.append(next_constraint)
            migration_steps.append({
                'action': 'new_constraint',
                'target': next_constraint,
                'location': new_location
            })

def extend_constraint(comp_constraint, next_constraint, migration_steps, location):
    if isinstance(next_constraint['name'], dict):
        comp_constraint['name'] = next_constraint['name']['to']
        migration_steps.append({
            'action': 'rename_constraint',
            'location': location,
            **next_constraint['name']
        })

    for key, value in next_constraint.items():
        comp_constraint[key] = value

    migration_steps.append({
        'action': 'modify_constraint',
        'target': comp_constraint,
        'location': new_location
    })


def extend_indexes(comp_indexes, next_indexes, migration_steps, location):
    for next_index in next_indexes:
        new_location = copy.copy(location)
        new_location['index'] = next_index['name']

        drop = next_index.get('$drop', False)
        name = next_index['name']

        if drop:
            comp_indexes = [idx for idx in comp_indexes if idx['name'] != name]
            migration_steps.append({
                'action': 'drop_index',
                'target': name,
                'location': new_location
            })
            continue

        if name in [idx['name'] for idx in comp_indexes]:
            comp_index_ix = [i for i, idx in enumerate(comp_indexes) if idx['name'] == name][0]
            extend_index(
                comp_indexes[comp_index_ix],
                next_index,
                migration_steps,
                new_location
            )
        else:
            comp_indexes.append(next_index)
            migration_steps.append({
                'action': 'new_index',
                'target': next_index,
                'location': new_location
            })


def extend_index(comp_index, next_index, migration_steps, location):
    if isinstance(next_index['name'], dict):
        comp_index['name'] = next_index['name']['to']
        migration_steps.append({
            'action': 'rename_index',
            'location': location,
            **next_index['name']
        })

    for key, value in next_index.items():
        comp_index[key] = value

    migration_steps.append({
        'action': 'modify_index',
        'target': comp_index,
        'location': new_location
    })
