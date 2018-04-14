from bokeh.io import output_file, curdoc, save
from bokeh.models import Tabs

from pyesg.validation.report.page_builder import PageBuilder
from pyesg.validation.report.theme import REPORT_THEME


class ReportBuilder:
    """
    Class for building a report from results.
    """
    def build_report(self, file_path:str, title: str, results: dict) -> None:
        """
        Builds the validation report from validation results and saves it to a file.
        Args:
            file_path: The path of the HTML file to which to save the reports.
            title: The title of the report.
            results: The validation results to use to build the report.

        """
        curdoc().theme = REPORT_THEME
        page_builder = PageBuilder()
        pages = []
        for asset_class_id, asset_class_results in results.items():
            pages.append(page_builder.build_page(asset_class_id, asset_class_results))

        output_file(file_path, title=title)
        tabs = Tabs(tabs=pages)
        save(tabs)
