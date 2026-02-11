# V-Dem Data Extraction Script
# Extracts v2x_libdem (Liberal Democracy) and v2x_delibdem (Polarization) indicators
# Output: data_intermediate/vdem_extracted.csv in standard format

# Install packages if needed (uncomment if first run)
# install.packages("devtools")
# devtools::install_github("vdeminstitute/vdemdata")

library(vdemdata)
library(dplyr)
library(tidyr)

# Target countries and their V-Dem names
target_countries <- c(
  "Denmark",
  "United States of America",
  "United Kingdom",
  "Bosnia and Herzegovina",
  "Cyprus"
)

# Year range
year_start <- 2010
year_end <- 2025

# Extract data for target countries
vdem_extract <- vdem %>%
  filter(
    country_name %in% target_countries,
    year >= year_start,
    year <= year_end
  ) %>%
  select(
    country_name,
    year,
    v2x_libdem,
    v2x_delibdem
  ) %>%
  # Standardize country names
  mutate(
    country = case_when(
      country_name == "United States of America" ~ "United States",
      TRUE ~ country_name
    )
  ) %>%
  select(country, year, v2x_libdem, v2x_delibdem)

# Convert to long format (standard format)
vdem_long <- vdem_extract %>%
  pivot_longer(
    cols = c(v2x_libdem, v2x_delibdem),
    names_to = "indicator_raw",
    values_to = "value"
  ) %>%
  mutate(
    indicator = case_when(
      indicator_raw == "v2x_libdem" ~ "Liberal Democracy",
      indicator_raw == "v2x_delibdem" ~ "Polarization"
    ),
    source = "V-Dem"
  ) %>%
  select(country, year, indicator, value, source) %>%
  filter(!is.na(value))

# Print summary
print("============================================================")
print("V-Dem Data Extraction")
print("============================================================")
print(paste("Total records:", nrow(vdem_long)))
print("Countries:")
print(unique(vdem_long$country))
print("")
print("Records per country/indicator:")
print(table(vdem_long$country, vdem_long$indicator))

# Get output directory
args <- commandArgs(trailingOnly = FALSE)
script_path <- sub("--file=", "", args[grep("--file=", args)])

if (length(script_path) > 0 && nchar(script_path) > 0) {
  script_dir <- dirname(script_path)
  output_dir <- file.path(dirname(script_dir), "data_intermediate")
} else {
  output_dir <- file.path(getwd(), "data_intermediate")
}

if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

output_path <- file.path(output_dir, "vdem_extracted.csv")

# Save to CSV
write.csv(vdem_long, output_path, row.names = FALSE)
print(paste("Saved V-Dem data to:", output_path))

