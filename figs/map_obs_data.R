
library(tidyverse)
library(arrow)

read_variable <- function(df, vv){
  print(vv)
  df %>% 
    mutate(data = map(path, read_feather)) %>% 
    unnest(data) %>% 
    select(-path) %>% 
    select(lon, lat) %>% 
    distinct() %>% 
    mutate(lon_1 = plyr::round_any(lon, 0.1), 
           lat_1 = plyr::round_any(lat, 0.1)) %>% 
    group_by(lon_1, lat_1) %>% 
    sample_n(10, replace = TRUE) %>%
    ungroup() %>% 
    select(lon, lat) %>% 
    distinct() %>% 
    filter(lon > -20, lon <10) %>% 
    filter(lat > 40, lat < 65)
  
}
df_variables <- fs::dir_info("/data/thaumus2/scratch/common/ecovalcore/point/", recurse = TRUE) %>% 
  select(path) %>% 
  filter(!str_detect(path, "units")) %>% 
  filter(!str_detect(path, "profile")) %>% 
  # get the basename
  mutate(basename = basename(path)) %>% 
  filter(str_detect(path, "feat")) %>% 
  separate(basename, into = c("source", "variable", "year")) %>% 
  mutate(variable = ifelse(str_detect(path, "benbio"), "Benthic biomass", variable)) %>% 
  mutate(variable = ifelse(str_detect(path, "carbon"), "Sediment carbon", variable)) %>% 
  mutate(variable = ifelse(str_detect(path, "oxycons"), "Benthic oxygen consumption", variable)) %>% 
  filter(variable != "nitrogen") %>% 
  filter(variable != "nitrite") %>% 
  filter(variable != "phosphorus") %>% 
  select(path, variable) %>% 
  # capitalize variable
  mutate(variable = str_to_title(variable)) %>%
  mutate(variable = ifelse(variable == "Poc", "POC", variable)) %>%
  mutate(variable = ifelse(variable == "Doc", "DOC", variable)) %>%
  mutate(variable = ifelse(variable == "Ph", "pH", variable)) %>%
  mutate(variable = ifelse(variable == "Pco2", "pCO2", variable)) %>%
  mutate(variable = ifelse(variable == "Mesozoo", "Mesozooplankton", variable)) %>%
  mutate(variable = ifelse(variable == "Pft", "PFTs", variable)) %>%
  group_by(variable) %>% 
  nest() %>% 
  mutate(data = map(data, read_variable, vv = variable))

world_map <- map_data("world")

df_variables <- df_variables %>% 
  unnest(data) 

gg <- df_variables %>% 
  filter(variable != "Bottom") %>% 
  mutate(variable = str_replace(variable, "Benthic Oxygen", "Benthic O2")) %>% 
  # remove anything in the Mediterranean
  filter(!(lon > 0 & lon < 20 & lat < 45 & lat > 35)) %>%
  ggplot()+
  geom_point(aes(lon, lat), size = 0.5)+
  geom_polygon(data = world_map, aes(x = long, y = lat, group = group), fill = "grey60")+
  facet_wrap(~variable, ncol = 4)+
  coord_fixed(xlim = c(min(df_variables$lon), max(df_variables$lon)), 
               ylim = c(min(df_variables$lat), max(df_variables$lat)), ratio = 1.5)+
  # ditch the x and y axes
  theme_bw(base_size = 18)+
  theme(
    axis.text = element_blank(),
    axis.ticks = element_blank(),
    axis.title = element_blank(),
    panel.background = element_rect(fill = "white"),
    panel.grid = element_blank(),
    strip.background = element_rect(fill = "grey80")
  )+
  coord_sf(expand = FALSE, xlim = c(-20, 10), ylim = c(40, 65), 
           default_crs = sf::st_crs(4326)) 

ggsave("~/projects/ecoValCore/figs/map_point_data.png", gg, width = 20, height = 20 * 0.7, dpi = 300)

read_netcdf <- function(ff){
  df <- tidync::hyper_tibble(ff,
                             force = TRUE)
                             # first time stpe
  if ("longitude" %in% names(df)) {
    df <- df %>% 
    rename(lon = longitude, lat = latitude)
  }
  df %>% 
    select(lon, lat) %>% 
    distinct() %>% 
    mutate(lon = as.numeric(lon)) %>% 
    mutate(lat = as.numeric(lat)) 
  
}

df_gridded <- fs::dir_info("/data/thaumus2/scratch/common/ecovalcore/gridded/nws", recurse = TRUE) %>% 
  # only netcdf
  filter(str_detect(path, "\\.nc$")) %>% 
  select(path) %>% 
  filter(!str_detect(path, "benthic")) %>% 
  mutate(dirname = dirname(path)) %>% 
  # base directory
  mutate(basename = basename(dirname)) %>% 
  select(path, dirname) %>% 
  mutate(dirname = str_replace(dirname,"/data/thaumus2/scratch/common/ecovalcore/gridded/", "")) %>% 
    separate(dirname, into = c("ignore", "variable")) %>% 
  group_by(variable) %>% 
  sample_n(1) %>% 
  mutate(data = purrr::map(path, read_netcdf)) 
df_gridded <- df_gridded %>% 
  mutate(variable = str_to_title(variable)) %>%
  mutate(variable = ifelse(variable == "Poc", "POC", variable)) %>%
  mutate(variable = ifelse(variable == "Doc", "DOC", variable)) %>%
  mutate(variable = ifelse(variable == "Ph", "pH", variable)) %>%
  mutate(variable = ifelse(variable == "Pco2", "pCO2", variable)) %>%
  mutate(variable = ifelse(variable == "Mesozoo", "Mesozooplankton", variable)) %>%
  mutate(variable = ifelse(variable == "Pft", "PFTs", variable)) 

gg <- df_gridded %>% 
  filter(variable != "inorganic") %>% 
  select(variable, data) %>% 
  unnest() %>% 
  ggplot()+
  geom_raster(aes(lon, lat))+
  geom_polygon(data = world_map, aes(x = long, y = lat, group = group), fill = "grey60")+
  facet_wrap(~variable, ncol = 5)+
  coord_sf(expand = FALSE, xlim = c(-20, 10), ylim = c(40, 65), 
           default_crs = sf::st_crs(4326)) +
  # ditch the x and y axes
  theme_bw(base_size = 18)+
  theme(
    axis.text = element_blank(),
    axis.ticks = element_blank(),
    axis.title = element_blank(),
    panel.background = element_rect(fill = "white"),
    panel.grid = element_blank(),
    strip.background = element_rect(fill = "grey80")
  )

ggsave("~/projects/ecoValCore/figs/map_gridded_data_nws.png", gg, width = 20, height = 20 * 0.6, dpi = 300)
  
  
df_gridded <- fs::dir_info("/data/thaumus2/scratch/common/ecoval/gridded/global", recurse = TRUE) %>% 
  # only netcdf
  filter(str_detect(path, "\\.nc$")) %>% 
  select(path) %>% 
  filter(!str_detect(path, "benthic")) %>% 
  mutate(dirname = dirname(path)) %>% 
  # base directory
  mutate(basename = basename(dirname)) %>% 
  select(path, dirname) %>% 
  mutate(dirname = str_replace(dirname,"/data/thaumus2/scratch/common/ecoval/gridded/", "")) %>% 
    separate(dirname, into = c("ignore", "variable")) %>% 
  group_by(variable) %>% 
  sample_n(1) %>% 
  mutate(data = purrr::map(path, read_netcdf)) 

df_gridded <- df_gridded %>% 
  mutate(variable = str_to_title(variable)) %>%
  mutate(variable = ifelse(variable == "Poc", "POC", variable)) %>%
  mutate(variable = ifelse(variable == "Doc", "DOC", variable)) %>%
  mutate(variable = ifelse(variable == "Ph", "pH", variable)) %>%
  mutate(variable = ifelse(variable == "Pco2", "pCO2", variable)) %>%
  mutate(variable = ifelse(variable == "Mesozoo", "Mesozooplankton", variable)) %>%
  mutate(variable = ifelse(variable == "Pft", "PFTs", variable)) 

gg <- df_gridded %>% 
  filter(variable != "inorganic") %>% 
  select(variable, data) %>% 
  unnest() %>% 
  ggplot()+
  geom_raster(aes(lon, lat))+
  geom_polygon(data = world_map, aes(x = long, y = lat, group = group), fill = "grey60")+
  facet_wrap(~variable, ncol = 5)+
  coord_sf(expand = FALSE,
           default_crs = sf::st_crs(4326)) +
  # ditch the x and y axes
  theme_bw(base_size = 18)+
  theme(
    axis.text = element_blank(),
    axis.ticks = element_blank(),
    axis.title = element_blank(),
    panel.background = element_rect(fill = "white"),
    panel.grid = element_blank(),
    strip.background = element_rect(fill = "grey80")
  )

ggsave("~/projects/ecoValCore/figs/map_gridded_data_globals.png", gg, width = 20, height = 20 * 0.6, dpi = 300)
  


library(tidyverse)


arrow::read_feather("/data/thaumus2/scratch/common/ecovalcore/point/nws/all/pco2/socat23_pco2.feather") %>% 
  filter(year == 2010) %>% 
  filter(between(lon, -20, 9)) %>% 
  filter(between(lat, 45, 65)) %>% 
  ggplot(aes(lon, lat))+
  geom_point()


df <- read_csv("/data/proteus1/scratch/rwi/ecoval_testing/matched/point/nws/surface/oxygen/ices_surface_oxygen.csv")
df
df <- read_csv("/data/proteus1/scratch/rwi/ecoval_testing/matched/point/nws/bottom/oxygen/ices_bottom_oxygen.csv")
df %>% 
  filter(depth < 150) %>% 
  ggplot(aes(lon, lat, colour = depth))+
  geom_point()

