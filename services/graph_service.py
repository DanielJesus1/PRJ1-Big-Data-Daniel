import base64
from io import BytesIO

from matplotlib.figure import Figure


def count_by_district(records):
    counts = {}
    for record in records:
        district = record["district"]
        counts[district] = counts.get(district, 0) + 1

    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def create_district_chart(records):
    counts = count_by_district(records)
    districts = [district for district, _ in counts]
    values = [count for _, count in counts]

    figure = Figure(figsize=(10, max(4, len(districts) * 0.48)))
    axis = figure.subplots()
    colors = [
        "#a1c9f4", "#ffb482", "#8de5a1", "#ff9f9b", "#d0bbff",
        "#debb9b", "#fab0e4", "#cfcfcf", "#fffea3", "#b9f2f0",
    ]
    bars = axis.barh(
        districts,
        values,
        color=[colors[i % len(colors)] for i in range(len(districts))],
        height=0.68,
    )

    axis.invert_yaxis()
    axis.set_title("Consulados por distrito")
    axis.set_xlabel("Número de consulados")
    axis.set_xlim(0, max(values, default=1) * 1.14)

    for bar, value in zip(bars, values):
        axis.text(value + 0.08, bar.get_y() + bar.get_height() / 2, str(value), va="center")

    figure.tight_layout()
    image_buffer = BytesIO()
    figure.savefig(image_buffer, format="png", bbox_inches="tight")

    return {
        "image": base64.b64encode(image_buffer.getvalue()).decode("ascii"),
        "counts": counts,
    }
