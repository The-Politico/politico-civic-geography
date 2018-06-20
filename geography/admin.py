# -*- coding: utf-8 -*-
from django.contrib import admin
from geography.models import (Division, DivisionLevel, Geometry,
                              IntersectRelationship, Point, PointLabelOffset)


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


class IntersectRelationshipInline(admin.StackedInline):
    model = IntersectRelationship
    fk_name = 'from_division'
    extra = 0


class DivisionAdmin(admin.ModelAdmin):
    inlines = (IntersectRelationshipInline,)
    list_display = ('label', 'level', 'code')
    list_filter = ('level',)
    search_fields = ('code', 'label')
    readonly_fields = ('parent', 'uid',)

    fieldsets = (
        ('Names', {
            'fields': ('name', 'label', 'short_label')
        }),
        ('Reference codes', {
            'fields': ('code', 'code_components')
        }),
        ('In effect', {
            'fields': (
                'effective', 'effective_start', 'effective_end',
            )
        }),
        ('Reference fields', {
            'fields': ('parent', 'uid')
        })
    )


class PointInline(admin.StackedInline):
    model = Point
    fk_name = 'geometry'
    extra = 0


class GeometryAdmin(admin.ModelAdmin):
    inlines = (PointInline,)
    list_display = ('division', 'map_level')
    list_filter = (('subdivision_level', custom_titled_filter('map level')), )
    search_fields = ('division__name',)
    readonly_fields = ('file_size', 'large_preview', 'source', 'series',)

    fieldsets = (
        (None, {
            'fields': ('division', 'subdivision_level', 'source', 'series',)
        }),
        ('Geo data', {
            'fields': (
                'topojson', 'simplification',
                'file_size', 'large_preview',)
        }),
        ('In effect', {
            'fields': (
                'effective', 'effective_start', 'effective_end',
            )
        }),
    )

    def map_level(self, obj):
        return obj.subdivision_level.name


class PointLabelOffsetInline(admin.StackedInline):
    model = PointLabelOffset
    fk_name = 'point'
    extra = 0


class PointAdmin(admin.ModelAdmin):
    inlines = (PointLabelOffsetInline,)


admin.site.register(DivisionLevel)
admin.site.register(Division, DivisionAdmin)
admin.site.register(Geometry, GeometryAdmin)
admin.site.register(Point, PointAdmin)
