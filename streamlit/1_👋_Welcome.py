import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Welcome",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        'Get Help':
        'https://www.energy.gov/eere/buildings/building-technologies-office',
        'Report a bug': "https://github.com/anushreechaudhuri/equity-tool",
        'About': "### National Building Upgrade Challenge Equity Tool"
    })
# Read Excel File with data definitions, first sheet
dac_def = pd.read_excel("data_definitions.xlsx",
                        sheet_name="CensusTracts",
                        index_col=False)
nhpd_def = pd.read_excel("data_definitions.xlsx",
                         sheet_name="NHPD",
                         index_col=False)
# Begin Pasting Page Content Here

welcome_tab, faq_tab, viz_tab, report_tab = st.tabs(["๐ Welcome", "โน๏ธ FAQ", "How-To: ๐บ Visualize", "How-To: ๐ Report"])

with welcome_tab:
    st.title("Welcome to the Building Upgrade Equity Tool!")

    st.markdown("This tool is designed to help you visualize and identify the most burdened parts of your community. By drawing on data from the National Housing Preservation Database and the U.S. Department of Energyโs Justice40 Initiative, both individual buildings and entire neighborhoods are highlighted as potential candidates for equitable building decarbonization investments.")

    st.markdown("In [**๐บ Visualize**](%EF%B8%8F_Visualize#explore-a-national-map), the tool presents an interactive national map that allows you to explore areas of interest by zooming, filtering, and searching. After identifying areas that youโd like a closer look at, the [**๐ Report**](Report#generate-a-report-for-your-location) feature generates a detailed overview of every census tract and affordable housing property in the area you select.")

    st.markdown("Click on the other tabs on this page to learn more about the tool and how to use it! For information about data sources, check out the [**๐ก Sources**](Sources#data-sources) section.")

with faq_tab:
    st.header("โน๏ธ Frequently Asked Questions")

    with st.expander("What is the Justice40 Initiative? What is the National Housing Preservation Database?"):
        st.markdown("The [Justice40 Initiative](https://www.whitehouse.gov/environmentaljustice/justice40/) is a cross-agency federal commitment to direct at least 40% of federal investments in areas like clean energy and energy efficiency; clean transit; affordable and sustainable housing; training and workforce development; the remediation and reduction of legacy pollution; and the development of clean water infrastructure to Disadvantaged Communities (DACs). The Initiative stems from President Bidenโs Executive Order 14008, Tackling the Climate Crisis at Home and Abroad. The National Building Upgrade Challenge is a Justice40 covered program and is committed to ensuring equitable investment and access to building electrification.")
        st.markdown("The [National Housing Preservation Database (NHPD)](https://preservationdatabase.org/) is an address-level inventory of federally assisted rental housing in the U.S. The data originates from the [US Department of Housing and Urban Development (HUD)](https://www.hud.gov/) and the [US Department of Agriculture (USDA)](https://www.usda.gov/), and it includes ten federally subsidized programs as well as state and local subsidies from Connecticut, Florida, and Massachusetts. The NHPD was created by the [Public and Affordable Housing Research Corporation (PAHRC)](https://www.pahrc.org/) and the [National Low Income Housing Coalition (NLIHC)](https://nlihc.org/) in 2011 to provide communities with the information they need to effectively preserve their stock of public and affordable housing.")
    with st.expander("What is a census tract?"):
        st.markdown("The census tract is the smallest unit of geography for which consistent data can be displayed on the map. The tool uses census tracts that can vary widely in area but represent about 4,000 people each.")
    with st.expander("What does it mean to be a โDisadvantagedโ census tract?"):
        st.markdown("According to the [Department of Energy (DOE) website](https://www.energy.gov/diversity/justice40-initiative), the DOEโs working definition of โDisadvantagedโ is based on cumulative burden and includes data for thirty six (36) burden indicators collected at the census tract level. These burden indicators can be grouped across the following four categories (the numbers in parenthesis are the number of indicators in each category):")
        st.markdown("* Fossil Dependence (2)")
        st.markdown("* Energy Burden (5)")
        st.markdown("* Environmental and Climate Hazards (10)")
        st.markdown("* Socio-economic Vulnerabilities (19)")
        st.markdown("The 36 burden indicators were selected based on extensive stakeholder outreach, consultation of similar energy justice programs, and recommendations from the White House Environmental Justice Advisory Council. To be considered โDisadvantaged,โ a census tract must rank in the 80th percentile of the cumulative sum of the 36 burden indicators and have at least 30% of households classified as low-income. **Nationwide, 13,581 census tracts were identified as DACs using this methodology (18.6% of 73,056 total U.S. census tracts). Additionally, federally recognized tribal lands and U.S. territories, in their entirety, are categorized as โDisadvantaged.โ**")
    with st.expander("What does it mean to be โEligibleโ for the Housing Tax Credit?"):
        st.markdown("Census tracts that are identified as โEligibleโ for the Housing Tax Credit, also known as [โLow-Income Housing Tax Credit Qualified Census Tracts,โ](https://www.huduser.gov/portal/datasets/qct.html) must have 50 percent of households with incomes below 60 percent of the Area Median Gross Income (AMGI) or have a poverty rate of 25 percent or more. This is a general indicator of geographic areas with *naturally occuring* affordable housing and historically low-to-moderate income populations. The Department of Housing and Urban Development uses the definition of a โQualified Census Tractโ to prioritize subsidies for affordable housing projects in the identified areas.")
    with st.expander("What is Energy Burden?"):
        st.markdown("Energy Burden is a simple ratio based on average annual housing energy costs divided by the average annual household income. So if two census tracts have the *same* annual housing income but one area has *higher* annual housing energy costs, then that area will have a *higher* energy burden. The measure is sourced from the Department of Energyโs [Low-Income Energy Affordability Data (LEAD) Tool](https://www.energy.gov/eere/slsc/low-income-energy-affordability-data-lead-tool), which draws on the U.S. Census Bureauโs American Community Survey 2018 Public Use Microdata Samples.")
    with st.expander("Why are Energy Burden and other indicators reported as percentiles?"):
        st.markdown("The tool ranks each census tract using percentiles that show how much burden each tract experiences relative to all other tracts in the nation, for each indicator. For example, if a tract has a 60% Energy Burden percentile, then 60% of the nationโs census tracts have *less* Energy Burden and 40% of the nationโs census tracts have *more* Energy Burden.")
    with st.expander("What do the other indicators in the tool represent?"):
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(label="Download Census Tract Definitions", data=dac_def.to_csv(index=False))
            st.dataframe(dac_def)
        with col2:
            st.download_button(label="Download NHPD Definitions", data=nhpd_def.to_csv(index=False))
            st.dataframe(nhpd_def)
    with st.expander("What about U.S. Tribal Lands and Territories?"):
        st.markdown("According to the [DOE website](https://www.energy.gov/diversity/justice40-initiative), federally recognized tribal lands and U.S. territories are categorized as Disadvantaged in accordance with White House Office of Management Budgetโs Interim Guidance โcommon conditionsโ definition of community. Tribal lands are defined from census boundaries for American Indian/Alaska Native/Native Hawaiian lands (U.S. Census Bureau, 2021). U.S. territories include Puerto Rico, Guam, American Samoa, Virgin Islands, and Northern Marianas (U.S. Census Bureau, 2019). The tool covers all U.S. census tracts, including those located within Tribal Nations, to the extent that data is available.")
    with st.expander("Thereโs not enough data near where I live. What should I do?"):
        st.markdown("This tool is meant to serve as a general guideline and resource, but is not intended to screen out any communities from participating in building decarbonization. Whether or not there is adequate data for your region, you should always rely on your local context and lived experience to determine how to incorporate equity into your decarbonization proposal. While this tool can help narrow down geographic areas of focus, your application will be considered holistically across many different factors.")

with viz_tab:
    st.header("How-To: ๐บ Visualize")
    st.markdown("### Navigating the Map: ")
    st.markdown(" * To expand the map, collapse the sidebar or click the link to open the map in a new tab.")
    st.markdown(" * To pan, click and hold the left mouse button and drag to move the map.")
    st.markdown(" * To collapse and uncollapse the legend, click the small carrot next to the legend title.")
    st.markdown(" * To zoom, use the scroll bar or pinch the touchpad. Alternatively, use the โ+โ and โ-โ buttons in the bottom left to zoom in and out.")
    st.markdown(" * To search for a specific location, use the search bar in the bottom left. If searching for a city or county, youโll get more accurate results by specifying the state.")
    st.markdown("### Interactive Features: ")
    st.markdown(" * To display and remove any layers, click on the checkboxes in the legend.")
    st.markdown(" * As you zoom in, county and census tract boundaries appear. The name of the county your mouse is hovering over is displayed in a pop-up.")
    st.markdown(" * Click on any census tract or property to view a pop-up with more information.")
    st.markdown(" * Several interactive widgets are displayed in the bottom or right sidebars, depending on how much the map is expanded. These allow for several helpful features.")
    st.markdown(" * Click on the small paint drop icon, which displays โApply Auto Styleโ on hover, to color the map according to the indicator in the title of the widget.")
    st.markdown(" * Click the three small dots to โtoggleโ the widget, which is unexpanded by default. By toggling the widget, you can filter by category or histogram range to only view areas meeting the selected parameters on the map. The widget dynamically adjusts to display values representing only the area currently in the map view.")

    st.markdown("All of these features are demonstrated live in the video below.")
    st.components.v1.iframe(
     src="https://www.loom.com/embed/e0942e95df9a4a8ebf449f7ec9592d70",
     height=520,
     scrolling=True,
     )


with report_tab:
    st.header("How-To: ๐ Report")
    st.markdown("1. Select a level from the options (Census Tract ID, County, State, or Tribe or Territory) to search by. Click Submit to continue.")
    st.markdown("2. In the box that appears, type a location and/or select from the dropdown. Press Search to continue.")
    st.markdown("3. Optionally, before searching, modify the report parameters by clicking on the โAdditional Report Parametersโ section to expand it. Use the slider to adjust the Energy Burden range. Check โDisadvantaged Statusโ to only include โDisadvantagedโ census tracts in the final report. Check โEligible Statusโ to only include Housing Tax Credit Eligible census tracts in the final report. Check โIndicators Reportedโ to include the values for indicators other than Energy Burden for each census tract included in the report. Once finished modifying the parameters, press Search to continue. Note that these parameters only affect the output of the downloadable report, not the interactive map or data tables.")
    st.markdown("4. Wait for up to one minute for results to appear. A spinning progress indicator will display on the screen until the results have finished loading.")
    st.markdown("5. A message may display indicating that no housing properties and/or census tracts were found for your search parameters. This may occur for a Tribe or Territory search, or any Census Tract ID or County that does not have public or subsidized housing in it.")
    st.markdown("6. Click on โHousing Dataโ or โCensus Tract Dataโ to expand the sections. A table with all search results is displayed. The table is interactive; you can scroll vertically and horizontally. Click the diagonal double arrow icon in the top right to expand the table to the full width of the screen. Double click on any header to sort by that column. Finally, download the data table as a csv and reset the search by clicking the button below the table.")
    st.markdown("7. Click on โMapโ to expand the interactive map. Hold down the left mouse and drag to pan. Scroll or pinch the trackpad to zoom; alternatively, click the โ+โ and โ-โ icons in the top right toolbar. Click the โhomeโ icon in the top right toolbar to reset the view. Click the diagonal double arrow icon in the top right to expand the map to the full width of the screen. More information about the census tracts (colored by Energy Burden Percentile, with a red border if โDisadvantagedโ) and affordable housing properties (black circles) can be viewed in a pop-up by hovering over them with a mouse. Click on the โDownload Mapโ button to download an image of the map to your device.")
    st.markdown("8. Click on โDownload Reportโ to download a file with a full report to your local device.")
    st.markdown("All of these features are demonstrated live in the video below.")
    st.components.v1.iframe(
     src="https://www.loom.com/embed/28b6127ea16e4bad8c5bab0408629e89",
     height=520,
     scrolling=True,
     )



