import numpy as np
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, HoverTool

from bokeh.models.widgets import Panel, Tabs
from bokeh.io import output_file, show, curdoc
from bokeh.plotting import figure
from bokeh.plotting.helpers import _get_range
from bokeh.themes import Theme

from pyesg.io.reader import PyESGReader

reader = PyESGReader('/users/rajivpatel/Desktop/yomama.pyesg')
sims = reader.get_output_simulations(0)
mean = sims.mean(axis=0)
stdev = np.sqrt(sims.var(axis=0, ddof=1))

times = np.arange(reader.number_of_time_steps)

uci = mean + 1.96 / np.sqrt(reader.number_of_simulations) * stdev
lci = mean - 1.96 / np.sqrt(reader.number_of_simulations) * stdev

data = ColumnDataSource(data={
    'time': times,
    'discounted_tri': mean,
    'upper_ci': uci,
    'lower_ci': lci
})

p1 = figure(toolbar_location=None, height=300, width=600, title="Discounted TRI", x_axis_label='Time(y)')

plot1 = p1.line(x='time', y='discounted_tri', color='black', source=data, legend='Discounted TRI', )
plot2 = p1.line(x='time', y='upper_ci', color='red', source=data, legend='Upper CI')
plot3 = p1.line(x='time', y='lower_ci', color='red', source=data, legend='Lower CI', line_dash='dashed')
p1.legend.location=None
# p1.legend.click_policy='mute'
p1.title.align = 'center'

hover_tool = HoverTool(
    renderers=[plot1],
    tooltips=[
        ('Time (y)', '@time'),
        ('Discounted TRI', '@discounted_tri'),
        ('Upper CI', '@upper_ci'),
        ('Lower CI', '@lower_ci')
    ],
    mode='vline',
)
p1.add_tools(hover_tool)
p1.add_tools(HoverTool(renderers=[plot2, plot3], mode='vline', tooltips=[]))

p1.x_range = _get_range([0, reader.number_of_projection_time_steps])
p1.y_range = _get_range([0.8, 1.2])

theme = Theme(json={
    'attrs': {
        'Figure': {
            'background_fill_color': '#f9f4f4',
            # 'border_fill_color': '#e6e6e6',
            'outline_line_color': '#444444'
        },
        # 'Axis': {
        #     'axis_line_color': "black",
        #     'axis_label_text_color': "black",
        #     'major_label_text_color': "black",
        #     'major_tick_line_color': "black",
        #     'minor_tick_line_color': "black",
        #     },
        'Line': {
            'line_width': 2,
        },
        'Legend': {
            'label_text_font_size': "8pt",
            'background_fill_alpha': 0,
            'border_line_alpha': 0,
            # 'spacing': 0,
        },
        'Circle': {
            'fill_color': 'lightblue',
            'size': 10,
            },
        }
    })

curdoc().theme = theme

output_file('test_graph.html', title='Your mum')
tab = Panel(child=column(row(p1), row(p2)), title='GBP_Equities')
tabs = Tabs(tabs=[tab])
show(tabs)
