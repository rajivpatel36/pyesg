from bokeh.themes import Theme


REPORT_THEME = Theme(json={
    'attrs': {
        'Figure': {
            'background_fill_color': '#f9f4f4',
            'outline_line_color': '#444444'
        },
        'Line': {
            'line_width': 2,
        },
        'Legend': {
            'label_width': 75,
            'label_text_font_size': "8pt",
            'background_fill_alpha': 0,
            'border_line_alpha': 0,
        },
    }
})
