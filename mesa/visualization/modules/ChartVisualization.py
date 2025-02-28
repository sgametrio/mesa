# -*- coding: utf-8 -*-
"""
Chart Module
============

Module for drawing live-updating line charts using Charts.js

"""
import json
from mesa.visualization.ModularVisualization import VisualizationElement


class ChartModule(VisualizationElement):
    """ Each chart can visualize one or more model-level series as lines
     with the data value on the Y axis and the step number as the X axis.

    At the moment, each call to the render method returns a list of the most
    recent values of each series.

    Attributes:
        series: A list of dictionaries containing information on series to
                plot. Each dictionary must contain (at least) the "Label" and
                "Color" keys. The "Label" value must correspond to a
                model-level series collected by the model's DataCollector, and
                "Color" must have a valid HTML color.
        canvas_height, canvas_width: The width and height to draw the chart on
                                     the page, in pixels. Default to 200 x 500
        data_collector_name: Name of the DataCollector object in the model to
                             retrieve data from.
        template: "chart_module.html" stores the HTML template for the module.


    Example:
        schelling_chart = ChartModule([{"Label": "happy", "Color": "Black"}],
                                      data_collector_name="datacollector")

    TODO:
        Have it be able to handle agent-level variables as well.

        More Pythonic customization; in particular, have both series-level and
        chart-level options settable in Python, and passed to the front-end
        the same way that "Color" is currently.

    """
    package_includes = ["Chart.min.js", "ChartModule.js"]

    def __init__(self, series, scope="model", canvas_height=200, canvas_width=500,
                 data_collector_name="datacollector"):
        """
        Create a new line chart visualization.

        Args:
            series: A list of dictionaries containing series names and
                    HTML colors to chart them in, e.g.
                    [{"Label": "happy", "Color": "Black"},]
            canvas_height, canvas_width: Size in pixels of the chart to draw.
            data_collector_name: Name of the DataCollector to use.
        """

        self.scope = scope
        self.series = series
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.data_collector_name = data_collector_name

        series_json = json.dumps(self.series)
        new_element = "new ChartModule({}, {},  {})"
        new_element = new_element.format(series_json, canvas_width,
                                         canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        current_values = []
        data_collector = getattr(model, self.data_collector_name)

        if self.scope == "model":
            for s in self.series:
                name = s["Label"]
                try:
                    val = data_collector.model_vars[name][-1]  # Latest value
                except (IndexError, KeyError):
                    val = 0
                current_values.append(val)
        
        elif self.scope == "agent":
            df = data_collector.get_agent_vars_dataframe().astype('float')
            print(df.to_string())
            try:
                latest_step = df.index.levels[0][-1]
                labelStrings = [s['Label'] for s in self.series]
                dictionary = df.loc[latest_step].T.loc[labelStrings].to_dict()
                current_values = list(dictionary.values())
            except:
                current_values = []
        else:
            raise ValueError("scope must be 'agent' or 'model'")
        return current_values
