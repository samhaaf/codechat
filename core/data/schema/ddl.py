import jsonmodel
import json
import sql as sql_generator


def ddl_from_model(model):
    # # Validate JSON against model
    # jsonmodel.validate(instance=model, model=json_model)

    ddl = sql_generator.new_database(model)

    return ddl


if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        model = json.load(f)

    sql = ddl_from_model()
    print(sql)
