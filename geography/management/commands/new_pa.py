import geojson
import json
import shapefile
import os
import subprocess

from datetime import date
from django.contrib.humanize.templatetags.humanize import ordinal
from django.core.management.base import BaseCommand
from geography.models import Division, DivisionLevel, Geometry
from tqdm import tqdm

SHP_BASE = 'http://www.pacourts.us/assets/files/setting-6061/file-6845.zip'
SHP_SLUG = 'clipped_penn'
STATE_LEVEL = DivisionLevel.STATE


class Command(BaseCommand):
    @staticmethod
    def toposimplify(geojson, p):
        """
        Convert geojson and simplify topology.

        geojson is a dict representing geojson.
        p is a simplification threshold value between 0 and 1.
        """
        proc_out = subprocess.run(
            ['geo2topo'],
            input=bytes(
                json.dumps(geojson),
                'utf-8'),
            stdout=subprocess.PIPE
        )
        proc_out = subprocess.run(
            ['toposimplify', '-P', p],
            input=proc_out.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        topojson = json.loads(proc_out.stdout)
        # Standardize object name
        topojson['objects']['divisions'] = topojson['objects'].pop('-')
        return topojson

    def get_district_shp(self):
        cmd_path = os.path.dirname(os.path.realpath(__file__))
        pa_path = os.path.join(cmd_path, '../../bin/clipped_penn')

        shape = shapefile.Reader(os.path.join(
            pa_path,
            '{}.shp'.format(SHP_SLUG)
        ))
        fields = shape.fields[1:]
        field_names = [f[0] for f in fields]
        district_records = [shp for shp in shape.shapeRecords()]
        features = []
        for shp in district_records:
            rec = dict(zip(field_names, shp.record))
            label = '{} congressional district'.format(
                ordinal(int(rec['DISTRICT']))
            )

            geometry = shp.shape.__geo_interface__
            geodata = {
                'type': 'Feature',
                'geometry': geometry,
                'properties': {
                    'state': 42,
                    'district': rec['DISTRICT'],
                    'name': label
                }
            }
            features.append(geodata)
        return self.toposimplify(geojson.FeatureCollection(features), '0.03')

    def handle(self, *args, **options):
        cmd_path = os.path.dirname(os.path.realpath(__file__))
        pa_path = os.path.join(cmd_path, '../../bin/clipped_penn')

        shape = shapefile.Reader(os.path.join(
            pa_path,
            '{}.shp'.format(SHP_SLUG)
        ))

        fields = shape.fields[1:]
        field_names = [f[0] for f in fields]
        districts = [shp for shp in shape.shapeRecords()]

        state = Division.objects.get(
            code=42,
            level__name=DivisionLevel.STATE
        )

        district_level = DivisionLevel.objects.get(
            name=DivisionLevel.DISTRICT
        )

        for shp in tqdm(districts):
            district = dict(zip(field_names, shp.record))
            label = '{} {} congressional district'.format(
                state.label,
                ordinal(int(district['DISTRICT']))
            )

            district_obj, created = Division.objects.update_or_create(
                code=district['DISTRICT'],
                level=district_level,
                parent=state,
                defaults={
                    'name': label,
                    'label': label,
                    'code_components': {
                        'fips': {
                            'state': state.code,
                        },
                        'district': district['DISTRICT']
                    },
                }
            )

            geodata = {
                'type': 'Feature',
                'geometry': shp.shape.__geo_interface__,
                'properties': {
                    'state': 42,
                    'district': district['DISTRICT'],
                    'name': label
                }
            }

            district_geometry = district_obj.geometries.get(
                division=district_obj,
                subdivision_level=district_level,
                series=2016
            )

            district_geometry.topojson = self.toposimplify(geodata, '0.03')
            district_geometry.save()

        state_geometry = state.geometries.get(
            division=state,
            subdivision_level=district_level,
            series=2016
        )

        state_geometry.topojson = self.get_district_shp()
        state_geometry.save()
