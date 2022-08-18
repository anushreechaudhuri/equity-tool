from fpdf import FPDF
from fpdf import YPos, XPos
from PIL import Image
from datetime import datetime
import pandas as pd

class PDF(FPDF):

    def tract_table(self, dac_select, headings=["Tract ID", "City", "County", "Population", "DAC", "HTC", "State %", "National %", "Energy Burden"], col_widths=(22, 30, 45, 17, 10, 10, 15, 17, 25)):
        # Colors, line width and bold font:
        self.set_fill_color(15, 102, 54)
        self.set_text_color(255)
        self.set_draw_color(15, 102, 54)
        self.set_line_width(0.3)
        self.set_font(style="B", size=8)
        for col_width, heading in zip(col_widths, headings):
            self.multi_cell(col_width, 7, heading, border=1, align="C", fill=True, new_y=YPos.TOP)
        self.ln()
        # Color and font restoration:
        self.set_fill_color(224, 235, 255)
        self.set_text_color(0)
        self.set_font()
        fill = False
        for _, tract in dac_select.sort_values(by=["avg_energy_burden_natl_pctile"],ascending=False).iterrows():
            self.cell(col_widths[0], 6, tract["GEOID"], border="LR", align="C", fill=fill, new_y=YPos.TOP)
            try:
                self.cell(col_widths[1], 6, tract["city"], border="LR", align="C", fill=fill, new_y=YPos.TOP)
            except:
                self.cell(col_widths[1], 6, "", border="LR", align="C", fill=fill, new_y=YPos.TOP)
            self.cell(col_widths[2], 6, tract["county_name"], border="LR", align="C", fill=fill, new_y=YPos.TOP)
            self.cell(col_widths[3], 6, str(tract['population']), border="LR", align="C", fill=fill, new_y=YPos.TOP)
            self.cell(col_widths[4], 6, tract['DAC_check'], border="LR", align="C", fill=fill, new_y=YPos.TOP)
            self.cell(col_widths[5], 6, tract['QCT_check'], border="LR", align="C", fill=fill, new_y=YPos.TOP)
            self.cell(col_widths[6], 6, str(tract['tract_state_percentile']), border="LR", align="C", fill=fill, new_y=YPos.TOP)
            self.cell(col_widths[7], 6, str(tract['tract_national_percentile']), border="LR", align="C", fill=fill, new_y=YPos.TOP)
            self.cell(col_widths[8], 6, str(tract["avg_energy_burden_natl_pctile"]), border="LR", align="C", fill=fill, new_y=YPos.TOP)
            self.ln()
            fill = not fill
        self.cell(sum(col_widths), 0, "", "T")



def generate_pdf(shape,
                 map,
                 dac_select,
                 nhpd_select,
                 detailed,
                 out_path="out.pdf"):
    pdf = PDF(format="letter")
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(15, 102, 54)
    pdf.cell(
        w=0,
        h=10,
        txt=
        f'NBUC Equity Tool Report: {(datetime.now().strftime("%m-%d-%Y %H:%M:%S"))}',
        border=0,
        fill=True,
        align='C')
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0)
    pdf.cell(w=0,
             h=10,
             txt=f'Selected Boundary: {shape["NAME"].iloc[0]}',
             border=0,
             fill=False,
             align='C')
    pdf.ln(10)
    pdf.image(map, w=100, h=75, x=pdf.w / 4)
    pdf.ln(10)
    pdf.set_x(0)
    prev_y = pdf.get_y()
    pdf.multi_cell(
        w=70,
        h=10,
        txt=f'{len(dac_select[dac_select["DAC_status"]=="Disadvantaged"])} \n Disadvantaged \n Census Tracts',
        markdown=True, align='C', new_y=YPos.TOP)
    pdf.set_x(70)
    pdf.multi_cell(w=70, h=10, txt=f'{len(nhpd_select)} \n Affordable \n Housing Properties', align='C', new_y=YPos.TOP)
    pdf.set_x(140)
    pdf.multi_cell(w=70,
             h=10,
             txt=f'{dac_select["avg_energy_burden_natl_pctile"].mean():.2f} \n Avg. Energy \n Burden %', align='C',new_y=YPos.TOP)
    pdf.ln(40)
    pdf.set_x(0)
    pdf.multi_cell(w=70,
             h=10,
             txt=f'{len(dac_select[dac_select["QCT_status"]=="Eligible"])} \n Housing Tax Credit \n Eligible Tracts', align='C', new_y=YPos.TOP)
    pdf.set_x(70)
    pdf.multi_cell(w=70, h=10, txt=f'{int(nhpd_select["Assisted Units"].sum())} \n Total \n Housing Units', align='C', new_y=YPos.TOP)
    pdf.set_x(140)
    pdf.multi_cell(w=70,
             h=10,
             txt=f'{dac_select["nonwhite_pct_natl_pctile"].mean():.2f} \n Avg. Nonwhite \n Percentile', align='C', new_y=YPos.TOP)
    pdf.ln(40)
    pdf.set_text_color(255)
    pdf.set_x(70)
    pdf.cell(w=70, h=10, txt='Download Data Definitions', border=0, fill=True, align='C', link='https://docs.google.com/spreadsheets/d/1zigWKMy4_WLyaB46iqG4185vPi85wCZeDSc4fvQE5tI/edit?usp=sharing')
    pdf.add_page()
    pdf.tract_table(dac_select)
    pdf.output(out_path)


if __name__ == "__main__":
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

    generate_pdf(shape,
                 "streamlit/fig.png",
                 dac_select,
                 nhpd_select,
                 detailed=False,
                 out_path="out.pdf")
