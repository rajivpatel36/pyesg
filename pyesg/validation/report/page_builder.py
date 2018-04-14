from typing import List

from bokeh.layouts import row, column
from bokeh.models import Panel, Row

from pyesg.validation.report.analysis_builders.builder_factory import get_analysis_builder


class PageBuilder:
    """
    Class for building a page of analyses for an asset class in the validation report.
    """
    def build_analysis(self, analysis_result: dict) -> Row:
        """
        Returns the page row containing the charts for an analysis.
        Args:
            analysis_result: The result of the analysis. It contains the keys:
                'analysis_id', 'result_type', 'results'

        Returns:
            The page row containing the charts for an analysis based on its results.
        """
        analysis_id = analysis_result["analysis_id"]
        builder = get_analysis_builder(analysis_id)
        fig = builder.build_chart(analysis_result["results"])

        # Get row object to add to structure.
        row_to_add = row(*fig) if isinstance(fig, list) else row(fig)
        return row_to_add

    def build_page(self, title: str, page_results: List[dict]) -> Panel:
        """
        Returns a page containing charts for all supplied analysis results.
        Args:
            title: The title for the page
            page_results: A list of the analysis results for the analyses to include on the page

        Returns:
            A Panel object for the page containing charts for all supplied analysis results.
        """
        structure = [self.build_analysis(analysis_result) for analysis_result in page_results]
        return Panel(child=column(*structure), title=title)
