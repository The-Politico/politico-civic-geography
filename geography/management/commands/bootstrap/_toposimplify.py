# Imports from python.
import json
import subprocess


class Toposimplify:
    @staticmethod
    def toposimplify(geojson, p):
        """
        Convert geojson and simplify topology.

        geojson is a dict representing geojson.
        p is a simplification threshold value between 0 and 1.
        """
        proc_out = subprocess.run(
            ["geo2topo"],
            input=bytes(json.dumps(geojson), "utf-8"),
            stdout=subprocess.PIPE,
        )
        proc_out = subprocess.run(
            ["toposimplify", "-P", p],
            input=proc_out.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        topojson = json.loads(proc_out.stdout)
        # Standardize object name
        topojson["objects"]["divisions"] = topojson["objects"].pop("-")
        return topojson
