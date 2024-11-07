from .model import build_model_from_file
from .extend import extend_model
from .migration import build_migration_sql
import sql as sql_generator
import os
import json
import sys


def process_deltas(delta_path):
    deltas = get_delta_order(delta_path)

    last_model = None
    for delta in deltas:
        delta_dir = os.path.join(delta_path, delta) + '/'

        comp_model = None
        if os.path.exists(delta_dir + 'build/model.json'):
            with open(delta_dir + 'build/model.json') as f:
                comp_model = json.load(f)

        have_ddl = os.path.exists(delta_dir + 'build/ddl.sql')
        have_migration = os.path.exists(delta_dir + 'build/migration.sql')

        if have_ddl and have_migration and comp_model is not None:  # TODO: and same hash
            continue

        this_delta = None
        for model_file in ['warehouse.json', 'database.json']:
            if os.path.exists(delta_dir + model_file):
                this_delta = build_model_from_file(delta_dir + model_file)
                if model_file == 'database.json':
                    this_delta = {'databases': [this_delta]}

        assert this_delta is not None, (
            f'Need either {delta_dir}warehouse.json or {delta_dir}database.json'
        )

        this_model, migration_steps = extend_model(last_model, this_delta)

        migration_sql = build_migration_sql(migration_steps)

        ddl_sql = sql_generator.new_database(this_model['databases'][0])

        if not os.path.exists(delta_dir + 'build/'):
            os.makedirs(delta_dir + 'build/')

        with open(delta_dir + 'build/model.json', 'w') as f:
            json.dump(this_model, f, indent=4)

        with open(delta_dir + 'build/migration_steps.json', 'w') as f:
            json.dump(migration_steps, f, indent=4)

        with open(delta_dir + 'build/migration.sql', 'w') as f:
            f.write(migration_sql)

        with open(delta_dir + 'build/ddl.sql', 'w') as f:
            f.write(ddl_sql)


def get_delta_order(delta_dir):
    delta_dir = os.path.join(os.path.dirname(__file__), delta_dir)
    delta_folders = [folder for folder in os.listdir(delta_dir) if os.path.isdir(os.path.join(delta_dir, folder))]
    delta_folders.sort()
    return delta_folders


if __name__ == '__main__':
    process_deltas(sys.argv[1] if len(sys) > 1 else './deltas')
