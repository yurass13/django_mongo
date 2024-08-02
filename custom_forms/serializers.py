from rest_framework import serializers

from .models import CustomForm, FieldTemplate


class FieldTemplateSerializer(serializers.ModelSerializer):
    """Serializer for FieldTemplate."""
    def validate(self, attrs):
        if not isinstance(attrs['f_name'], str):
            raise serializers.ValidationError("Wrong f_name value type!" +
                                              f"\nExpected <str>, but got {type(attrs['f_name'])}")

        if attrs['f_type'] not in FieldTemplate.FieldType.values:
            raise serializers.ValidationError("Unavailable f_type value!" +
                                              f"Expected Literal from {FieldTemplate.FieldType.values}"
                                              f", but got {attrs['f_type']}")

        return attrs

    class Meta:
        model = FieldTemplate
        fields = ('f_name', 'f_type')


class CustomFormSerializer(serializers.ModelSerializer):
    """Serializer for CustomForm."""
    fields = FieldTemplateSerializer(many=True)

    class Meta:
        model = CustomForm
        fields = ('name', 'fields')


