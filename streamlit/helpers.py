import pandas as pd
from datetime import datetime
import base64
import pdfkit
import numpy as np


def percent_bar(value):
    try:
        return round(0.93 * value)
    except:
        return 0


def highlight(value):
    try:
        value = float(value)
        if value > 50:
            return "bad"
    except ValueError:
        if value == "Eligible" or value == "Disadvantaged":
            return "bad"
    return "good"


def color_bar(value):
    if value > 50:
        return "bad-bar"
    return "good-bar"


def zoom_center(
    lons: tuple = None,
    lats: tuple = None,
    lonlats: tuple = None,
    format: str = "lonlat",
    projection: str = "mercator",
    width_to_height: float = 2.0,
):
    """Finds optimal zoom and centering for a plotly mapbox.
    Must be passed (lons & lats) or lonlats.
    Temporary solution awaiting official implementation, see:
    https://github.com/plotly/plotly.js/issues/3434

    Parameters
    --------
    lons: tuple, optional, longitude component of each location
    lats: tuple, optional, latitude component of each location
    lonlats: tuple, optional, gps locations
    format: str, specifying the order of longitud and latitude dimensions,
        expected values: 'lonlat' or 'latlon', only used if passed lonlats
    projection: str, only accepting 'mercator' at the moment,
        raises `NotImplementedError` if other is passed
    width_to_height: float, expected ratio of final graph's with to height,
        used to select the constrained axis.

    Returns
    --------
    zoom: float, from 1 to 20
    center: dict, gps position with 'lon' and 'lat' keys

    >>> print(zoom_center((-109.031387, -103.385460),
    ...     (25.587101, 31.784620)))
    (5.75, {'lon': -106.208423, 'lat': 28.685861})
    """
    if lons is None and lats is None:
        if isinstance(lonlats, tuple):
            lons, lats = zip(*lonlats)
        else:
            raise ValueError("Must pass lons & lats or lonlats")

    maxlon, minlon = max(lons), min(lons)
    maxlat, minlat = max(lats), min(lats)
    center = {
        "lon": round((maxlon + minlon) / 2, 6),
        "lat": round((maxlat + minlat) / 2, 6),
    }

    # longitudinal range by zoom level (20 to 1)
    # in degrees, if centered at equator
    lon_zoom_range = np.array([
        0.0007,
        0.0014,
        0.003,
        0.006,
        0.012,
        0.024,
        0.048,
        0.096,
        0.192,
        0.3712,
        0.768,
        1.536,
        3.072,
        6.144,
        11.8784,
        23.7568,
        47.5136,
        98.304,
        190.0544,
        360.0,
    ])

    if projection == "mercator":
        margin = 1.2
        height = (maxlat - minlat) * margin * width_to_height
        width = (maxlon - minlon) * margin
        lon_zoom = np.interp(width, lon_zoom_range, range(20, 0, -1))
        lat_zoom = np.interp(height, lon_zoom_range, range(20, 0, -1))
        zoom = round(min(lon_zoom, lat_zoom), 2)
    else:
        raise NotImplementedError(
            f"{projection} projection is not implemented")

    return zoom, center


def generate_from_data(shape,
                       map,
                       dac_select,
                       nhpd_select,
                       detailed,
                       out_path="out.pdf"):
    if detailed:
        tracts_html = "\n".join([
            f"""
            <section class="break-before">
            <div class="h-8 w-full">&nbsp;</div>
            <div class="font-bold text-xl text-white bg-[#00583C] p-2 w-80">Census Tract {tract['GEOID']}</div>
            <div class="text-lg mt-2">
                <div class="inline-block align-top mr-8">
                <b>City:</b> {tract['city']}</br>
                <b>County:</b> {tract['county_name']}</br>
                <b>State:</b> {tract['county_name'][-2:]}</br>
                <b>Population:</b> {tract['population']} </br>
                </div>
                <div class="inline-block align-top">
                <b>DAC Status:</b> <mark class="{highlight(tract['DAC_status'])}">{tract['DAC_status']}</mark></br>
                <b>QCT Status:</b> <mark class="{highlight(tract['QCT_status'])}">{tract['QCT_status']}</mark></br>
                <b>State Ranking:</b> <mark class="{highlight(tract['tract_state_percentile'])}">{tract['tract_state_percentile']}</mark> </br>
                <b>National Ranking:</b> <mark class="{highlight(tract['tract_national_percentile'])}">{tract['tract_national_percentile']}</mark> </br>
                </div>
            </p>
            <table class="mt-4">
                <tr>
                <th>Indicator</th>
                <th class="w-[70%]">Percentile</th>
                </tr>
                <tr>
                <td>Energy Burden</td>
                <td>
                    <div class="{color_bar(tract["avg_energy_burden_natl_pctile"])}" style="width: {percent_bar(tract["avg_energy_burden_natl_pctile"])}%"></div>
                    <div class="inline-block align-middle">{tract["avg_energy_burden_natl_pctile"]}</div>
                </td>
                </tr>
                <tr>
                <td>Housing Burden</td>
                <td>
                    <div class="{color_bar(tract["avg_housing_burden_natl_pctile"])}" style="width: {percent_bar(tract["avg_housing_burden_natl_pctile"])}%"></div>
                    <div class="inline-block align-middle">{tract["avg_housing_burden_natl_pctile"]}</div>
                </td>
                </tr>
                    <tr>
                <td>Transport Burden</td>
                <td>
                    <div class="{color_bar(tract["avg_transport_burden_natl_pctile"])}" style="width: {percent_bar(tract["avg_transport_burden_natl_pctile"])}%"></div>
                    <div class="inline-block align-middle">{tract["avg_transport_burden_natl_pctile"]}</div>
                </td>
                </tr>
                <tr>
                <td>Low Income (AMI)</td>
                <td>
                    <div class="{color_bar(tract["lowincome_ami_pct_natl_pctile"])}" style="width: {percent_bar(tract["lowincome_ami_pct_natl_pctile"])}%"></div>
                    <div class="inline-block align-middle">{tract["lowincome_ami_pct_natl_pctile"]}</div>
                </td>
                </tr>
                <tr>
                <td>Nonwhite Population</td>
                <td>
                    <div class="{color_bar(tract["nonwhite_pct_natl_pctile"])}" style="width: {percent_bar(tract["nonwhite_pct_natl_pctile"])}%"></div>
                    <div class="inline-block align-middle">{tract["nonwhite_pct_natl_pctile"]}</div>
                </td>
                </tr>
                <tr>
                <td>Incomplete Plumbing</td>
                <td>
                    <div class="{color_bar(tract["incomplete_plumbing_pct_natl_pctile"])}" style="width: {percent_bar(tract["incomplete_plumbing_pct_natl_pctile"])}%"></div>
                    <div class="inline-block align-middle">{tract["incomplete_plumbing_pct_natl_pctile"]}</div>
                </td>
                </tr>
                <td>Lead Paint</td>
                <td>
                    <div class="{color_bar(tract["lead_paint_pct_natl_pctile"])}" style="width: {percent_bar(tract["lead_paint_pct_natl_pctile"])}%"></div>
                    <div class="inline-block align-middle">{tract["lead_paint_pct_natl_pctile"]}</div>
                </td>
                </tr>
                <td>Non-Grid Heating</td>
                <td>
                    <div class="{color_bar(tract["nongrid_heat_pct_natl_pctile"])}" style="width: {percent_bar(tract["nongrid_heat_pct_natl_pctile"])}%"></div>
                    <div class="inline-block align-middle">{tract["nongrid_heat_pct_natl_pctile"]}</div>
                </td>
                </tr>
            </table>
            </p>
            </section>
            """ for _, tract in
            dac_select.sort_values(by=["avg_energy_burden_natl_pctile"],
                                   ascending=False).iterrows()
        ])

    else:
        tracts_html = "\n".join([
            f"""
            <section class="break-before">
            <div class="h-8 w-full">&nbsp;</div>
            <div class="font-bold text-xl text-white bg-[#00583C] p-2 w-80">Census Tract {tract['GEOID']}</div>
            <div class="text-lg mt-2">
                <div class="inline-block align-top mr-8">
                <b>City:</b> {tract['city']}</br>
                <b>County:</b> {tract['county_name']}</br>
                <b>Energy Burden:</b> {tract["avg_energy_burden_natl_pctile"]}</br>
                <b>Population:</b> {tract['population']} </br>
                </div>
                <div class="inline-block align-top">
                <b>DAC Status:</b> <mark class="{highlight(tract['DAC_status'])}">{tract['DAC_status']}</mark></br>
                <b>QCT Status:</b> <mark class="{highlight(tract['QCT_status'])}">{tract['QCT_status']}</mark></br>
                <b>State Ranking:</b> <mark class="{highlight(tract['tract_state_percentile'])}">{tract['tract_state_percentile']}</mark> </br>
                <b>National Ranking:</b> <mark class="{highlight(tract['tract_national_percentile'])}">{tract['tract_national_percentile']}</mark> </br>
                </div>
            </section>
            """ for _, tract in
            dac_select.sort_values(by=["avg_energy_burden_natl_pctile"],
                                   ascending=False).iterrows()
        ])

    nhpd_html = "\n".join([
        f"""
        <section class="break-before">
        <div class="h-8 w-full">&nbsp;</div>
        <div class="font-bold text-xl text-white bg-[#69BE28] p-2 w-full mt-8">Property: {property["Property Name"]}</div>
        <div class="text-lg mt-2">
            <div class="inline-block align-top mr-8">
            <b>Street Address:</b> {property["Street Address"]}</br>
            <b>City:</b> {property["City"]}</br>
            <b>State:</b> {property["State"]}</br>
            <b>Zip Code:</b> {property["Zip Code"]}</br>
            <b>Subsidy:</b> {str(property["Subsidy Name"]) + ", " + str(property["Subsidy Subname"])}</br>
            <b>Owner Name:</b> {property["Owner Name"]} </br>
            <b>Rent to FMR Ratio:</b> {property["Rent to FMR Ratio"]} </br>
            </div>
            <div class="inline-block align-top">
            <b>Known Total Units:</b> {property["Known Total Units"]}</br>
            <b>Assisted Units:</b> {property["Assisted Units"]}</br>
            <b>Earliest Construction Date:</b> {property["Earliest Construction Date"]}</br>
            <b>Latest Construction Date:</b> {property["Latest Construction Date"]} </br>
            <b>Subsidy Start Date:</b> {property["Start Date"]} </br>
            <b>Subsidy End Date:</b> {property["End Date"]} </br>
            </div>
        </p>
        </section>
        """ for _, property in nhpd_select.iterrows()
    ])

    with open("simple-styles.css", "r") as f:
        style = f.read()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <script src="https://cdn.plot.ly/plotly-2.12.1.min.js"></script>
        <style>
        {style}
        </style>
    </head>
    <body class="w-screen">
        <div class="w-full h-fit bg-[#00583C] p-2 px-4 relative">
            <h1 class="text-white font-bold block text-2xl">NBUC Equity Tool Report</h1>
            <h1 class="text-white font-bold block text-lg absolute top-0 pt-2.5" style="right: 0px; width: 190px;">
                {datetime.now().strftime("%m/%d/%Y %H:%M:%S")}
            </h1>
        </div>
        <div class="w-full px-14">
            <section id="main-area " class="w-full h-fit mt-8 text-center">
                <p class="mb-2">
                    <a class="text-black text-xl"><b>Selected Boundary:</b> {shape.iloc[0]["NAME"]}</a
            >
        </p>
        {map}
        <div class="mt-8 w-full h-fit align-top">
            <div class="w-[32%] inline-block">
            <h1 class="font-bold text-4xl"> {len(dac_select[dac_select["DAC_status"]=="Disadvantaged"])} </h1>
            <h1 class="font-semibold leading-tight text-lg">Total </br>  DAC Census Tracts</h1>
            </div>
            <div class="w-[32%] h-full inline-block align-top">
            <h1 class="font-bold text-4xl">{len(nhpd_select)}</h1>
            <h1 class="font-semibold leading-tight text-lg">Subsidized Affordable </br>  Housing Properties</h1>
            </div>
            <div class="w-[32%] inline-block align-top">
            <h1 class="font-bold text-4xl">{dac_select['avg_energy_burden_natl_pctile'].mean():.2f}</h1>
            <h1 class="font-semibold leading-tight text-lg break-words">Average Energy </br> Burden Percentile</h1>
            </div>
        </div>
        <div class="mt-8 w-full h-fit align-top">
            <div class="w-[32%] inline-block">
            <h1 class="font-bold text-4xl"> {len(dac_select[dac_select["QCT_status"]=="Eligible"])} </h1>
            <h1 class="font-semibold leading-tight text-lg">Total Housing Tax Credit </br>   Eligible Census Tracts</h1>
            </div>
            <div class="w-[32%] h-full inline-block align-top">
            <h1 class="font-bold text-4xl">{int(nhpd_select['Assisted Units'].sum())}</h1>
            <h1 class="font-semibold leading-tight text-lg">Total </br>  Assisted Units</h1>
            </div>
            <div class="w-[32%] inline-block align-top">
            <h1 class="font-bold text-4xl">{dac_select['nonwhite_pct_natl_pctile'].mean():.2f}</h1>
            <h1 class="font-semibold leading-tight text-lg break-words">Average Nonwhite </br> Population Percentile</h1>
            </div>
        </div>
        </section>
        {tracts_html}
        {nhpd_html}

    </div>
    </body>
    </html>
    """

    options = {
        "enable-local-file-access": None,
        "margin-top": "0in",
        "margin-right": "0in",
        "margin-bottom": "0in",
        "margin-left": "0in",
    }

    # with open("out.html", "w") as f:
    #     f.write(html)

    # subprocess.call(
    #     ["lessc", "templates/compiled-styles.css", "templates/simple-styles.css"]
    # )
    pdfkit.from_string(html,
                       out_path,
                       options=options,
                       css="simple-styles.css")


if __name__ == "__main__":
    # TESTING DATA
    shape = pd.DataFrame({
        "NAME": ["San Diego County"],
    })

    dac_select = pd.DataFrame({
        "GEOID": ["012345678910"],
        "city": ["San Diego"],
        "county_name": ["San Diego"],
        "population": [4444.22],
        "DAC_status": ["Disadvantaged"],
        "QCT_status": ["Not Eligible"],
        "lead_paint_pct_natl_pctile": [78.81],
        "avg_energy_burden_natl_pctile": [11.11],
        "avg_housing_burden_natl_pctile": [50],
        "avg_transport_burden_natl_pctile": [55.53],
        "incomplete_plumbing_pct_natl_pctile": [0.0],
        "lowincome_ami_pct_natl_pctile": [23.1],
        "nongrid_heat_pct_natl_pctile": [100.00],
        "nonwhite_pct_natl_pctile": [35.4],
        "tract_national_percentile": [0.0],
        "tract_state_percentile": [100.00],
    })

    for col in dac_select.columns:
        if "pctile" in col or "percentile" in col:
            dac_select[col + "_bars"] = round(0.93 * dac_select[col])

    nhpd_select = pd.DataFrame({
        "Property Name": ["Lone Bluffs"],
        "Street Address": ["14230 San Diego Ave"],
        "City": ["San Diego"],
        "County": ["San Diego"],
        "State": ["CA"],
        "Start Date": ["2019-01-01"],
        "End Date": ["2019-02-01"],
        "Earliest Construction Date": ["2019-01-01"],
        "Latest Construction Date": ["2019-02-01"],
        "Rent to FMR Ratio": [1],
        "Subsidy Name": ["Section 8"],
        "Subsidy Subname": ["PRAC"],
        "Owner Name": ["Happy Villages Apartments"],
        "Known Total Units": [50],
        "Assisted Units": [15],
        "Zip Code": ["92129"],
    })
    image = {}

    with open("fig.png", "rb") as f:
        encoded_string = base64.b64encode(f.read())
        image["map"] = encoded_string.decode("utf-8")
        image[
            "map"] = '<img src="data:image/png;base64,{0}" class="w-full h-auto">'.format(
                image["map"])
