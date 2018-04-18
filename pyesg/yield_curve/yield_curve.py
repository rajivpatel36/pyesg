import bisect

from typing import Dict, List


class YieldCurve:
    """
    Class for specifying and extracting rates from a yield curve including interpolation of unspecified points.
    """
    def __init__(self):
        # Set so that term 0 gives rate = 0
        self._mapping = {0: 0}  # type: Dict[float, float]
        self._terms = []  # type: List[float]
        self._rates = []  # type: List[float]
        self._is_sorted = False
        self._max_term = None
        self._min_term = None

    def _resort_terms_and_rates(self) -> None:
        """
        Resorts the self._terms and self._rates list.
        """
        self._terms = sorted(self._mapping)
        self._rates = [self._mapping[term] for term in self._terms]
        self._min_term = self._terms[0]
        self._max_term = self._terms[-1]
        self._is_sorted = True

    def add_point(self, term: float, rate: float) -> None:
        """
        Adds a point to the yield curve.
        Args:
            term: The term of the point.
            rate: The continuously compounded spot rate of the point.
        """
        self._mapping[term] = rate
        self._is_sorted = False

    def get_rate(self, term: float) -> float:
        """
        Returns a rate with the specified term. If the term does not exist, interpolation between points is attempted.
        Args:
            term: The term of the point on the yield curve.

        Returns:
            The continuously compounded spot rate for the specified term.
        """
        if term < 0:
            raise ValueError("A negative term cannot be used.")

        # Get rate if it's already been specified.
        rate = self._mapping.get(term)

        if not self._is_sorted:
            self._resort_terms_and_rates()

        # Can't find rate so need to interpolate with what we've got
        if not self._terms:
            raise ValueError("No terms and rates specified that can be used for interpolation in the yield curve.")

        if term > self._max_term:
            raise ValueError("The specified term exceeds the maximum term in the yield curve. Interpolation cannot"
                             "be carried out.")

        if term < self._min_term:
            raise ValueError("The specified term is below the minimum term in the yield curve. Interpolation cannot"
                             "be carried out.")

        # Look up the index in self._terms and self._rates for the first term immediately AFTER the specified term.
        index_after = bisect.bisect_left(self._terms, term)
        term_after = self._terms[index_after]
        term_before = self._terms[index_after - 1]
        rate_after = self._rates[index_after]
        rate_before = self._rates[index_after - 1]

        # interpolate
        return rate_before + (term - term_before) / (term_after - term_before) * (rate_after - rate_before)
