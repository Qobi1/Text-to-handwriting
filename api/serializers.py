from rest_framework import serializers
from django.core.validators import RegexValidator


class TextToHandwritingSerializer(serializers.Serializer):
    text = serializers.CharField()
    ink_color = serializers.CharField(
        max_length=7,
        validators=[RegexValidator(regex=r"^#(?:[0-9a-fA-F]{3}){1,2}$", message="Invalid color format. Use #RRGGBB.")],
        allow_null=True,
        allow_blank=True,
        required=False
    )
    x_offset = serializers.IntegerField(allow_null=True, required=False)
    word_spacing = serializers.IntegerField(allow_null=True, required=False)
    font = serializers.CharField(required=False)
    is_image = serializers.BooleanField(default=True)
    font_size = serializers.IntegerField(required=False)
    line_spacing = serializers.IntegerField(required=False)

    def validate_font(self, value):
        fonts = {
            'handwriting_1': 'handwriting_1.ttf',
            'handwriting_2': 'handwriting_2.ttf',
            'handwriting_3': 'handwriting_3.ttf',
            'handwriting_4': 'handwriting_4.ttf',
            'handwriting_5': 'handwriting_5.ttf',
            'handwriting_6': 'handwriting_6.ttf',
            'handwriting_7': 'handwriting_7.ttf',
            'handwriting_8': 'handwriting_7.ttf',
            'handwriting_9': 'handwriting_9.ttf',
            'handwriting_10': 'handwriting_10.ttf',
            'handwriting_11': 'handwriting_11.ttf',
            'handwriting_12': 'handwriting_12.ttf',
            'handwriting_13': 'handwriting_13.ttf',
            'handwriting_14': 'handwriting_14.ttf',
            'handwriting_15': 'handwriting_15.ttf',
            'handwriting_16': 'handwriting_16.ttf',
            'handwriting_17': 'handwriting_17.ttf',
            'handwriting_18': 'handwriting_18.ttf',
        }
        if value not in fonts.keys():
            raise serializers.ValidationError(
                """Choose one of the current options: handwriting_1, handwriting_2, handwriting_3, handwriting_4, handwriting_5, handwriting_6, handwriting_7, handwriting_8, handwriting_9, handwriting_10, handwriting_11, handwriting_12, handwriting_13, handwriting_14, handwriting_15, handwriting_16, handwriting_17, handwriting_18""")

        return fonts[value]


class ConvertImageToPdfSerializer(serializers.Serializer):
    image_files = serializers.ListField(
        child=serializers.CharField(),  # Each item in the list should be a string (image path)
        allow_empty=False  # Prevent empty lists if necessary
    )

