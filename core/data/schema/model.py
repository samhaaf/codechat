import json
import os
import sys


def build_model_from_file(path):

    def recur(value, current_path):

        if isinstance(value, list):
            return [recur(v, current_path) for v in value]

        elif isinstance(value, dict):

            if '$ref' in value and isinstance(value['$ref'], str):
                ref_path = os.path.join(os.path.dirname(current_path), value['$ref'])
                return build_model_from_file(ref_path)

            else:
                return {k: recur(v, current_path) for k, v in value.items()}

        else:
            return value


    with open(path, 'r') as f:
        model = json.load(f)

    return recur(model, path)


# Example usage
if __name__ == "__main__":

    if len(sys.argv) > 1:
        model = build_model_from_file(sys.argv[1])
        print(json.dumps(model, indent=4))

    else:
        print("Usage: python script.py <path-to-initial-model>")
