{% macro normalize_text(text_column) %}
    -- Convert to lowercase
    lower({{ text_column }}) as normalized_text,
    
    -- Remove punctuation and special characters
    regexp_replace(
        lower({{ text_column }}),
        '[^a-z0-9\s]',
        '',
        'g'
    ) as cleaned_text,
    
    -- Remove extra whitespace
    regexp_replace(
        regexp_replace(
            lower({{ text_column }}),
            '\s+',
            ' ',
            'g'
        ),
        '^\s+|\s+$',
        '',
        'g'
    ) as trimmed_text
{% endmacro %} 