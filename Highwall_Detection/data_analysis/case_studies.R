library(dplyr)

#------------------------------------------------------------------------------
# LOAD DATA
#------------------------------------------------------------------------------

# Define directory paths
input_dir <- "Highwall_Detection/data_analysis/inputs"
cleaned_dir <- "Highwall_Detection/data_analysis/cleaned"

# Load dataframes
all_permits <- read.csv(file.path(cleaned_dir, "all_permits.csv"))
highwalls <- read.csv(file.path(cleaned_dir, "highwalls.csv"))
wv_individual_bonds <- read.csv(file.path(input_dir, "wv_individual_bonds.csv"))
wv_permits <- read.csv(file.path(cleaned_dir, "wv_permits.csv"))
wv_permit_search <- read.csv(file.path(input_dir, "wv_permit_search.csv"))
ky_individual_bonds <- read.csv(file.path(input_dir, "ky_individual_bonds.csv"))
ky_permits <- read.csv(file.path(cleaned_dir, "ky_permits.csv"))


#------------------------------------------------------------------------------
# A & G COAL CORPORATION IN VIRGINIA
#------------------------------------------------------------------------------

A_and_G_VA_permits <- all_permits %>%
  filter(Permittee == "A & G COAL CORPORATION", State == "Virginia")

# View(A_and_G_VA_permits)

A_and_G_permit_stats <- A_and_G_VA_permits %>%
  group_by(Bond_Status) %>%
  summarize(length = sum(Highwall_Length, na.rm = TRUE),
            min_cost = sum(Highwall_Cost_Min, na.rm = TRUE),
            mid_cost = sum(Highwall_Cost_Mid, na.rm = TRUE),
            max_cost = sum(Highwall_Cost_Max, na.rm = TRUE),
            bond = sum(Full_Bond, na.rm = TRUE),
            min_deficit = sum(Min_Deficit, na.rm = TRUE),
            mid_deficit = sum(Mid_Deficit, na.rm = TRUE),
            max_deficit = sum(Max_Deficit, na.rm = TRUE))
# View(A_and_G_permit_stats)

A_and_G_VA_highwalls <- highwalls %>%
  filter(Permittee == "A & G COAL CORPORATION", State == "Virginia")
# View(A_and_G_VA_highwalls)

A_and_G_highwall_stats <- A_and_G_VA_highwalls %>%
  group_by(Bond_Status) %>%
  summarize(avg_min_age = mean(Min_Age, na.rm = TRUE),
            avg_height = mean(Avg_Height, na.rm = TRUE))
# print(A_and_G_highwall_stats)


#------------------------------------------------------------------------------
# INDEMNITY NATIONAL INSURANCE COMPANY IN WEST VIRGINIA
#------------------------------------------------------------------------------

wv_individual_bonds$Bond_Amount <- as.numeric(gsub(",", "", wv_individual_bonds$Bond_Amount))
wv_individual_bonds$Bond_Rate <- as.numeric(gsub(",", "", wv_individual_bonds$Bond_Rate))


# What percentage of bonds does Indemnity hold in WV?
bonds_sum <- sum(wv_individual_bonds$Bond_Amount, na.rm = TRUE)
indemnity_bonds <- wv_individual_bonds %>%
  filter(Bonding_Institution == "INDEMNITY NATIONAL INSURANCE COMPANY")
indemnity_bonds_sum <- sum(indemnity_bonds$Bond_Amount, na.rm = TRUE)
# print(indemnity_bonds_sum / bonds_sum * 100)
# 63.9% of bonds in WV are held by Indemnity.


# What percentage of bonds does Indemnity hold in WV permits with highwalls?
hw_bonds <- wv_individual_bonds %>%
  filter(PermitID %in% wv_permits$Permit_ID)
hw_bonds_sum <- sum(hw_bonds$Bond_Amount, na.rm = TRUE)
indemnity_hw_bonds <- hw_bonds %>%
  filter(Bonding_Institution == "INDEMNITY NATIONAL INSURANCE COMPANY")
indemnity_hw_bonds_sum <- sum(indemnity_hw_bonds$Bond_Amount, na.rm = TRUE)
# print(indemnity_hw_bonds_sum / hw_bonds_sum * 100)
# 64.7% of bonds in WV permits with highwalls are held by Indemnity.


# What proportion of bonded WV permits has at least one bond with Indemnity?
bonded_permit_count <- wv_individual_bonds %>%
  distinct(PermitID) %>%
  nrow()
indemnity_permit_count <- indemnity_bonds %>%
  distinct(PermitID) %>%
  nrow()
# print(indemnity_permit_count / bonded_permit_count * 100)
# 49.3% of bonded WV permits have at least one bond with Indemnity.


# What proportion of WV permits has all their bonds with Indemnity?
indemnity_only_permits <- wv_individual_bonds %>%
  group_by(PermitID) %>%
  filter(all(Bonding_Institution == "INDEMNITY NATIONAL INSURANCE COMPANY"))
indemnity_only_permit_count <- indemnity_only_permits %>%
  distinct(PermitID) %>%
  nrow()
# print(indemnity_only_permit_count / bonded_permit_count * 100)
# 48.0% of bonded WV permits have all their bonds with Indemnity.


# How many WV permits have some bonds with Indemnity and some bonds with other companies?
indemnity_mixed_permits <- wv_individual_bonds %>%
  group_by(PermitID) %>%
  filter(any(Bonding_Institution == "INDEMNITY NATIONAL INSURANCE COMPANY") &
         any(Bonding_Institution != "INDEMNITY NATIONAL INSURANCE COMPANY")) %>%
  distinct(PermitID)
# print(indemnity_mixed_permits %>% nrow())
# Only 22 permits have some bonds with Indemnity and some bonds with other companies.


# What proportion of WV permits with highwalls has at least one bond with Indemnity?
hw_permit_count <- wv_permits %>%
  distinct(Permit_ID) %>%
  nrow()
indemnity_hw_permit_count <- indemnity_hw_bonds %>%
  distinct(PermitID) %>%
  nrow()
# print(indemnity_hw_permit_count / hw_permit_count * 100)
# 46.9% of WV permits with highwalls have at least one bond with Indemnity.


# What proportion of WV permits with highwalls has all their bonds with Indemnity?
indemnity_only_hw_permit_count <- hw_bonds %>%
  group_by(PermitID) %>%
  filter(all(Bonding_Institution == "INDEMNITY NATIONAL INSURANCE COMPANY")) %>%
  distinct(PermitID) %>%
  nrow()

# print(indemnity_only_hw_permit_count / hw_permit_count * 100)
# 44.8% of WV permits with highwalls have all their bonds with Indemnity.


# How many WV permits with highwalls have some bonds with Indemnity and some bonds with other companies?
indemnity_mixed_hw_permit_count <- hw_bonds %>%
  group_by(PermitID) %>%
  filter(any(Bonding_Institution == "INDEMNITY NATIONAL INSURANCE COMPANY") &
         any(Bonding_Institution != "INDEMNITY NATIONAL INSURANCE COMPANY")) %>%
  distinct(PermitID) %>%
  nrow()
# print(indemnity_mixed_hw_permit_count)
# Only 3 permits with highwalls have some bonds with Indemnity and some bonds with other companies.


# What is the total cost of highwalls in WV permits bonded completely by Indemnity?
wv_indemnity_hw_permits <- all_permits %>%
  filter(Permit_ID %in% indemnity_only_permits$PermitID)
# View(wv_indemnity_hw_permits)

indemnity_hw_stats <- wv_indemnity_hw_permits %>%
  summarize(total_cost = sum(Highwall_Cost_Mid, na.rm = TRUE),
            total_bond = sum(Full_Bond, na.rm = TRUE))
# print(indemnity_hw_stats)
# total_cost = $65,803,940
# total_bond = $148,077,818

# What proportion of highwall reclamation costs in WV are insured by Indemnity?
wv_total_cost <- sum(wv_permits$Highwall_Cost_Mid, na.rm = TRUE)
# print(indemnity_hw_stats$total_cost / wv_total_cost * 100)


#------------------------------------------------------------------------------
# KRGF SUBSIDIES IN KENTUCKY
#------------------------------------------------------------------------------

ky_hw_bonds <- ky_individual_bonds %>%
  filter(Permit_ID %in% ky_permits$Permit_ID)

# How many highwall-bearing permits are subsidized by KRGF?
krgf_bonds <- ky_hw_bonds %>%
  filter(Bond_Institution %in% c("KY BOND POOL", "KENTUCKY RECLAMATION GUARANTY FUND")) %>%
  filter(Current_Bond_Amount > 0)
krgf_hw_permit_count <- krgf_bonds %>% distinct(Permit_ID) %>% nrow()
# print(krgf_hw_permit_count)
# 10 highwall-bearing permits are subsidized by KRGF


# What is the total subsidy amount from KRGF for highwall-bearing permits?
krgf_hw_bond_amount <- krgf_bonds %>% summarize(total_bond_amount = sum(Current_Bond_Amount, na.rm = TRUE))
# print(krgf_hw_bond_amount)
# Total subsidy amount from KRGF for highwall-bearing permits is $10,289,850


# Calculate the percentage of total bond amount from KRGF for each permit
krgf_permits <- ky_hw_bonds %>%
  filter(Current_Bond_Amount > 0) %>%
  group_by(Permit_ID) %>%
  filter(any(Bond_Institution %in% c("KY BOND POOL", "KENTUCKY RECLAMATION GUARANTY FUND")))
krgf_bond_percentage <- krgf_permits %>%
  group_by(Permit_ID) %>%
  summarize(
    total_bond = sum(Current_Bond_Amount, na.rm = TRUE),
    krgf_bond = sum(Current_Bond_Amount[Bond_Institution %in% c("KY BOND POOL", "KENTUCKY RECLAMATION GUARANTY FUND")], na.rm = TRUE),
    krgf_percentage = (krgf_bond / total_bond) * 100
  )
# Calculate the average percentage across all permits
avg_krgf_percentage <- mean(krgf_bond_percentage$krgf_percentage, na.rm = TRUE)
# print(avg_krgf_percentage)


# -----------------------------------------------------------------------------
# PER-ACRE BOND RATES IN WEST VIRGINIA
# -----------------------------------------------------------------------------

# Analyze all relevant performance bonds (not just those for highwall permits)
all_perf_bonds <- wv_individual_bonds %>%
  filter(PermitID %in% wv_permit_search$Permit_ID) %>% # within study region
  filter(grepl("^[SCIZH]", PermitID)) %>% # coal surface mining and haulroad permits only
  filter(Bond_Purpose == "PERF") %>% # performance bonds only
  filter(Current_Acres > 0) %>%
  mutate(Bond_Amount_per_Acre = Bond_Amount / Current_Acres) %>%
  mutate(expected_perf_bond = Bond_Rate * Current_Acres)

all_perf_bond_stats <- all_perf_bonds %>%
  summarize(min_bond_rate = min(Bond_Rate, na.rm = TRUE),
            max_bond_rate = max(Bond_Rate, na.rm = TRUE),
            avg_bond_rate = mean(Bond_Rate, na.rm = TRUE),
            weighted_avg_bond_rate = sum(Bond_Rate * Current_Acres, na.rm = TRUE) / sum(Current_Acres, na.rm = TRUE),
            n = nrow(all_perf_bonds))
# print(all_perf_bond_stats)

# Bond rates range from $1000 to $5000 per acre.
# Weighted average bond rate is $3,057 per acre.
# n = 1702 performance bonds


# Analyze relationship between bond rate and actual bond amount
log_model <- lm(
  log(Bond_Amount) ~ log(Bond_Rate) + log(Current_Acres),
  data = all_perf_bonds
)
# print(summary(log_model))


# Analyze bond rates for highwall permits only
hw_perf_bonds <- all_perf_bonds %>%
  filter(PermitID %in% wv_permits$Permit_ID)


# Calculate summary statistics for Bond_Rate values
hw_perf_bond_stats <- hw_perf_bonds %>%
  summarize(min_bond_rate = min(Bond_Rate, na.rm = TRUE),
            max_bond_rate = max(Bond_Rate, na.rm = TRUE),
            avg_bond_rate = mean(Bond_Rate, na.rm = TRUE),
            weighted_avg_bond_rate = sum(Bond_Rate * Current_Acres, na.rm = TRUE) / sum(Current_Acres, na.rm = TRUE),
            n = nrow(hw_perf_bonds))
# print(hw_perf_bond_stats)

# Weighted average bond rate is $3,547 per acre, n=547 bonds.


# Analyze bond rates for non-highwall permits only
no_hw_perf_bonds <- all_perf_bonds %>%
  filter(!PermitID %in% wv_permits$Permit_ID)

no_hw_perf_bond_stats <- no_hw_perf_bonds %>%
  summarize(min_bond_rate = min(Bond_Rate, na.rm = TRUE),
            max_bond_rate = max(Bond_Rate, na.rm = TRUE),
            avg_bond_rate = mean(Bond_Rate, na.rm = TRUE),
            weighted_avg_bond_rate = sum(Bond_Rate * Current_Acres, na.rm = TRUE) / sum(Current_Acres, na.rm = TRUE),
            n = nrow(no_hw_perf_bonds))
# print(no_hw_perf_bond_stats)

# Weighted average bond rate is $2,800 per acre, n=1,155 bonds.


# Analyze bond rates for underbonded highwall permits
underbonded_wv_permits <- wv_permits %>%
  filter(Mid_Deficit > 0, Bond_Status == "Bonded")

underbonded_hw_perf_bonds <- wv_individual_bonds %>%
  filter(PermitID %in% underbonded_wv_permits$Permit_ID) %>%
  filter(Bond_Purpose == "PERF") %>%
  filter(Current_Acres > 0) %>%
  mutate(Bond_Amount_per_Acre = Bond_Amount / Current_Acres) %>%
  mutate(expected_perf_bond = Bond_Rate * Current_Acres)

underbonded_hw_perf_bond_stats <- underbonded_hw_perf_bonds %>%
  summarize(min_bond_rate = min(Bond_Rate, na.rm = TRUE),
            max_bond_rate = max(Bond_Rate, na.rm = TRUE),
            avg_bond_rate = mean(Bond_Rate, na.rm = TRUE),
            weighted_avg_bond_rate = sum(Bond_Rate * Current_Acres, na.rm = TRUE) / sum(Current_Acres, na.rm = TRUE),
            n = nrow(underbonded_hw_perf_bonds))
# print(underbonded_hw_perf_bond_stats)

# Weighted average bond rate is $3,068, n=116


# Compare bond rates for underbonded highwall permits to highwall costs per acre
underbonded_hw_perf_bonds <- underbonded_hw_perf_bonds %>%
  group_by(PermitID) %>%
  summarize(bonded_acres = sum(Current_Acres, na.rm = TRUE),
            expected_perf_bond = sum(expected_perf_bond, na.rm = TRUE),
            avg_bond_rate = mean(Bond_Rate, na.rm = TRUE))

underbonded_wv_permits <- underbonded_wv_permits %>%
  left_join(underbonded_hw_perf_bonds, by = c("Permit_ID" = "PermitID")) %>%
  mutate(hw_cost_per_acre = Highwall_Cost_Mid / bonded_acres) %>%
  mutate(bond_diff = (expected_perf_bond - Bond_Amount))

# View(underbonded_wv_permits)