from geography.models import Division

from .related_division import RelatedDivisionSerializer


class DivisionSerializer(RelatedDivisionSerializer):
    children = RelatedDivisionSerializer(many=True, read_only=True)

    class Meta:
        model = Division
        fields = (
            'uid',
            'name',
            'label',
            'short_label',
            'code',
            'level',
            'code_components',
            'postal_code',
            'children',
        )
