from . import ASSEMBLY_ALGORITHMS
import json


class AssemblyConfigError(ValueError):
    pass


class AssemblyConfiguration:
    def __init__(self, label, algorithm):
        self.label = label
        self.algorithm = algorithm

    @classmethod
    def from_json(cls, d):
        return cls(d["label"], d["algorithm"])

    @staticmethod
    def parse_json(fh):
        algorithms = []
        assemblers = []
        data = json.load(fh)
        for d in data:
            algorithm = d["algorithm"]
            if algorithm not in ASSEMBLY_ALGORITHMS:
                message = f"Found unsupported assembly algorithm in config file: [[{algorithm}]]!"
                raise AssemblyConfigError(message)
            if algorithm in algorithms:
                message = (
                    f"Found duplicate assembly algorithm found in config file: [[{algorithm}]]!"
                )
                raise AssemblyConfigError(message)
            algorithms.append(algorithm)
            assemblers.append(AssemblyConfiguration.from_json(d))
        return assemblers
