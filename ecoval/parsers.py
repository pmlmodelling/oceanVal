import nctoolkit as nc
import re
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

    # add a setter for each attribute
    def set_all(self, long_name = None, gridded = None, point = None, source = None, short_name = None, short_title = None, model_variable = None):
        # if any of these are None, return an error
        if long_name is None or gridded is None or point is None or source is None or short_name is None or short_title is None or model_variable is None:
            raise ValueError("All attributes must be provided")
        self.long_name = long_name
        self.gridded = gridded
        self.point = point
        self.source = source
        self.short_name = short_name
        self.short_title = short_title
        self.model_variable = model_variable
        # add the __name__ of self to keys
        key = get_name(self)
        if key is not None:
            session_info["keys"].append(key)


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

    chlorophyll = Variable()
    chlorophyll.gridded = True
    chlorophyll.point = True
    chlorophyll.source = {}
    chlorophyll.source["nsbc"] = "Hinrichs,Iris; Gouretski,Viktor; Paetsch,Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1). URL: <https://www.cen.uni-hamburg.de/en/icdc/data/ocean/nsbc.html>"
    chlorophyll.source["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry, Extracted March 3, 2023. ICES, Copenhagen"
    chlorophyll.source["various"] = "ICES Data Portal, Dataset on Ocean HydroChemistry, Extracted March 3, 2023. ICES, Copenhagen. \n Olsen, A., R. M. Key, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Pérez and T. Suzuki. The Global Ocean Data Analysis Project version 2 (GLODAPv2) – an internally consistent data product for the world ocean, Earth Syst. Sci. Data, 8, 297–323, 2016, doi:10.5194/essd-8-297-2016. \n Key, R.M., A. Olsen, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Perez, and T. Suzuki. 2015. Global Ocean Data Analysis Project, Version 2 (GLODAPv2), ORNL/CDIAC-162, NDP-093. Carbon Dioxide Information Analysis Center, Oak Ridge National Laboratory, US Department of Energy, Oak Ridge, Tennessee. doi:10.3334/CDIAC/OTG.NDP093_GLODAPv2."
    chlorophyll.source["socat23"] = "Bakker, Dorothee C. E.; Alin, Simone R.; Bates, Nicholas; Becker, Meike; Feely, Richard A.; Gkritzalis, Thanos; Jones, Steve D.; Kozyr, Alex; Lauvset, Siv K.; Metzl, Nicolas; Munro, David R.; Nakaoka, Shin-ichiro; Nojiri, Yukihiro; O'Brien, Kevin M.; Olsen, Are; Pierrot, Denis; Rehder, Gregor; Steinhoff, Tobias; Sutton, Adrienne J.; Sweeney, Colm; Tilbrook, Bronte; Wada, Chisato; Wanninkhof, Rik; Akl, John; Barbero, Leticia; Beatty, Cory M.; Berghoff, Carla F.; Bittig, Henry C.; Bott, Randy; Burger, Eugene F.; Cai, Wei-Jun; Castaño-Primo, Rocío; Corredor, Jorge E.; Cronin, Margot; De Carlo, Eric H.; DeGrandpre, Michael D.; Dietrich, Colin; Drennan, William M.; Emerson, Steven R.; Enochs, Ian C.; Enyo, Kazutaka; Epherra, Lucía; Evans, Wiley; Fiedler, Björn; Fontela, Marcos; Frangoulis, Constantin; Gehrung, Martina; Giannoudi, Louisa; Glockzin, Michael; Hales, Burke; Howden, Stephan D.; Ibánhez, J. Severino P.; Kamb, Linus; Körtzinger, Arne; Lefèvre, Nathalie; Lo Monaco, Claire; Lutz, Vivian A.; Macovei, Vlad A.; Maenner Jones, Stacy; Manalang, Dana; Manzello, Derek P.; Metzl, Nicolas; Mickett, John; Millero, Frank J.; Monacci, Natalie M.; Morell, Julio M.; Musielewicz, Sylvia; Neill, Craig; Newberger, Tim; Newton, Jan; Noakes, Scott; Ólafsdóttir, Sólveig Rósa; Ono, Tsuneo; Osborne, John; Padín, Xose A.; Paulsen, Melf; Perivoliotis, Leonidas; Petersen, Wilhelm; Petihakis, George; Plueddemann, Albert J.; Rodriguez, Carmen; Rutgersson, Anna; Sabine, Christopher L.; Salisbury, Joseph E.; Schlitzer, Reiner; Skjelvan, Ingunn; Stamataki, Natalia; Sullivan, Kevin F.; Sutherland, Stewart C.; T'Jampens, Michiel; Tadokoro, Kazuaki; Tanhua, Toste; Telszewski, Maciej; Theetaert, Hannelore; Tomlinson, Michael; Vandemark, Douglas; Velo, Antón; Voynova, Yoana G.; Weller, Robert A.; Whitehead, Chris; Wimart-Rousseau, Cathy (2023). Surface Ocean CO2 Atlas Database Version 2023 (SOCATv2023) (NCEI Accession 0278913). [indicate subset used]. NOAA National Centers for Environmental Information. Dataset. <https://doi.org/10.25921/r7xa-bt92>. Accessed [25/04/2024]."
    chlorophyll.short_name = "chlorophyll"
    chlorophyll.short_title = "Chlorophyll"
    chlorophyll.long_name = "chlorophyll concentration"
    chlorophyll.model_variable = "auto"
    session_info["keys"].append("chlorophyll")

    # oxygen
    oxygen = Variable()
    oxygen.gridded = True
    oxygen.point = True
    oxygen.source = {}
    oxygen.source["nsbc"] = "Hinrichs,Iris; Gouretski; Viktor; Paetsch,Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1). URL: <https://www.cen.uni-hamburg.de/en/icdc/data/ocean/nsbc.html>"
    oxygen.source["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry , Extracted March 3, 2023. ICES, Copenhagen"
    oxygen.source["socat23"] = "Bakker, Dorothee C. E.; Alin, Simone R.; Bates, Nicholas; Becker, Meike; Feely, Richard A.; Gkritzalis, Thanos; Jones, Steve D.; Kozyr, Alex; Lauvset, Siv K.; Metzl, Nicolas; Munro, David R.; Nakaoka, Shin-ichiro; Nojiri, Yukihiro; O'Brien, Kevin M.; Olsen, Are; Pierrot, Denis; Rehder, Gregor; Steinhoff, Tobias; Sutton, Adrienne J.; Sweeney, Colm; Tilbrook, Bronte; Wada, Chisato; Wanninkhof, Rik; Akl, John; Barbero, Leticia; Beatty, Cory M.; Berghoff, Carla F.; Bittig, Henry C.; Bott, Randy; Burger, Eugene F.; Cai, Wei-Jun; Castaño-Primo, Rocío; Corredor, Jorge E.; Cronin, Margot; De Carlo, Eric H.; DeGrandpre, Michael D.; Dietrich, Colin; Drennan, William M.; Emerson, Steven R.; Enochs, Ian C.; Enyo, Kazutaka; Epherra, Lucía; Evans, Wiley; Fiedler, Björn; Fontela, Marcos; Frangoulis, Constantin; Gehrung, Martina; Giannoudi, Louisa; Glockzin, Michael; Hales, Burke; Howden, Stephan D.; Ibánhez, J. Severino P.; Kamb, Linus; Körtzinger, Arne; Lefèvre, Nathalie; Lo Monaco, Claire; Lutz, Vivian A.; Macovei, Vlad A.; Maenner Jones, Stacy; Manalang, Dana; Manzello, Derek P.; Metzl, Nicolas; Mickett, John; Millero, Frank J.; Monacci, Natalie M.; Morell, Julio M.; Musielewicz, Sylvia; Neill, Craig; Newberger, Tim; Newton, Jan; Noakes, Scott; Ólafsdóttir, Sólveig Rósa; Ono, Tsuneo; Osborne, John; Padín, Xose A.; Paulsen, Melf; Perivoliotis, Leonidas; Petersen, Wilhelm; Petihakis, George; Plueddemann, Albert J.; Rodriguez, Carmen; Rutgersson, Anna; Sabine, Christopher L.; Salisbury, Joseph E.; Schlitzer, Reiner; Skjelvan, Ingunn; Stamataki, Natalia; Sullivan, Kevin F.; Sutherland, Stewart C.; T'Jampens, Michiel; Tadokoro, Kazuaki; Tanhua, Toste; Telszewski, Maciej; Theetaert, Hannelore; Tomlinson, Michael; Vandemark, Douglas; Velo, Antón; Voynova, Yoana G.; Weller, Robert A.; Whitehead, Chris; Wimart-Rousseau, Cathy (2023). Surface Ocean CO2 Atlas Database Version 2023 (SOCATv2023) (NCEI Accession 0278913). [indicate subset used]. NOAA National Centers for Environmental Information. Dataset. <https://doi.org/10.25921/r7xa-bt92>. Accessed [25/04/2024]."
    oxygen.short_name = "oxygen"
    oxygen.short_title = "Oxygen"
    oxygen.long_name = "dissolved oxygen concentration"
    oxygen.model_variable = "auto"
    keys.append("oxygen")

    # now nitrate

    nitrate = Variable()
    nitrate.gridded = True
    nitrate.point = True
    nitrate.source = {}
    nitrate.source["nsbc"] = "Hinrichs,Iris; Gouretski,Viktor; Paetsch,Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1). URL: <https://www.cen.uni-hamburg.de/en/icdc/data/ocean/nsbc.html>"
    nitrate.source["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry , Extracted March 3, 2023. ICES, Copenhagen"
    nitrate.source["various"] = "ICES Data Portal, Dataset on Ocean HydroChemistry, Extracted March 3, 2023. ICES, Copenhagen. \n Olsen, A., R. M. Key, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Pérez and T. Suzuki. The Global Ocean Data Analysis Project version 2 (GLODAPv2) – an internally consistent data product for the world ocean, Earth Syst. Sci. Data, 8, 297–323, 2016, doi:10.5194/essd-8-297-2016. \n Key, R.M., A. Olsen, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Perez, and T. Suzuki. 2015. Global Ocean Data Analysis Project, Version 2 (GLODAPv2), ORNL/CDIAC-162, NDP-093. Carbon Dioxide Information Analysis Center, Oak Ridge National Laboratory, US Department of Energy, Oak Ridge, Tennessee. doi:10.3334/CDIAC/OTG.NDP093_GLODAPv2."
    nitrate.source["socat23"] = "Bakker, Dorothee C. E.; Alin, Simone R.; Bates, Nicholas; Becker, Meike; Feely, Richard A.; Gkritzalis, Thanos; Jones, Steve D.; Kozyr, Alex; Lauvset, Siv K.; Metzl, Nicolas; Munro, David R.; Nakaoka, Shin-ichiro; Nojiri, Yukihiro; O'Brien, Kevin M.; Olsen, Are; Pierrot, Denis; Rehder, Gregor; Steinhoff, Tobias; Sutton, Adrienne J.; Sweeney, Colm; Tilbrook, Bronte; Wada, Chisato; Wanninkhof, Rik; Akl, John; Barbero, Leticia; Beatty, Cory M.; Berghoff, Carla F.; Bittig, Henry C.; Bott, Randy; Burger, Eugene F.; Cai, Wei-Jun; Castaño-Primo, Rocío; Corredor, Jorge E.; Cronin, Margot; De Carlo, Eric H.; DeGrandpre, Michael D.; Dietrich, Colin; Drennan, William M.; Emerson, Steven R.; Enochs, Ian C.; Enyo, Kazutaka; Epherra, Lucía; Evans, Wiley; Fiedler, Björn; Fontela, Marcos; Frangoulis, Constantin; Gehrung, Martina; Giannoudi, Louisa; Glockzin, Michael; Hales, Burke; Howden, Stephan D.; Ibánhez, J. Severino P.; Kamb, Linus; Körtzinger, Arne; Lefèvre, Nathalie; Lo Monaco, Claire; Lutz, Vivian A.; Macovei, Vlad A.; Maenner Jones, Stacy; Manalang, Dana; Manzello, Derek P.; Metzl, Nicolas; Mickett, John; Millero, Frank J.; Monacci, Natalie M.; Morell, Julio M.; Musielewicz, Sylvia; Neill, Craig; Newberger, Tim; Newton, Jan; Noakes, Scott; Ólafsdóttir, Sólveig Rósa; Ono, Tsuneo; Osborne, John; Padín, Xose A.; Paulsen, Melf; Perivoliotis, Leonidas; Petersen, Wilhelm; Petihakis, George; Plueddemann, Albert J.; Rodriguez, Carmen; Rutgersson, Anna; Sabine, Christopher L.; Salisbury, Joseph E.; Schlitzer, Reiner; Skjelvan, Ingunn; Stamataki, Natalia; Sullivan, Kevin F.; Sutherland, Stewart C.; T'Jampens, Michiel; Tadokoro, Kazuaki; Tanhua, Toste; Telszewski, Maciej; Theetaert, Hannelore; Tomlinson, Michael; Vandemark, Douglas; Velo, Antón; Voynova, Yoana G.; Weller, Robert A.; Whitehead, Chris; Wimart-Rousseau, Cathy (2023). Surface Ocean CO2 Atlas Database Version 2023 (SOCATv2023) (NCEI Accession 0278913). [indicate subset used]. NOAA National Centers for Environmental Information. Dataset. <https://doi.org/10.25921/r7xa-bt92>. Accessed [25/04/2024]."
    nitrate.short_name = "nitrate"
    nitrate.short_title = "Nitrate"
    nitrate.long_name = "nitrate concentration"
    nitrate.model_variable = "auto"
    keys.append("nitrate")

    # phosphate
    phosphate = Variable()
    phosphate.gridded = True
    phosphate.point = True
    phosphate.source = {}
    phosphate.source["nsbc"] = "Hinrichs,Iris; Gouretski,Viktor; Paetsch,Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1). URL: <https://www.cen.uni-hamburg.de/en/icdc/data/ocean/nsbc.html>"
    phosphate.source["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry , Extracted March 3, 2023. ICES, Copenhagen"
    phosphate.source["various"] = "ICES Data Portal, Dataset on Ocean HydroChemistry, Extracted March 3, 2023. ICES, Copenhagen. \n Olsen, A., R. M. Key, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Pérez and T. Suzuki. The Global Ocean Data Analysis Project version 2 (GLODAPv2) – an internally consistent data product for the world ocean, Earth Syst. Sci. Data, 8, 297–323, 2016, doi:10.5194/essd-8-297-2016. \n Key, R.M., A. Olsen, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Perez, and T. Suzuki. 2015. Global Ocean Data Analysis Project, Version 2 (GLODAPv2), ORNL/CDIAC-162, NDP-093. Carbon Dioxide Information Analysis Center, Oak Ridge National Laboratory, US Department of Energy, Oak Ridge, Tennessee. doi:10.3334/CDIAC/OTG.NDP093_GLODAPv2."
    phosphate.source["socat23"] = "Bakker, Dorothee C. E.; Alin, Simone R.; Bates, Nicholas; Becker, Meike; Feely, Richard A.; Gkritzalis, Thanos; Jones, Steve D.; Kozyr, Alex; Lauvset, Siv K.; Metzl, Nicolas; Munro, David R.; Nakaoka, Shin-ichiro; Nojiri, Yukihiro; O'Brien, Kevin M.; Olsen, Are; Pierrot, Denis; Rehder, Gregor; Steinhoff, Tobias; Sutton, Adrienne J.; Sweeney, Colm; Tilbrook, Bronte; Wada, Chisato; Wanninkhof, Rik; Akl, John; Barbero, Leticia; Beatty, Cory M.; Berghoff, Carla F.; Bittig, Henry C.; Bott, Randy; Burger, Eugene F.; Cai, Wei-Jun; Castaño-Primo, Rocío; Corredor, Jorge E.; Cronin, Margot; De Carlo, Eric H.; DeGrandpre, Michael D.; Dietrich, Colin; Drennan, William M.; Emerson, Steven R.; Enochs, Ian C.; Enyo, Kazutaka; Epherra, Lucía; Evans, Wiley; Fiedler, Björn; Fontela, Marcos; Frangoulis, Constantin; Gehrung, Martina; Giannoudi, Louisa; Glockzin, Michael; Hales, Burke; Howden, Stephan D.; Ibánhez, J. Severino P.; Kamb, Linus; Körtzinger, Arne; Lefèvre, Nathalie; Lo Monaco, Claire; Lutz, Vivian A.; Macovei, Vlad A.; Maenner Jones, Stacy; Manalang, Dana; Manzello, Derek P.; Metzl, Nicolas; Mickett, John; Millero, Frank J.; Monacci, Natalie M.; Morell, Julio M.; Musielewicz, Sylvia; Neill, Craig; Newberger, Tim; Newton, Jan; Noakes, Scott; Ólafsdóttir, Sólveig Rósa; Ono, Tsuneo; Osborne, John; Padín, Xose A.; Paulsen, Melf; Perivoliotis, Leonidas; Petersen, Wilhelm; Petihakis, George; Plueddemann, Albert J.; Rodriguez, Carmen; Rutgersson, Anna; Sabine, Christopher L.; Salisbury, Joseph E.; Schlitzer, Reiner; Skjelvan, Ingunn; Stamataki, Natalia; Sullivan, Kevin F.; Sutherland, Stewart C.; T'Jampens, Michiel; Tadokoro, Kazuaki; Tanhua, Toste; Telszewski, Maciej; Theetaert, Hannelore; Tomlinson, Michael; Vandemark, Douglas; Velo, Antón; Voynova, Yoana G.; Weller, Robert A.; Whitehead, Chris; Wimart-Rousseau, Cathy (2023). Surface Ocean CO2 Atlas Database Version 2023 (SOCATv2023) (NCEI Accession 0278913). [indicate subset used]. NOAA National Centers for Environmental Information. Dataset. <https://doi.org/10.25921/r7xa-bt92>. Accessed [25/04/2024]."
    phosphate.short_name = "phosphate"
    phosphate.short_title = "Phosphate"
    phosphate.long_name = "phosphate concentration"
    phosphate.model_variable = "auto"
    keys.append("phosphate")

    # silicate
    silicate = Variable()
    silicate.gridded = True
    silicate.point = True
    silicate.source = {}
    silicate.source["nsbc"] = "Hinrichs,Iris; Gouretski,Viktor; Paetsch,Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1). URL: <https://www.cen.uni-hamburg.de/en/icdc/data/ocean/nsbc.html>"
    silicate.source["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry , Extracted March 3, 2023. ICES, Copenhagen"
    silicate.source["various"] = "ICES Data Portal, Dataset on Ocean HydroChemistry, Extracted March 3, 2023. ICES, Copenhagen. \n Olsen, A., R. M. Key, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Pérez and T. Suzuki. The Global Ocean Data Analysis Project version 2 (GLODAPv2) – an internally consistent data product for the world ocean, Earth Syst. Sci. Data, 8, 297–323, 2016, doi:10.5194/essd-8-297-2016. \n Key, R.M., A. Olsen, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Perez, and T. Suzuki. 2015. Global Ocean Data Analysis Project, Version 2 (GLODAPv2), ORNL/CDIAC-162, NDP-093. Carbon Dioxide Information Analysis Center, Oak Ridge National Laboratory, US Department of Energy, Oak Ridge, Tennessee. doi:10.3334/CDIAC/OTG.NDP093_GLODAPv2."
    silicate.source["socat23"] = "Bakker, Dorothee C. E.; Alin, Simone R.; Bates, Nicholas; Becker, Meike; Feely, Richard A.; Gkritzalis, Thanos; Jones, Steve D.; Kozyr, Alex; Lauvset, Siv K.; Metzl, Nicolas; Munro, David R.; Nakaoka, Shin-ichiro; Nojiri, Yukihiro; O'Brien, Kevin M.; Olsen, Are; Pierrot, Denis; Rehder, Gregor; Steinhoff, Tobias; Sutton, Adrienne J.; Sweeney, Colm; Tilbrook, Bronte; Wada, Chisato; Wanninkhof, Rik; Akl, John; Barbero, Leticia; Beatty, Cory M.; Berghoff, Carla F.; Bittig, Henry C.; Bott, Randy; Burger, Eugene F.; Cai, Wei-Jun; Castaño-Primo, Rocío; Corredor, Jorge E.; Cronin, Margot; De Carlo, Eric H.; DeGrandpre, Michael D.; Dietrich, Colin; Drennan, William M.; Emerson, Steven R.; Enochs, Ian C.; Enyo, Kazutaka; Epherra, Lucía; Evans, Wiley; Fiedler, Björn; Fontela, Marcos; Frangoulis, Constantin; Gehrung, Martina; Giannoudi, Louisa; Glockzin, Michael; Hales, Burke; Howden, Stephan D.; Ibánhez, J. Severino P.; Kamb, Linus; Körtzinger, Arne; Lefèvre, Nathalie; Lo Monaco, Claire; Lutz, Vivian A.; Macovei, Vlad A.; Maenner Jones, Stacy; Manalang, Dana; Manzello, Derek P.; Metzl, Nicolas; Mickett, John; Millero, Frank J.; Monacci, Natalie M.; Morell, Julio M.; Musielewicz, Sylvia; Neill, Craig; Newberger, Tim; Newton, Jan; Noakes, Scott; Ólafsdóttir, Sólveig Rósa; Ono, Tsuneo; Osborne, John; Padín, Xose A.; Paulsen, Melf; Perivoliotis, Leonidas; Petersen, Wilhelm; Petihakis, George; Plueddemann, Albert J.; Rodriguez, Carmen; Rutgersson, Anna; Sabine, Christopher L.; Salisbury, Joseph E.; Schlitzer, Reiner; Skjelvan, Ingunn; Stamataki, Natalia; Sullivan, Kevin F.; Sutherland, Stewart C.; T'Jampens, Michiel; Tadokoro, Kazuaki; Tanhua, Toste; Telszewski, Maciej; Theetaert, Hannelore; Tomlinson, Michael; Vandemark, Douglas; Velo, Antón; Voynova, Yoana G.; Weller, Robert A.; Whitehead, Chris; Wimart-Rousseau, Cathy (2023). Surface Ocean CO2 Atlas Database Version 2023 (SOCATv2023) (NCEI Accession 0278913). [indicate subset used]. NOAA National Centers for Environmental Information. Dataset. <https://doi.org/10.25921/r7xa-bt92>. Accessed [25/04/2024]."
    silicate.short_name = "silicate"
    silicate.short_title = "Silicate"
    silicate.long_name = "silicate concentration"
    silicate.model_variable = "auto"
    keys.append("silicate")

    # benbio
    benbio = Variable()
    benbio.gridded = False
    benbio.point = True
    benbio.source = {}
    benbio.source["nsbs"] = "URL: <https://www.vliz.be/vmdcdata/nsbs/about.php>" 
    benbio.short_name = "macrobenthos biomass"
    benbio.long_name = "macrobenthos biomass"
    benbio.short_title = "Macrobenthos Biomass"
    benbio.model_variable = "auto"
    keys.append("benbio")

    # ammonium
    ammonium = Variable()
    ammonium.gridded = False
    ammonium.point = True
    ammonium.source = {}
    ammonium.source["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry , Extracted March 3, 2023. ICES, Copenhagen"
    ammonium.source["nsbc"] = "Hinrichs,Iris; Gouretski,Viktor; Paetsch,Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1). URL: <https://www.cen.uni-hamburg.de/en/icdc/data/ocean/nsbc.html>"
    ammonium.short_name = "ammonium"
    ammonium.short_title = "Ammonium"
    ammonium.long_name = "ammonium concentration"
    ammonium.model_variable = "auto"
    keys.append("ammonium")


    # pco2
    pco2 = Variable()
    pco2.gridded = False
    pco2.point = True
    pco2.source = {}
    pco2.source["socat23"] = "Bakker, Dorothee C. E.; Alin, Simone R.; Bates, Nicholas; Becker, Meike; Feely, Richard A.; Gkritzalis, Thanos; Jones, Steve D.; Kozyr, Alex; Lauvset, Siv K.; Metzl, Nicolas; Munro, David R.; Nakaoka, Shin-ichiro; Nojiri, Yukihiro; O'Brien, Kevin M.; Olsen, Are; Pierrot, Denis; Rehder, Gregor; Steinhoff, Tobias; Sutton, Adrienne J.; Sweeney, Colm; Tilbrook, Bronte; Wada, Chisato; Wanninkhof, Rik; Akl, John; Barbero, Leticia; Beatty, Cory M.; Berghoff, Carla F.; Bittig, Henry C.; Bott, Randy; Burger, Eugene F.; Cai, Wei-Jun; Castaño-Primo, Rocío; Corredor, Jorge E.; Cronin, Margot; De Carlo, Eric H.; DeGrandpre, Michael D.; Dietrich, Colin; Drennan, William M.; Emerson, Steven R.; Enochs, Ian C.; Enyo, Kazutaka; Epherra, Lucía; Evans, Wiley; Fiedler, Björn; Fontela, Marcos; Frangoulis, Constantin; Gehrung, Martina; Giannoudi, Louisa; Glockzin, Michael; Hales, Burke; Howden, Stephan D.; Ibánhez, J. Severino P.; Kamb, Linus; Körtzinger, Arne; Lefèvre, Nathalie; Lo Monaco, Claire; Lutz, Vivian A.; Macovei, Vlad A.; Maenner Jones, Stacy; Manalang, Dana; Manzello, Derek P.; Metzl, Nicolas; Mickett, John; Millero, Frank J.; Monacci, Natalie M.; Morell, Julio M.; Musielewicz, Sylvia; Neill, Craig; Newberger, Tim; Newton, Jan; Noakes, Scott; Ólafsdóttir, Sólveig Rósa; Ono, Tsuneo; Osborne, John; Padín, Xose A.; Paulsen, Melf; Perivoliotis, Leonidas; Petersen, Wilhelm; Petihakis, George; Plueddemann, Albert J.; Rodriguez, Carmen; Rutgersson, Anna; Sabine, Christopher L.; Salisbury, Joseph E.; Schlitzer, Reiner; Skjelvan, Ingunn; Stamataki, Natalia; Sullivan, Kevin F.; Sutherland, Stewart C.; T'Jampens, Michiel; Tadokoro, Kazuaki; Tanhua, Toste; Telszewski, Maciej; Theetaert, Hannelore; Tomlinson, Michael; Vandemark, Douglas; Velo, Antón; Voynova, Yoana G.; Weller, Robert A.; Whitehead, Chris; Wimart-Rousseau, Cathy (2023). Surface Ocean CO2 Atlas Database Version 2023 (SOCATv2023) (NCEI Accession 0278913). [indicate subset used]. NOAA National Centers for Environmental Information. Dataset. <https://doi.org/10.25921/r7xa-bt92>. Accessed [25/04/2024]."
    pco2.short_name = "pCO<sub>2</sub>" 
    pco2.short_title = "pCO<sub>2</sub>" 
    pco2.long_name = "partial pressure of CO<sub>2</sub>"
    pco2.model_variable = "auto"
    keys.append("pco2")

    # ph
    ph = Variable()
    ph.gridded = False
    ph.point = True
    ph.source = {}
    ph.source["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry , Extracted March 3, 2023. ICES, Copenhagen"
    ph.short_name = "pH"
    ph.short_title = "pH"
    ph.long_name = "pH"
    ph.model_variable = "auto"
    keys.append("ph")


    # salinity
    salinity = Variable()
    salinity.gridded = True
    salinity.point = True
    salinity.source = {}
    salinity.source["nsbc"] = "Hinrichs,Iris; Gouretski,Viktor; Paetsch,Johannes; Emeis, Kay; Stammer, Detlef (2017). North Sea Biogeochemical Climatology (Version 1.1). URL: <https://www.cen.uni-hamburg.de/en/icdc/data/ocean/nsbc.html>"
    salinity.source["ices"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry , Extracted March 3, 2023. ICES, Copenhagen"
    salinity.short_name = "salinity"    
    salinity.short_title = "Salinity"
    salinity.long_name = "salinity"
    salinity.model_variable = "auto"
    keys.append("salinity")

    # temperature
    temperature = Variable()
    temperature.gridded = True
    temperature.point = True
    temperature.source = {}
    temperature.source["ostia"] =  "Good, S.; Fiedler, E.; Mao, C.; Martin, M.J.; Maycock, A.; Reid, R.; Roberts-Jones, J.; Searle, T.; Waters, J.; While, J.; Worsfold, M. The Current Configuration of the OSTIA System for Operational Production of Foundation Sea Surface Temperature and Ice Concentration Analyses. Remote Sens. 2020, 12, 720, doi:10.3390/rs12040720. \n URL: <https://data.marine.copernicus.eu/product/SST_GLO_SST_L4_REP_OBSERVATIONS_010_011/description> \n From 2022 onwards, the near-real time product is used: <https://data.marine.copernicus.eu/product/SST_GLO_SST_L4_NRT_OBSERVATIONS_010_001/description>"
    temperature.short_name = "temperature"  
    temperature.short_title = "Temperature"
    temperature.long_name = "temperature"
    temperature.model_variable = "auto"
    keys.append("temperature")

    # co2flux
    co2flux = Variable()
    co2flux.gridded = True
    co2flux.point = False
    co2flux.source = {}
    co2flux.source["ncei"] = "Jersild, Annika; Landschützer, Peter; Gruber, Nicolas; Bakker, Dorothee C. E. (2017). An observation-based global monthly gridded sea surface pCO2 and air-sea CO2 flux product from 1982 onward and its monthly climatology (NCEI Accession 0160558). Version 7.7. [v 2022]. NOAA National Centers for Environmental Information. Dataset. https://doi.org/10.7289/v5z899n6. Accessed [2025-11-04] URL: <https://www.ncei.noaa.gov/data/oceans/ncei/ocads/data/0160558/MPI_SOM-FFN_v2022/>"
    co2flux.short_name = "air-sea CO2<sub>2</sub> fluxes" 
    co2flux.short_title = "CO2<sub>2</sub> fluxes"
    co2flux.long_name = "air-sea CO2<sub>2</sub> fluxes" 
    co2flux.model_variable = "auto"
    keys.append("co2flux")


    # alkalinity
    alkalinity = Variable()
    alkalinity.gridded = True
    alkalinity.point = True
    alkalinity.source = {}
    alkalinity.source["glodap"] = "Lauvset, S. K., Key, R. M., Olsen, A., van Heuven, S., Velo, A., Lin, X., Schirnick, C., Kozyr, A., Tanhua, T., Hoppema, M., Jutterström, S., Steinfeldt, R., Jeansson, E., Ishii, M., Perez, F. F., Suzuki, T., and Watelet, S.: A new global interior ocean mapped climatology: the 1° ×  1° GLODAP version 2, Earth Syst. Sci. Data, 8, 325–340, https://doi.org/10.5194/essd-8-325-2016, 2016."
    alkalinity.source["various"] =  "ICES Data Portal, Dataset on Ocean HydroChemistry, Extracted March 3, 2023. ICES, Copenhagen. \n Olsen, A., R. M. Key, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Pérez and T. Suzuki. The Global Ocean Data Analysis Project version 2 (GLODAPv2) – an internally consistent data product for the world ocean, Earth Syst. Sci. Data, 8, 297–323, 2016, doi:10.5194/essd-8-297-2016. \nKey, R.M., A. Olsen, S. van Heuven, S. K. Lauvset, A. Velo, X. Lin, C. Schirnick, A. Kozyr, T. Tanhua, M. Hoppema, S. Jutterström, R. Steinfeldt, E. Jeansson, M. Ishii, F. F. Perez, and T. Suzuki. 2015. Global Ocean Data Analysis Project, Version 2 (GLODAPv2), ORNL/CDIAC-162, NDP-093. Carbon Dioxide Information Analysis Center, Oak Ridge National Laboratory, US Department of Energy, Oak Ridge, Tennessee. doi:10.3334/CDIAC/OTG.NDP093_GLODAPv2."
    alkalinity.short_name = "alkalinity"
    alkalinity.short_title = "Alkalinity"
    alkalinity.long_name = "total alkalinity"
    alkalinity.model_variable = "auto"
    keys.append("alkalinity")

    # now kd
    kd = Variable()
    kd.gridded = True
    kd.point = False
    kd.source = {}
    kd.source["cmems"] = "URL: <https://doi.org/10.48670/moi-00281>" 
    kd.short_name = "kd" 
    kd.short_title = "kd"
    kd.long_name = "light attenuation"
    kd.model_variable = "auto"
    keys.append("kd")

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
    # use the set_all method
    def add_variable(self, name, long_name, short_name, short_title, gridded, point, source, model_variable): 
        var = Variable()
        var.long_name = long_name
        var.short_name = short_name
        var.short_title = short_title
        var.gridded = gridded
        var.point = point
        var.source = source
        var.model_variable = model_variable
        # ensure nothing is None
        for attr in [var.long_name, var.short_name, var.short_title, var.source, var.model_variable]:
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
    ds_contents = ds_contents.query("nlevels > 1").reset_index(drop=True)
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
            model_dict[vv] = definitions[vv].model_variable
            continue

        if vv != "ph":
            the_vars = [
                x
                for x in [str(x) for x in ds_contents.long_name]
                if vv_check.lower() in x.lower()
                and "benthic" not in x.lower()
                and "river" not in x.lower()
            ]
        if vv == "temperature":
            the_vars = [
                x
                for x in [str(x) for x in ds_contents.long_name]
                if vv_check.lower() in x.lower()
                and "benthic" not in x.lower()
                and "air" not in x.lower()
                and "river" not in x.lower()
            ]
        if vv == "spm":
            the_vars = [
                x for x in ds_contents.long_name if "chloroph" in x and ("micro" in x)
            ]

        if vv == "benbio":
            the_vars = [
                x
                for x in ds_contents_top.long_name
                if "carbon" in x
                and ("feeder" in x.lower() or "predator" in x.lower())
                and "uptake" not in x.lower()
                and "penetr" not in x.lower()
            ]

        if vv == "ph":
            the_vars = [
                x
                for x in ds_contents.long_name
                if ("pH" in x)
                or (" ph " in x)
                and "benthic" not in x.lower()
                and "river" not in x.lower()
            ]
            if len(the_vars) == 0:
                if len(ds_contents.query("variable == 'ph'")) > 0:
                    the_vars = list(ds_contents.query("variable == 'ph'").long_name)

        if vv == "co2flux":
            the_vars = [
                x
                for x in ds_contents_top.long_name
                if "co2" in x.lower()
                and "flux" in x.lower()
                and "river" not in x.lower()
            ]

        if vv == "pco2":
            the_vars = [
                x
                for x in ds_contents.long_name
                if "carbonate" in x.lower()
                and "partial" in x.lower()
                and "river" not in x.lower()
            ]

        if vv == "silicate":
            the_vars = [
                x
                for x in ds_contents.long_name
                if ("silicate" in x.lower() or "silicic" in x.lower())
                and "benthic" not in x.lower()
                and "river" not in x.lower()
            ]

            if len(the_vars) > 1:
                the_vars_2 = [
                    x
                    for x in ds_contents.long_name
                    if "benthic" not in x.lower() and "river" not in x.lower()
                ]
                the_vars_2 = [
                    x for x in the_vars_2 if re.match(r"silicate.silicate", x)
                ]
                if len(the_vars_2) == 1:
                    the_vars = the_vars_2

        if vv == "oxygen":
            the_vars = [
                x
                for x in ds_contents.long_name
                if "oxygen" in x.lower()
                and "benthic" not in x.lower()
                and "saturation" not in x.lower()
                and "util" not in x.lower()
                and "flux" not in x.lower()
                and "river" not in x.lower()
            ]


        if vv == "kd":
            the_vars = [
                x
                for x in ds_contents.long_name
                if "atten" in x.lower() and "coeff" in x.lower()
            ]

        if vv == "chlorophyll":
            if len(the_vars) > 1:
                the_vars = [x for x in the_vars if "total" not in x.lower()]

        if vv in [ "benbio"]:
            model_vars = ds_contents_top.query("long_name in @the_vars").variable
        else:
            if vv != "co2flux" and vv != "pco2":
                model_vars = ds_contents.query("long_name in @the_vars").variable
            else:
                if vv == "co2flux":
                    model_vars = ds_contents_top.query(
                        "long_name in @the_vars"
                    ).variable
                else:
                    model_vars = ds_contents.query("long_name in @the_vars").variable

        add = True

        if len(model_vars) > 1 and vv not in [
            "chlorophyll",
            "benbio",
            "micro"
        ]:
            add = False

        if add:
            if len(model_vars) > 0:
                model_dict[vv] = "+".join(model_vars)
            else:

                if "nitrate" not in model_dict.keys() and vv == "nitrate":
                    if "ammonium" not in model_dict.keys():
                        df_nitrogen = (
                            ds_contents.query("long_name.str.contains('nitrogen')")
                            .query("long_name.str.contains('nutrient')")
                            .reset_index(drop=True)
                        )
                        if len(df_nitrogen) == 1:
                            model_dict["nitrate"] = df_nitrogen.variable[0]
                            warnings.warn(
                                "No nitrate variable found, using nitrogen nutrient variable"
                            )

                if vv not in model_dict.keys():
                    model_dict[vv] = None
    return model_dict


