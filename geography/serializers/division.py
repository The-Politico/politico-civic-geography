from geography.models import Division

from .child_division import ChildDivisionSerializer


class DivisionSerializer(ChildDivisionSerializer):
    children = ChildDivisionSerializer(many=True, read_only=True)

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
