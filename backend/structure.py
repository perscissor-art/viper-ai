from dataclasses import dataclass

@dataclass
class StructurePoint:
    x: int
    y: int
    label: str   # HH HL LH LL


class StructureEngine:

    def __init__(self):
        pass

    # -----------------------------
    # Split highs and lows
    # -----------------------------
    def separate(self, swings):

        highs = []
        lows = []

        for s in swings:

            if s.kind == "HIGH":
                highs.append(s)

            if s.kind == "LOW":
                lows.append(s)

        return highs, lows

    # -----------------------------
    # Label Higher High / Lower High
    # -----------------------------
    def label_highs(self, highs):

        result = []

        if len(highs) < 2:
            return result

        previous = highs[0]

        for current in highs[1:]:

            if current.y < previous.y:

                label = "HH"

            else:

                label = "LH"

            result.append(
                StructurePoint(
                    current.x,
                    current.y,
                    label
                )
            )

            previous = current

        return result

    # -----------------------------
    # Label Higher Low / Lower Low
    # -----------------------------
    def label_lows(self, lows):

        result = []

        if len(lows) < 2:
            return result

        previous = lows[0]

        for current in lows[1:]:

            if current.y < previous.y:

                label = "HL"

            else:

                label = "LL"

            result.append(
                StructurePoint(
                    current.x,
                    current.y,
                    label
                )
            )

            previous = current

        return result

    # -----------------------------
    # Detect BOS
    # -----------------------------
    def detect_bos(self, high_labels):

        if len(high_labels) < 2:
            return False

        last = high_labels[-1]

        return last.label == "HH"

    # -----------------------------
    # Detect CHOCH
    # -----------------------------
    def detect_choch(self, high_labels, low_labels):

        if len(high_labels) < 2:
            return False

        if len(low_labels) < 2:
            return False

        return (
            high_labels[-1].label == "HH"
            and
            low_labels[-1].label == "HL"
        )

    # -----------------------------
    # Build complete structure
    # -----------------------------
    def analyze(self, swings):

        highs, lows = self.separate(swings)

        high_labels = self.label_highs(highs)

        low_labels = self.label_lows(lows)

        bos = self.detect_bos(high_labels)

        choch = self.detect_choch(
            high_labels,
            low_labels
        )

        labels = high_labels + low_labels

        labels.sort(key=lambda p: p.x)

        return {

            "labels": labels,

            "bos": bos,

            "choch": choch

        }