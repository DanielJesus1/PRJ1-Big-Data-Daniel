from flask import Flask, render_template, request

from services.data_service import get_countries, get_districts, load_consulates
from services.graph_service import create_district_chart

app = Flask(__name__)


@app.route("/")
def dashboard():
    consulates = load_consulates()
    country = request.args.get("country", "").strip()
    district = request.args.get("district", "").strip()
    filtered = [
        item for item in consulates
        if (not country or item["country"] == country)
        and (not district or item["district"] == district)
    ]

    return render_template(
        "dashboard.html",
        consulates=filtered,
        countries=get_countries(consulates),
        districts=get_districts(consulates),
        selected_country=country,
        selected_district=district,
    )


@app.route("/grafica")
def graph():
    consulates = load_consulates()
    chart_data = create_district_chart(consulates)
    return render_template(
        "grafica.html",
        chart_image=chart_data["image"],
        district_count=len(chart_data["counts"]),
        total=len(consulates),
    )


if __name__ == "__main__":
    app.run(debug=True)
