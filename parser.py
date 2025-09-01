import re


class ProgressParser:
    re_percentage = re.compile(r'(\d+\.\d)\%')
    re_eta = re.compile(r'ETA\s([\d\:]+)\s')

    def parse(self, buf: str) -> (int, str):
        print(f"Attempt to parse: {buf}")
        match_eta = self.re_eta.search(buf)
        match_percentage = self.re_percentage.search(buf)
        if match_percentage is None:
            return (None, None)
        print(f"Match: {match_percentage.group(1)}")
        percentage = float(match_percentage.group(1))
        percentage = int(round(percentage))
        print(f"Percentage = {percentage}")

        if match_eta is None:
            return (percentage, None)

        print(f"Match: {match_eta.group(1)}")
        return (percentage, match_eta.group(1))
