import re


class ProgressParser:
    re_percentage = re.compile(r'(\d+\.\d)\%')
    re_eta = re.compile(r'ETA\s([\d\:]+)\s')

    def parse(self, buf: str) -> (int, str):
        match_eta = self.re_eta.search(buf)
        match_percentage = self.re_percentage.search(buf)
        if match_percentage is None:
            return (None, None)
        percentage = float(match_percentage.group(1))
        percentage = int(round(percentage))

        if match_eta is None:
            return (percentage, None)

        return (percentage, match_eta.group(1))
