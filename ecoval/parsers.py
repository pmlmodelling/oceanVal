import nctoolkit as nc
import re
import pandas as pd
import os
import glob
import warnings
from ecoval.session import session_info

session_info["keys"] = []

bad_conc_vars = ["medium", "pod", "size"]

def get_name(obj):
    namespace = globals()
    for name in namespace:
        if namespace[name] is obj:
            return name
    return None

# create a validator class
# create a variable class to hold metadata
class Variable:
    def __init__(self):
        self.long_name = None
        self.gridded = None 



class Validator:
    def __init__(self):
        self.rules = {}

    def validate(self, data):
        errors = {}
        for field, rule in self.rules.items():
            if field not in data:
                errors[field] = "Field is missing"
            elif not rule(data[field]):
                errors[field] = "Validation failed"
        return errors
    # add chlorophyll
    def add_rule(self, field, rule):
        self.rules[field] = rule

    keys = session_info["keys"]

    #chlorophyll = Variable()
    #chlorophyll.gridded = True
    #chlorophyll.point = True
    #chlorophyll.sources = {}
    #chlorophyll.sources["nsbc"] = "Hinrichs,Iris; Gouretski,Viktor; Paetsch,Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1). URL: <https://www.cen.uni-hamburg.de/en/icdc/data/ocean/nsbc.html>"
    #chlorophyll.gridded_source = "nsbc"
    #chlorophyll.sources["various"] = "ICES Data Portal, Dataset on Ocean HydroChemistry, Extracted March 3, 2023. ICES, Copenhagen. \n Olsen, A., R. M. Key, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Pérez and T. Suzuki. The Global Ocean Data Analysis Project version 2 (GLODAPv2) – an internally consistent data product for the world ocean, Earth Syst. Sci. Data, 8, 297–323, 2016, doi:10.5194/essd-8-297-2016. \n Key, R.M., A. Olsen, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Perez, and T. Suzuki. 2015. Global Ocean Data Analysis Project, Version 2 (GLODAPv2), ORNL/CDIAC-162, NDP-093. Carbon Dioxide Information Analysis Center, Oak Ridge National Laboratory, US Department of Energy, Oak Ridge, Tennessee. doi:10.3334/CDIAC/OTG.NDP093_GLODAPv2."
    #chlorophyll.point_source = "various"
    #chlorophyll.sources["socat23"] = "Bakker, Dorothee C. E.; Alin, Simone R.; Bates, Nicholas; Becker, Meike; Feely, Richard A.; Gkritzalis, Thanos; Jones, Steve D.; Kozyr, Alex; Lauvset, Siv K.; Metzl, Nicolas; Munro, David R.; Nakaoka, Shin-ichiro; Nojiri, Yukihiro; O'Brien, Kevin M.; Olsen, Are; Pierrot, Denis; Rehder, Gregor; Steinhoff, Tobias; Sutton, Adrienne J.; Sweeney, Colm; Tilbrook, Bronte; Wada, Chisato; Wanninkhof, Rik; Akl, John; Barbero, Leticia; Beatty, Cory M.; Berghoff, Carla F.; Bittig, Henry C.; Bott, Randy; Burger, Eugene F.; Cai, Wei-Jun; Castaño-Primo, Rocío; Corredor, Jorge E.; Cronin, Margot; De Carlo, Eric H.; DeGrandpre, Michael D.; Dietrich, Colin; Drennan, William M.; Emerson, Steven R.; Enochs, Ian C.; Enyo, Kazutaka; Epherra, Lucía; Evans, Wiley; Fiedler, Björn; Fontela, Marcos; Frangoulis, Constantin; Gehrung, Martina; Giannoudi, Louisa; Glockzin, Michael; Hales, Burke; Howden, Stephan D.; Ibánhez, J. Severino P.; Kamb, Linus; Körtzinger, Arne; Lefèvre, Nathalie; Lo Monaco, Claire; Lutz, Vivian A.; Macovei, Vlad A.; Maenner Jones, Stacy; Manalang, Dana; Manzello, Derek P.; Metzl, Nicolas; Mickett, John; Millero, Frank J.; Monacci, Natalie M.; Morell, Julio M.; Musielewicz, Sylvia; Neill, Craig; Newberger, Tim; Newton, Jan; Noakes, Scott; Ólafsdóttir, Sólveig Rósa; Ono, Tsuneo; Osborne, John; Padín, Xose A.; Paulsen, Melf; Perivoliotis, Leonidas; Petersen, Wilhelm; Petihakis, George; Plueddemann, Albert J.; Rodriguez, Carmen; Rutgersson, Anna; Sabine, Christopher L.; Salisbury, Joseph E.; Schlitzer, Reiner; Skjelvan, Ingunn; Stamataki, Natalia; Sullivan, Kevin F.; Sutherland, Stewart C.; T'Jampens, Michiel; Tadokoro, Kazuaki; Tanhua, Toste; Telszewski, Maciej; Theetaert, Hannelore; Tomlinson, Michael; Vandemark, Douglas; Velo, Antón; Voynova, Yoana G.; Weller, Robert A.; Whitehead, Chris; Wimart-Rousseau, Cathy (2023). Surface Ocean CO2 Atlas Database Version 2023 (SOCATv2023) (NCEI Accession 0278913). [indicate subset used]. NOAA National Centers for Environmental Information. Dataset. <https://doi.org/10.25921/r7xa-bt92>. Accessed [25/04/2024]."
    #chlorophyll.short_name = "chlorophyll"
    #chlorophyll.short_title = "Chlorophyll"
    #chlorophyll.long_name = "chlorophyll concentration"
    #chlorophyll.model_variable = "auto"
    #chlorophyll.point_dir = "auto"
    #chlorophyll.gridded_dir = "auto"
    #chlorophyll.obs_var = "auto"
    #chlorophyll.verbose_description = ""
    #chlorophyll.vertical = True
    #keys.append("chlorophyll")

    ## oxygen
    #oxygen = Variable()
    #oxygen.gridded = True
    #oxygen.point = True
    #oxygen.sources = {}
    #oxygen.sources["nsbc"] = "Hinrichs,Iris; Gouretski; Viktor; Paetsch,Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1). URL: <https://www.cen.uni-hamburg.de/en/icdc/data/ocean/nsbc.html>"
    #oxygen.sources["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry , Extracted March 3, 2023. ICES, Copenhagen"
    #oxygen.gridded_source = "nsbc"
    #oxygen.point_source = "ices"
    #oxygen.short_name = "oxygen"
    #oxygen.short_title = "Oxygen"
    #oxygen.long_name = "dissolved oxygen concentration"
    #oxygen.model_variable = "auto"
    #oxygen.point_dir = "auto"
    #oxygen.gridded_dir = "auto"
    #oxygen.obs_var = "auto"
    #oxygen.verbose_description = ""
    #oxygen.vertical = True
    #keys.append("oxygen")

    ## now nitrate

    #nitrate = Variable()
    #nitrate.gridded = True
    #nitrate.point = True
    #nitrate.sources = {}
    #nitrate.sources["nsbc"] = "Hinrichs,Iris; Gouretski,Viktor; Paetsch,Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1). URL: <https://www.cen.uni-hamburg.de/en/icdc/data/ocean/nsbc.html>"
    #nitrate.sources["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry , Extracted March 3, 2023. ICES, Copenhagen"
    #nitrate.sources["various"] = "ICES Data Portal, Dataset on Ocean HydroChemistry, Extracted March 3, 2023. ICES, Copenhagen. \n Olsen, A., R. M. Key, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Pérez and T. Suzuki. The Global Ocean Data Analysis Project version 2 (GLODAPv2) – an internally consistent data product for the world ocean, Earth Syst. Sci. Data, 8, 297–323, 2016, doi:10.5194/essd-8-297-2016. \n Key, R.M., A. Olsen, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Perez, and T. Suzuki. 2015. Global Ocean Data Analysis Project, Version 2 (GLODAPv2), ORNL/CDIAC-162, NDP-093. Carbon Dioxide Information Analysis Center, Oak Ridge National Laboratory, US Department of Energy, Oak Ridge, Tennessee. doi:10.3334/CDIAC/OTG.NDP093_GLODAPv2."
    #nitrate.gridded_source = "nsbc"
    #nitrate.point_source = "various"
    #nitrate.short_name = "nitrate"
    #nitrate.short_title = "Nitrate"
    #nitrate.long_name = "nitrate concentration"
    #nitrate.model_variable = "auto"
    #nitrate.point_dir = "auto"
    #nitrate.gridded_dir = "auto"
    #nitrate.obs_var = "auto"
    #nitrate.verbose_description = ""
    #nitrate.vertical = True
    #keys.append("nitrate")

    ## phosphate
    #phosphate = Variable()
    #phosphate.gridded = True
    #phosphate.point = True
    #phosphate.sources = {}
    #phosphate.sources["nsbc"] = "Hinrichs,Iris; Gouretski,Viktor; Paetsch,Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1). URL: <https://www.cen.uni-hamburg.de/en/icdc/data/ocean/nsbc.html>"
    #phosphate.sources["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry , Extracted March 3, 2023. ICES, Copenhagen"
    #phosphate.sources["various"] = "ICES Data Portal, Dataset on Ocean HydroChemistry, Extracted March 3, 2023. ICES, Copenhagen. \n Olsen, A., R. M. Key, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Pérez and T. Suzuki. The Global Ocean Data Analysis Project version 2 (GLODAPv2) – an internally consistent data product for the world ocean, Earth Syst. Sci. Data, 8, 297–323, 2016, doi:10.5194/essd-8-297-2016. \n Key, R.M., A. Olsen, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Perez, and T. Suzuki. 2015. Global Ocean Data Analysis Project, Version 2 (GLODAPv2), ORNL/CDIAC-162, NDP-093. Carbon Dioxide Information Analysis Center, Oak Ridge National Laboratory, US Department of Energy, Oak Ridge, Tennessee. doi:10.3334/CDIAC/OTG.NDP093_GLODAPv2."
    #phosphate.gridded_source = "nsbc"
    #phosphate.point_source = "various"
    #phosphate.short_name = "phosphate"
    #phosphate.short_title = "Phosphate"
    #phosphate.long_name = "phosphate concentration"
    #phosphate.model_variable = "auto"
    #phosphate.point_dir = "auto"
    #phosphate.gridded_dir = "auto"
    #phosphate.obs_var = "auto"
    #phosphate.verbose_description = ""
    #phosphate.vertical = True
    #keys.append("phosphate")

    ## silicate
    #silicate = Variable()
    #silicate.gridded = True
    #silicate.point = True
    #silicate.sources = {}
    #silicate.sources["nsbc"] = "Hinrichs,Iris; Gouretski,Viktor; Paetsch,Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1). URL: <https://www.cen.uni-hamburg.de/en/icdc/data/ocean/nsbc.html>"
    #silicate.sources["various"] = "ICES Data Portal, Dataset on Ocean HydroChemistry, Extracted March 3, 2023. ICES, Copenhagen. \n Olsen, A., R. M. Key, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Pérez and T. Suzuki. The Global Ocean Data Analysis Project version 2 (GLODAPv2) – an internally consistent data product for the world ocean, Earth Syst. Sci. Data, 8, 297–323, 2016, doi:10.5194/essd-8-297-2016. \n Key, R.M., A. Olsen, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Perez, and T. Suzuki. 2015. Global Ocean Data Analysis Project, Version 2 (GLODAPv2), ORNL/CDIAC-162, NDP-093. Carbon Dioxide Information Analysis Center, Oak Ridge National Laboratory, US Department of Energy, Oak Ridge, Tennessee. doi:10.3334/CDIAC/OTG.NDP093_GLODAPv2."
    #silicate.gridded_source = "nsbc"
    #silicate.point_source = "various"
    #silicate.short_name = "silicate"
    #silicate.short_title = "Silicate"
    #silicate.long_name = "silicate concentration"
    #silicate.model_variable = "auto"
    #silicate.point_dir = "auto"
    #silicate.gridded_dir = "auto"
    #silicate.obs_var = "auto"
    #silicate.verbose_description = ""
    #silicate.vertical = True
    #keys.append("silicate")

    ## benbio
    #benbio = Variable()
    #benbio.gridded = False
    #benbio.point = True
    #benbio.sources = {}
    #benbio.sources["nsbs"] = "URL: <https://www.vliz.be/vmdcdata/nsbs/about.php>" 
    #benbio.point_source = "nsbs"
    #benbio.short_name = "macrobenthos biomass"
    #benbio.long_name = "macrobenthos biomass"
    #benbio.short_title = "Macrobenthos Biomass"
    #benbio.model_variable = "auto"
    #benbio.point_dir = "auto"
    #benbio.gridded_dir = "auto"
    #benbio.obs_var = "auto"
    #benbio.verbose_description = ""
    #benbio.vertical = False
    #keys.append("benbio")

    ## ammonium
    #ammonium = Variable()
    #ammonium.gridded = False
    #ammonium.point = True
    #ammonium.sources = {}
    #ammonium.sources["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry , Extracted March 3, 2023. ICES, Copenhagen"
    #ammonium.sources["nsbc"] = "Hinrichs,Iris; Gouretski,Viktor; Paetsch,Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1). URL: <https://www.cen.uni-hamburg.de/en/icdc/data/ocean/nsbc.html>"
    #ammonium.point_source = "ices"
    #ammonium.gridded_source = "nsbc"
    #ammonium.short_name = "ammonium"
    #ammonium.short_title = "Ammonium"
    #ammonium.long_name = "ammonium concentration"
    #ammonium.model_variable = "auto"
    #ammonium.point_dir = "auto"
    #ammonium.gridded_dir = "auto"
    #ammonium.obs_var = "auto"
    #ammonium.verbose_description = ""
    #ammonium.vertical = True
    #keys.append("ammonium")


    ## pco2
    #pco2 = Variable()
    #pco2.gridded = False
    #pco2.point = True
    #pco2.sources = {}
    #pco2.sources["socat23"] = "Bakker, Dorothee C. E.; Alin, Simone R.; Bates, Nicholas; Becker, Meike; Feely, Richard A.; Gkritzalis, Thanos; Jones, Steve D.; Kozyr, Alex; Lauvset, Siv K.; Metzl, Nicolas; Munro, David R.; Nakaoka, Shin-ichiro; Nojiri, Yukihiro; O'Brien, Kevin M.; Olsen, Are; Pierrot, Denis; Rehder, Gregor; Steinhoff, Tobias; Sutton, Adrienne J.; Sweeney, Colm; Tilbrook, Bronte; Wada, Chisato; Wanninkhof, Rik; Akl, John; Barbero, Leticia; Beatty, Cory M.; Berghoff, Carla F.; Bittig, Henry C.; Bott, Randy; Burger, Eugene F.; Cai, Wei-Jun; Castaño-Primo, Rocío; Corredor, Jorge E.; Cronin, Margot; De Carlo, Eric H.; DeGrandpre, Michael D.; Dietrich, Colin; Drennan, William M.; Emerson, Steven R.; Enochs, Ian C.; Enyo, Kazutaka; Epherra, Lucía; Evans, Wiley; Fiedler, Björn; Fontela, Marcos; Frangoulis, Constantin; Gehrung, Martina; Giannoudi, Louisa; Glockzin, Michael; Hales, Burke; Howden, Stephan D.; Ibánhez, J. Severino P.; Kamb, Linus; Körtzinger, Arne; Lefèvre, Nathalie; Lo Monaco, Claire; Lutz, Vivian A.; Macovei, Vlad A.; Maenner Jones, Stacy; Manalang, Dana; Manzello, Derek P.; Metzl, Nicolas; Mickett, John; Millero, Frank J.; Monacci, Natalie M.; Morell, Julio M.; Musielewicz, Sylvia; Neill, Craig; Newberger, Tim; Newton, Jan; Noakes, Scott; Ólafsdóttir, Sólveig Rósa; Ono, Tsuneo; Osborne, John; Padín, Xose A.; Paulsen, Melf; Perivoliotis, Leonidas; Petersen, Wilhelm; Petihakis, George; Plueddemann, Albert J.; Rodriguez, Carmen; Rutgersson, Anna; Sabine, Christopher L.; Salisbury, Joseph E.; Schlitzer, Reiner; Skjelvan, Ingunn; Stamataki, Natalia; Sullivan, Kevin F.; Sutherland, Stewart C.; T'Jampens, Michiel; Tadokoro, Kazuaki; Tanhua, Toste; Telszewski, Maciej; Theetaert, Hannelore; Tomlinson, Michael; Vandemark, Douglas; Velo, Antón; Voynova, Yoana G.; Weller, Robert A.; Whitehead, Chris; Wimart-Rousseau, Cathy (2023). Surface Ocean CO2 Atlas Database Version 2023 (SOCATv2023) (NCEI Accession 0278913). [indicate subset used]. NOAA National Centers for Environmental Information. Dataset. <https://doi.org/10.25921/r7xa-bt92>. Accessed [25/04/2024]."
    #pco2.point_source = "socat23"
    #pco2.short_name = "pCO<sub>2</sub>" 
    #pco2.short_title = "pCO<sub>2</sub>" 
    #pco2.long_name = "partial pressure of CO<sub>2</sub>"
    #pco2.model_variable = "auto"
    #pco2.point_dir = "auto"
    #pco2.gridded_dir = "auto"
    #pco2.obs_var = "auto"
    #pco2.verbose_description = ""
    #pco2.vertical = False
    #keys.append("pco2")

    ## ph
    #ph = Variable()
    #ph.gridded = False
    #ph.point = True
    #ph.sources = {}
    #ph.sources["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry , Extracted March 3, 2023. ICES, Copenhagen"
    #ph.point_source = "ices"
    #ph.short_name = "pH"
    #ph.short_title = "pH"
    #ph.long_name = "pH"
    #ph.model_variable = "auto"
    #ph.point_dir = "auto"
    #ph.gridded_dir = "auto"
    #ph.obs_var = "auto" 
    #ph.verbose_description = ""
    #ph.vertical = True
    #keys.append("ph")


    ## salinity
    #salinity = Variable()
    #salinity.gridded = True
    #salinity.point = True
    #salinity.sources = {}
    #salinity.sources["nsbc"] = "Hinrichs,Iris; Gouretski,Viktor; Paetsch,Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1). URL: <https://www.cen.uni-hamburg.de/en/icdc/data/ocean/nsbc.html>"
    #salinity.sources["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry , Extracted March 3, 2023. ICES, Copenhagen"
    #salinity.gridded_source = "nsbc"
    #salinity.point_source = "ices"
    #salinity.short_name = "salinity"    
    #salinity.short_title = "Salinity"
    #salinity.long_name = "salinity"
    #salinity.model_variable = "auto"
    #salinity.point_dir = "auto"
    #salinity.gridded_dir = "auto"
    #salinity.obs_var = "auto"
    #salinity.verbose_description = ""
    #salinity.vertical = True
    #keys.append("salinity")

    ## temperature
    #temperature = Variable()
    #temperature.gridded = True
    #temperature.point = True
    #temperature.sources = {}
    #temperature.sources["ostia"] =  "Good, S.; Fiedler, E.; Mao, C.; Martin, M.J.; Maycock, A.; Reid, R.; Roberts-Jones, J.; Searle, T.; Waters, J.; While, J.; Worsfold, M. The Current Configuration of the OSTIA System for Operational Production of Foundation Sea Surface Temperature and Ice Concentration Analyses. Remote Sens. 2020, 12, 720, doi:10.3390/rs12040720. \n URL: <https://data.marine.copernicus.eu/product/SST_GLO_SST_L4_REP_OBSERVATIONS_010_011/description> \n From 2022 onwards, the near-real time product is used: <https://data.marine.copernicus.eu/product/SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001/description>"
    #temperature.sources["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry , Extracted March 3, 2023. ICES, Copenhagen"
    #temperature.gridded_source = "ostia"
    #temperature.point_source = "ices"
    #temperature.short_name = "temperature"  
    #temperature.short_title = "Temperature"
    #temperature.long_name = "temperature"
    #temperature.model_variable = "auto"
    #temperature.point_dir = "auto"
    #temperature.gridded_dir = "auto"
    #temperature.obs_var = "auto"
    #temperature.verbose_description = ""
    #temperature.vertical = True 
    #keys.append("temperature")

    ## co2flux
    #co2flux = Variable()
    #co2flux.gridded = True
    #co2flux.point = False
    #co2flux.sources = {}
    #co2flux.sources["ncei"] = "Jersild, Annika; Landschützer, Peter; Gruber, Nicolas; Bakker, Dorothee C. E. (2017). An observation-based global monthly gridded sea surface pCO2 and air-sea CO2 flux product from 1982 onward and its monthly climatology (NCEI Accession 0160558). Version 7.7. [v 2022]. NOAA National Centers for Environmental Information. Dataset. https://doi.org/10.7289/v5z899n6. Accessed [2025-11-04] URL: <https://www.ncei.noaa.gov/data/oceans/ncei/ocads/data/0160558/MPI_SOM-FFN_v2022/>"
    #co2flux.gridded_source = "ncei"
    #co2flux.short_name = "air-sea CO2<sub>2</sub> fluxes" 
    #co2flux.short_title = "CO2<sub>2</sub> fluxes"
    #co2flux.long_name = "air-sea CO2<sub>2</sub> fluxes" 
    #co2flux.model_variable = "auto"
    #co2flux.point_dir = "auto"
    #co2flux.gridded_dir = "auto"
    #co2flux.obs_var = "auto"
    #co2flux.verbose_description = ""
    #co2flux.vertical = False
    #keys.append("co2flux")


    ## alkalinity
    #alkalinity = Variable()
    #alkalinity.gridded = True
    #alkalinity.point = True
    #alkalinity.sources = {}
    #alkalinity.sources["glodap"] = "Lauvset, S. K., Key, R. M., Olsen, A., van Heuven, S., Velo, A., Lin, X., Schirnick, C., Kozyr, A., Tanhua, T., Hoppema, M., Jutterström, S., Steinfeldt, R., Jeansson, E., Ishii, M., Perez, F. F., Suzuki, T., and Watelet, S.: A new global interior ocean mapped climatology: the 1° ×  1° GLODAP version 2, Earth Syst. Sci. Data, 8, 325–340, https://doi.org/10.5194/essd-8-325-2016, 2016."
    #alkalinity.sources["various"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry, Extracted March 3, 2023. ICES, Copenhagen. \n Olsen, A., R. M. Key, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Pérez and T. Suzuki. The Global Ocean Data Analysis Project version 2 (GLODAPv2) – an internally consistent data product for the world ocean, Earth Syst. Sci. Data, 8, 297–323, 2016, doi:10.5194/essd-8-297-2016. \nKey, R.M., A. Olsen, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Perez, and T. Suzuki. 2015. Global Ocean Data Analysis Project, Version 2 (GLODAPv2), ORNL/CDIAC-162, NDP-093. Carbon Dioxide Information Analysis Center, Oak Ridge National Laboratory, US Department of Energy, Oak Ridge, Tennessee. doi:10.3334/CDIAC/OTG.NDP093_GLODAPv2."
    #alkalinity.gridded_source = "glodap"
    #alkalinity.point_source = "various"
    #alkalinity.short_name = "alkalinity"
    #alkalinity.short_title = "Alkalinity"
    #alkalinity.long_name = "total alkalinity"
    #alkalinity.model_variable = "auto"
    #alkalinity.point_dir = "auto"
    #alkalinity.gridded_dir = "auto"
    #alkalinity.obs_var = "auto"
    #alkalinity.verbose_description = ""
    #alkalinity.vertical = True
    #keys.append("alkalinity")

    ## now kd
    #kd = Variable()
    #kd.gridded = True
    #kd.point = False
    #kd.sources = {}
    #kd.sources["cmems"] = "URL: <https://doi.org/10.48670/moi-00281>" 
    #kd.gridded_source = "cmems"
    #kd.short_name = "kd" 
    #kd.short_title = "kd"
    #kd.long_name = "light attenuation"
    #kd.model_variable = "auto"
    #kd.point_dir = "auto"
    #kd.gridded_dir = "auto"
    #kd.obs_var = "KD490" 
    #text = "Sea surface light attenuation is compared with KD490 from the Copernicus Marine Environment Monitoring Service (CMEMS) dataset OCEANCOLOUR_GLO_BGC_L4_MY_009_104."
    #text += " Kd490 is a comparable but not identical measure of attenuation, Kd490 refers to attenuation at 490 nm, while the model has no spectral dependence."
    #kd.verbose_description = text
    #kd.vertical = False
    #keys.append("kd")

    # ensure self.x = y, adds x to the keys list
    def __setattr__(self, name, value):
        if name != "keys" and "rules" not in name:
            if name not in self.keys:
                self.keys.append(name)
                # ensure this can be accessed via self[name]

        super().__setattr__(name, value)

    # create a [] style accessor
    # make Validator subsettable, so that validator["chlorophyll"] returns the chlorophyll variable
    def __getitem__(self, key):
        # if key == "chlorophyll":
        #     return  
        return getattr(self, key, None)
    
    # add a method that let's user create a new Variable and add it to the definitions
    # 
    def add_gridded_comparison(self, name, long_name, short_name, short_title, source, description, model_variable, obs_dir = "auto", obs_var = "auto" , start = -1000, end = 3000  ): 
        try:
            point_dir = getattr(self, name).point_dir
            point = getattr(self, name).point
            point_source = getattr(self, name).point_source
            orig_sources = getattr(self, name).sources
            # get point start
            point_start = getattr(self, name).point_start
            point_end = getattr(self, name).point_end
            depths = getattr(self, name).depths
        except:
            orig_sources = dict()
            point = None,
            point_source = None
            point_dir = None
            point_start = -1000
            point_end = 3000
            depths = None
            pass

        var = Variable()
        var.depths = depths
        var.gridded_start = start
        var.gridded_end = end
        var.point_start = point_start
        var.point_end = point_end

        var.point = point
        var.point_source = point_source
        var.gridded = True
        var.long_name = long_name
        var.short_name = short_name
        var.short_title = short_title
        source = {source: description}
        if list(source.keys())[0] in orig_sources:
            # ensure the value is the same
            if orig_sources[list(source.keys())[0]] != source[list(source.keys())[0]]:
                raise ValueError(f"Source {list(source.keys())[0]} already exists with a different value")
        # ensure the sourc key does not included "_"
        if "_" in list(source.keys())[0]:
            raise ValueError("Source key cannot contain '_'")
        var.sources = orig_sources | source
        var.gridded_source = list(source.keys())[0]
        var.model_variable = model_variable
        var.point_dir = point_dir
        # add obs_var, ensure it's a string
        var.obs_var = obs_var
        if not isinstance(var.obs_var, str):
            raise ValueError("obs_var must be a string")
        # check this exists
        gridded_dir = obs_dir
        var.gridded_dir = gridded_dir
        if gridded_dir != "auto":
            if not os.path.exists(gridded_dir):
                raise ValueError(f"Gridded directory {gridded_dir} does not exist")

        # ensure nothing is None
        for attr in [var.long_name, var.short_name, var.short_title, var.sources, var.model_variable, var.obs_var, var.gridded_source]:
            if attr is None:
                raise ValueError(f"Attribute {attr} cannot be None")
        setattr(self, name, var)
    # 
    def add_point_comparison(self, name, long_name, depths, short_name, short_title, source, description, model_variable, start = -1000, end = 3000, obs_dir = "auto"): 
        try:
            gridded_dir = getattr(self, name).gridded_dir   
            obs_var = getattr(self, name).obs_var
            gridded = getattr(self, name).gridded
            gridded_source = getattr(self, name).gridded_source
            orig_sources = getattr(self, name).sources
            gridded_start = getattr(self, name).gridded_start
            gridded_end = getattr(self, name).gridded_end
        except:
            gridded_dir = "auto"
            obs_var = "auto"
            gridded_source = "auto"
            gridded = False
            orig_sources = dict()
            gridded_start = -1000
            gridded_end = 3000
            pass

        var = Variable()
        var.gridded_start = gridded_start
        var.gridded_end = gridded_end

        # depths must be a string and one of "surface" or "all"
        if not isinstance(depths, str):
            raise ValueError("depths must be a string")
        if depths not in ["surface", "all"]:
            raise ValueError("depths must be one of 'surface' or 'all'")
        var.depths = depths

        var.point = True
        var.gridded = gridded
        var.long_name = long_name
        var.short_name = short_name
        var.short_title = short_title
        var.point_start = start
        var.point_end = end
        # check these are int or can be cast to int
        try:
            var.point_start = int(var.point_start)
            var.point_end = int(var.point_end)
        except:
            raise ValueError("start and end must be integers")
        # append source to the var.source
        # check if source key is in orig_source
        source = {source: description}
        if list(source.keys())[0] in orig_sources:
            # ensure the value is the same
            if orig_sources[list(source.keys())[0]] != source[list(source.keys())[0]]:
                raise ValueError(f"Source {list(source.keys())[0]} already exists with a different value")
        # ensure the sourc key does not included "_"
        if "_" in list(source.keys())[0]:
            raise ValueError("Source key cannot contain '_'")
        var.sources = orig_sources | source 
        var.gridded_source = gridded_source
        var.point_source = list(source.keys())[0]   
        var.model_variable = model_variable
        var.point_dir = obs_dir
        # find feather files in point_dir
        point_files = [f for f in glob.glob(os.path.join(obs_dir, "*.feather"))] 
        # if no files exists, raise error
        if len(point_files) == 0:
            raise ValueError(f"No feather files found in point directory {obs_dir}")
        valid_vars = ["lon", "lat", "year", "month", "day", "depth", "observation", "source"]
        vertical = False
        for vv in point_files:
            # read in the first row
            df = pd.read_feather(vv)
            # throw error something else is in there
            bad_cols = [col for col in df.columns if col not in valid_vars]
            if len(bad_cols) > 0:
                raise ValueError(f"Invalid columns {bad_cols} found in point data file {vv}")
            if "depth" in df.columns:
                vertical = True

        var.vertical = vertical

        var.obs_var = obs_var
        # add obs_var, ensure it's a string
        if not isinstance(var.obs_var, str):
            raise ValueError("obs_var must be a string")
        # check this exists
        point_dir = obs_dir
        if point_dir != "auto":
            if not os.path.exists(point_dir):
                raise ValueError(f"Point directory {point_dir} does not exist")
        var.gridded_dir = gridded_dir
        if gridded_dir != "auto":
            if not os.path.exists(gridded_dir):
                raise ValueError(f"Gridded directory {gridded_dir} does not exist")

        # ensure nothing is None
        for attr in [var.long_name, var.short_name, var.short_title, var.sources, var.model_variable, var.obs_var]:
            if attr is None:
                raise ValueError(f"Attribute {attr} cannot be None")
        setattr(self, name, var)
    # 

definitions = Validator()



def generate_mapping(ds):
    """
    Generate mapping of model and observational variables
    """

    candidate_variables = definitions.keys
    ds1 = nc.open_data(ds[0], checks=False)
    ds_contents = ds1.contents

    ds_contents["long_name"] = [str(x) for x in ds_contents["long_name"]]

    ds_contents_top = ds_contents.query("nlevels == 1").reset_index(drop=True)
    #ds_contents = ds_contents.query("nlevels > 1").reset_index(drop=True)
    n_levels = ds_contents.nlevels.max()
    if n_levels > session_info["n_levels"]:
        session_info["n_levels"] = n_levels
    # number of rows in ds_contents
    if len(ds_contents) == 0:
        ds_contents = ds_contents_top

    model_dict = {}
    for vv in candidate_variables:
        vv_check = vv

        if definitions[vv].model_variable != "auto":
            variables = definitions[vv].model_variable.split("+")
            include = True
            for var in variables:
                if var not in ds_contents.variable.values:
                    include = False
            if include:
                model_dict[vv] = definitions[vv].model_variable
                continue

    return model_dict


