import json
from scipy.spatial import distance
from kit.utils.hash import HashDict
from pathlib import Path


class VectorDb:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path).absolute()
        self.vectors_dict, self.values_dict = self.load()

    def load(self) -> Tuple[HashDict, HashDict]:
        try:
            with open(self.db_path, 'r') as file:
                data = json.load(file)
                return HashDict(data["vectors"]), HashDict(data["values"])
        except FileNotFoundError:
            return HashDict(), HashDict()

    def save(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_path, 'w') as file:
            data = {
                "vectors": self.vectors_dict,
                "values": self.values_dict
            }
            json.dump(data, file)

    @staticmethod
    def euclidean_distance(v1: Tuple, v2: Tuple) -> float:
        return distance.euclidean(v1, v2)

    def put(self, vector: Tuple, item: Any):
        vector_id = self.vectors_dict.put(vector)
        self.values_dict.put(item, id=vector_id)

    def query(self, vector: Tuple, n: int, distance_func=None) -> List[Any]:
        if distance_func is None:
            distance_func = self.euclidean_distance

        distances = [(v_id, distance_func(vector, v)) for v_id, v in self.vectors_dict.items()]
        distances.sort(key=lambda x: x[1])

        closest_ids = [v_id for v_id, _ in distances[:n]]
        return [self.values_dict[v_id] for v_id in closest_ids]
