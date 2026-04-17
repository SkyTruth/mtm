library(dplyr)

#------------------------------------------------------------------------------
# LOAD CLEANED DATA
#------------------------------------------------------------------------------

# Define directory paths
cleaned_dir <- "cleaned"
results_dir <- "results"

# Load dataframes
segments <- read.csv(file.path(cleaned_dir, "segments.csv"))
highwalls <- read.csv(file.path(cleaned_dir, "highwalls.csv"))

#------------------------------------------------------------------------------
# BASIC SUMMARY STATS BY STATE AND TOTAL
#------------------------------------------------------------------------------

# Summarize segment stats by state
segment_stats <- segments %>%
  group_by(State) %>%
  summarize(avg_height = mean(Height),
    avg_height_weighted = weighted.mean(Height, Length)
  ) %>%
  bind_rows(
    .,
    tibble(
      State = "Total",
      avg_height = mean(segments$Height),
      avg_height_weighted = weighted.mean(segments$Height, segments$Length)
    )
  )
# print(segment_stats)


# Summarize highwall stats by state
highwall_stats <- highwalls %>%
  group_by(State) %>%
  summarize(
    num_highwalls = n_distinct(Highwall_ID),
    median_num_segments = median(Num_Segments),
    unrec_highwalls = sum(Rec_Status == "Unreclaimed"),
    reveg_highwalls = sum(Rec_Status == "Revegetated"),
    bonded_highwalls = sum(Bond_Status == "Bonded"),
    forfeited_highwalls = sum(Bond_Status == "Forfeited"),
    released_highwalls = sum(Bond_Status == "Released"),
    notbonded_highwalls = sum(Bond_Status == "Not Bonded"),
    num_segments = sum(Num_Segments),
    hw_length_km = sum(Length) / 1000,
    min_cost = sum(Min_Cost),
    mid_cost = sum(Mid_Cost),
    max_cost = sum(Max_Cost),
    avg_max_age = mean(Max_Age, na.rm = TRUE),
    avg_min_age = mean(Min_Age, na.rm = TRUE),
    avg_mid_age = mean(Mid_Age, na.rm = TRUE),
    avg_age_uncertainty = mean(Age_Uncertainty, na.rm = TRUE)
  ) %>%
  bind_rows(
    .,
    tibble(
      State = "Total",
      num_highwalls = n_distinct(highwalls$Highwall_ID),
      median_num_segments = median(highwalls$Num_Segments),
      unrec_highwalls = sum(highwalls$Rec_Status == "Unreclaimed"),
      reveg_highwalls = sum(highwalls$Rec_Status == "Revegetated"),
      bonded_highwalls = sum(highwalls$Bond_Status == "Bonded"),
      forfeited_highwalls = sum(highwalls$Bond_Status == "Forfeited"),
      released_highwalls = sum(highwalls$Bond_Status == "Released"),
      notbonded_highwalls = sum(highwalls$Bond_Status == "Not Bonded"),
      num_segments = sum(highwalls$Num_Segments),
      hw_length_km = sum(highwalls$Length) / 1000,
      min_cost = sum(highwalls$Min_Cost),
      mid_cost = sum(highwalls$Mid_Cost),
      max_cost = sum(highwalls$Max_Cost),
      avg_max_age = mean(highwalls$Max_Age, na.rm = TRUE),
      avg_min_age = mean(highwalls$Min_Age, na.rm = TRUE),
      avg_mid_age = mean(highwalls$Mid_Age, na.rm = TRUE),
      avg_age_uncertainty = mean(highwalls$Age_Uncertainty, na.rm = TRUE)
    )
  )
# View(highwall_stats)


# Summarize permit stats by state
permit_stats <- all_permits %>%
  group_by(State) %>%
  summarize(
    num_hw_permits = n_distinct(Permit_ID),
    num_hw_companies = n_distinct(Permittee, na.rm = TRUE),
    released_permits = sum(Bond_Status == "Released"),
    forfeited_permits = sum(Bond_Status == "Forfeited"),
    bonded_permits = sum(Bond_Status == "Bonded"),
    notbonded_permits = sum(Bond_Status == "Not Bonded"),
    avail_bond = sum(Avail_Bond, na.rm = TRUE),
    full_bond = sum(Full_Bond, na.rm = TRUE),
    min_deficit = sum(Min_Deficit, na.rm = TRUE),
    mid_deficit = sum(Mid_Deficit, na.rm = TRUE),
    max_deficit = sum(Max_Deficit, na.rm = TRUE),
    positive_min_deficit = sum(Min_Deficit[Min_Deficit > 0], na.rm = TRUE),
    positive_mid_deficit = sum(Mid_Deficit[Mid_Deficit > 0], na.rm = TRUE),
    positive_max_deficit = sum(Max_Deficit[Max_Deficit > 0], na.rm = TRUE)
  ) %>%
  bind_rows(
    .,
    tibble(
      State = "Total",
      num_hw_permits = n_distinct(all_permits$Permit_ID),
      num_hw_companies = n_distinct(all_permits$Permittee, na.rm = TRUE),
      released_permits = sum(all_permits$Bond_Status == "Released"),
      forfeited_permits = sum(all_permits$Bond_Status == "Forfeited"),
      bonded_permits = sum(all_permits$Bond_Status == "Bonded"),
      notbonded_permits = sum(all_permits$Bond_Status == "Not Bonded"),
      avail_bond = sum(all_permits$Avail_Bond, na.rm = TRUE),
      full_bond = sum(all_permits$Full_Bond, na.rm = TRUE),
      min_deficit = sum(all_permits$Min_Deficit, na.rm = TRUE),
      mid_deficit = sum(all_permits$Mid_Deficit, na.rm = TRUE),
      max_deficit = sum(all_permits$Max_Deficit, na.rm = TRUE),
      positive_min_deficit = sum(all_permits$Min_Deficit[all_permits$Min_Deficit > 0], na.rm = TRUE),
      positive_mid_deficit = sum(all_permits$Mid_Deficit[all_permits$Mid_Deficit > 0], na.rm = TRUE),
      positive_max_deficit = sum(all_permits$Max_Deficit[all_permits$Max_Deficit > 0], na.rm = TRUE)
    )
  )
# View(permit_stats)

#------------------------------------------------------------------------------
# ADDITIONAL ANALYSIS QUESTIONS
#------------------------------------------------------------------------------

# What percentage of bond money will highwall reclamation take up,
# and what percentage will be left over for other forms of reclamation?

total_hw_bond_pct <- all_permits %>%
  group_by(State) %>%
  summarize(
    bonds = sum(Full_Bond, na.rm = TRUE),
    hw_cost = sum(Highwall_Cost_Mid, na.rm = TRUE),
    highwall_percentage = (hw_cost / bonds) * 100
  ) %>%
  bind_rows(
    .,
    tibble(
      State = "Total",
      bonds = sum(all_permits$Full_Bond, na.rm = TRUE),
      hw_cost = sum(all_permits$Highwall_Cost_Mid, na.rm = TRUE),
      highwall_percentage = (hw_cost / bonds) * 100
    )
  )
# print(total_hw_bond_pct)

# Across all permits with highwalls, highwall reclamation will take up
# 47% of bond funds.


# In permits where bonds exceed highwall costs, what percentage of
# bonds will highwall reclamation consume?

# Calculate highwall costs as a percentage of bonds for each permit
all_permits <- all_permits %>%
  mutate(
    Hw_Percentage = if_else(
      Full_Bond > 0,
      (Highwall_Cost_Mid / Full_Bond) * 100,
      NA_real_
    )
  )

highwall_pct_by_permit <- all_permits %>%
  filter(Full_Bond > Highwall_Cost_Mid) %>%
  group_by(State) %>%
  summarize(
    avg_hw_percentage = mean(Hw_Percentage, na.rm = TRUE)
  ) %>%
  bind_rows(
    .,
    tibble(
      State = "Total",
      avg_hw_percentage = mean(all_permits$Hw_Percentage
      [all_permits$Full_Bond > all_permits$Highwall_Cost_Mid],
      na.rm = TRUE)
    )
  )

# print(highwall_pct_by_permit)

# In permits where bonds exceed highwall costs, highwall reclamation will
# consume 31% of bonds on average.


# How many bonded permits are bankrupted by highwalls?
# How many permits have highwalls but are unbonded?

bankrupted_permits <- all_permits %>%
  group_by(State) %>%
  summarize(
    total_bankrupted = sum(Mid_Deficit > 0, na.rm = TRUE),
    bonded_bankrupted = sum(Mid_Deficit > 0 & Full_Bond > 0, na.rm = TRUE),
    unbonded_bankrupted = sum(Mid_Deficit > 0 & Full_Bond == 0, na.rm = TRUE)
  ) %>%
  bind_rows(
    .,
    tibble(
      State = "Total",
      total_bankrupted = sum(all_permits$Mid_Deficit > 0, na.rm = TRUE),
      bonded_bankrupted = sum(all_permits$Mid_Deficit > 0
                              & all_permits$Full_Bond > 0, na.rm = TRUE),
      unbonded_bankrupted = sum(all_permits$Mid_Deficit > 0
                                & all_permits$Full_Bond == 0, na.rm = TRUE)
    )
  )
# print(bankrupted_permits)

# 254 permits are bankrupted by highwalls.
# 95 of these are bonded, 159 are unbonded.


# Among underbonded permits (bonded permits bankrupted by highwalls),
# what is the average deficit?

underbonded_deficit <- all_permits %>%
  filter(Mid_Deficit > 0 & Full_Bond > 0) %>%
  group_by(State) %>%
  summarize(avg_underbonded_deficit = mean(Mid_Deficit, na.rm = TRUE)) %>%
  bind_rows(
    .,
    tibble(
      State = "Total",
      avg_underbonded_deficit = mean(all_permits$Mid_Deficit
      [all_permits$Mid_Deficit > 0 & all_permits$Full_Bond > 0], na.rm = TRUE)
    )
  )

# print(underbonded_deficit)

# Among underbonded permits, the average deficit is $508,725.

#------------------------------------------------------------------------------
# SAVE RESULTS
#------------------------------------------------------------------------------

# Combine all statistics into a single tibble
format_stats <- function(df) {
  df %>%
    select(-"State") %>%
    t() %>%
    as_tibble(rownames = "statistic") %>%
    setNames(c("statistic", df$State))
}
combined_stats <- bind_rows(
  format_stats(segment_stats),
  format_stats(highwall_stats),
  format_stats(permit_stats),
  format_stats(total_hw_bond_pct),
  format_stats(highwall_pct_by_permit),
  format_stats(bankrupted_permits),
  format_stats(underbonded_deficit)
)
# View(combined_stats)

# Write combined statistics to CSV
write.csv(combined_stats, file.path(results_dir, "summary_stats.csv"), row.names = FALSE)