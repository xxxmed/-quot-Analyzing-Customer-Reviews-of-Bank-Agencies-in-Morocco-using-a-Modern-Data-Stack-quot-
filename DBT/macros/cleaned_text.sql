{% macro cleaned_text(text_column) %}
    -- Convert to lowercase, remove special characters and numbers, clean whitespace
    trim(
        regexp_replace(
            regexp_replace(
                lower(coalesce({{ text_column }}, '')),
                '[^a-z\s]',  -- Remove special characters and numbers, keep only letters and spaces
                '',
                'g'
            ),
            '\s+',  -- Clean whitespace
            ' ',
            'g'
        )
    )
{% endmacro %}