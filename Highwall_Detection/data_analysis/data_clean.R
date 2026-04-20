library(dplyr)

#------------------------------------------------------------------------------
# LOAD DATA
#------------------------------------------------------------------------------

# Define directory paths
input_dir <- "Highwall_Detection/data_analysis/inputs"
cleaned_dir <- "Highwall_Detection/data_analysis/cleaned"

# Load main dataframes
segments <- read.csv(file.path(input_dir, "segments.csv")) %>%
  filter(State != "Tennessee")
ky_permits <- read.csv(file.path(input_dir, "ky_permits.csv"))
wv_permits <- read.csv(file.path(input_dir, "wv_permits.csv"))
va_permits <- read.csv(file.path(input_dir, "va_permits.csv"))
# tn_permits <- read.csv(file.path(input_dir, "tn_permits.csv"))

# Load additional dataframes for case studies
wv_individual_bonds <- read.csv(file.path(input_dir, "wv_individual_bonds.csv"))
wv_permit_search <- read.csv(file.path(input_dir, "wv_permit_search.csv"))
ky_individual_bonds <- read.csv(file.path(input_dir, "ky_individual_bonds.csv"))

#------------------------------------------------------------------------------
# CLEAN DATA
#------------------------------------------------------------------------------

# Rename segment attributes
colnames(segments) <- c("State", "Highwall_ID", "Segment_ID", "Rec_Status",
                        "Rec_Status_Yr", "Earliest_Vis_Yr", "First_Mined_Yr",
                        "Last_Mined_Yr", "Max_Age", "Min_Age", "Raw_Length",
                        "Length", "Top_Elevation", "Base_Elevation", "Height",
                        "Min_Cost", "Mid_Cost", "Max_Cost", "Permit_ID",
                        "Permittee", "All_Permit_IDs", "Lidar_Yr",
                        "Lidar_Project", "Max_Slope", "Mean_Slope", "Med_Slope",
                        "system.index", ".geo")

# Calculate mid_age and age_uncertainty of segments
segments$Mid_Age <- (segments$Max_Age + segments$Min_Age) / 2
segments$Age_Uncertainty <- (segments$Max_Age - segments$Min_Age) / 2

# Remove pre-law segments and segments with no known First_Mined_Yr
segments <- segments %>%
  filter(First_Mined_Yr > 1982 & !is.na(First_Mined_Yr))

# Now that we are excluding pre-law highwalls, we need to
# re-aggregate the permit data.

# Remove existing highwall data from state permit dataframes
permit_df_names <- c("ky_permits", "wv_permits", "va_permits")
columns_to_remove <- c("system.index", ".geo", "Highwall_IDs", "Total_Length",
                       "Total_Cost_Min", "Total_Cost_Mid", "Total_Cost_Max")

for (df_name in permit_df_names) {
  df <- get(df_name)
  df <- df[, !names(df) %in% columns_to_remove]
  assign(df_name, df)
}

# Rename columns in state permit dataframes
colnames(ky_permits) <- c("Permit_ID", "Permittee", "Mine_Name", "Orig_Bond",
                          "Curr_Bond", "Avail_Bond", "Mine_Status",
                          "Bond_Status", "Highwall_Comp", "Highwall_Viol",
                          "Highwall_Total", "Acres", "Issue_Date", "Per_Type",
                          "Type_Flag", "Post_SMCRA")

colnames(wv_permits) <- c("Permit_ID", "Permittee", "Operator", "Mine_Name",
                          "Bond_Amount", "Avail_Bond",
                          "Mine_Status", "Bond_Status", "Mine_Type",
                          "Acres", "Acres_Dist", "Acres_Orig", "Acres_Recl",
                          "Expir_Date", "Issue_Date", "PMLU", "PMLU_2",
                          "Post_SMCRA", "Vio_Active", "Vio_Total", "WebLink")

colnames(va_permits) <- c("Permit_ID", "Permittee", "Mine_Name",
                          "Bond_Amount", "Avail_Bond", "Bond_Type",
                          "Mine_Status", "Bond_Status", "Issue_Date", "Acres",
                          "Anniversary", "App_Date", "App_No", "Mine_Type",
                          "Post_SMCRA", "Trans_From", "Release_Date",
                          "Mountaintop", "Underground", "Steep_Slope",
                          "Auger_Mining", "Non_AOC", "Remining",
                          "Remining_Acres", "Layer")

# colnames(tn_permits) <- c("Permit_ID", "Permittee", "Mine_Name",
#                           "Bond_Amount", "Avail_Bond", "Bond_Type",
#                           "Land_Req_Bond", "Water_Req_Bond", "Total_Req_Bond",
#                           "Bond_Shortfall", "Mine_Status", "Bond_Status",
#                           "Acres", "Post_SMCRA")

# Convert all dates from unix time to human-readable dates
date_columns <- list(
  ky_permits = c("Issue_Date"),
  wv_permits = c("Issue_Date", "Expir_Date"),
  va_permits = c("Issue_Date", "Anniversary")
)
for (df_name in names(date_columns)) {
  df <- get(df_name)
  for (col in date_columns[[df_name]]) {
    if (col %in% names(df)) {
      df[[col]] <- as.Date(as.POSIXct(df[[col]] / 1000, origin = "1970-01-01"))
    }
  }
  assign(df_name, df)
}

# Replace NA with 0 for all bond values
bond_columns <- list(
  ky_permits = c("Avail_Bond", "Curr_Bond", "Orig_Bond"),
  wv_permits = c("Bond_Amount", "Avail_Bond"),
  va_permits = c("Bond_Amount", "Avail_Bond")
  # tn_permits = c("Bond_Amount", "Avail_Bond")
)

for (df_name in names(bond_columns)) {
  df <- get(df_name)
  for (col in bond_columns[[df_name]]) {
    if (col %in% names(df)) {
      df[is.na(df[[col]]), col] <- 0
    }
  }
  assign(df_name, df)
}

# Replace blank and 'Transferred' with 'Not Bonded' in Bond_Status column
for (df_name in permit_df_names) {
  df <- get(df_name)
  df$Bond_Status <- ifelse(df$Bond_Status == "" |
                             df$Bond_Status == "Transferred",
                           "Not Bonded", df$Bond_Status)
  df$Permit_ID <- as.character(df$Permit_ID) # Convert Permit_ID to character
  assign(df_name, df)
}

# Create Full_Bond column (bond money available for all reclamation,
# even in P1 and P2 released permits))
ky_permits$Full_Bond <- ifelse(ky_permits$Bond_Status == "Released",
                               ky_permits$Curr_Bond,
                               ky_permits$Avail_Bond)
wv_permits$Full_Bond <- wv_permits$Avail_Bond
va_permits$Full_Bond <- va_permits$Bond_Amount
# tn_permits$Full_Bond <- tn_permits$Avail_Bond

# Summarize segment stats in state permit dataframes
for (df_name in permit_df_names) {
  df <- get(df_name)
  df <- df %>%
    rowwise() %>%
    mutate(
      Highwall_IDs = {
        ids <- as.character(unique(segments$Highwall_ID[segments$Permit_ID == Permit_ID]))
        ids <- ids[!is.na(ids)]
        if (length(ids) == 0) "" else paste0("[", paste(ids, collapse = ", "), "]")
      },
      Highwall_Length = sum(segments$Length[segments$Permit_ID == Permit_ID], na.rm = TRUE),
      Highwall_Cost_Min = sum(segments$Min_Cost[segments$Permit_ID == Permit_ID], na.rm = TRUE),
      Highwall_Cost_Mid = sum(segments$Mid_Cost[segments$Permit_ID == Permit_ID], na.rm = TRUE),
      Highwall_Cost_Max = sum(segments$Max_Cost[segments$Permit_ID == Permit_ID], na.rm = TRUE)
    ) %>%
    ungroup()
  assign(df_name, df)
}

# Remove permits with no highwalls
ky_permits <- ky_permits[ky_permits$Highwall_Length != 0, ]
wv_permits <- wv_permits[wv_permits$Highwall_Length != 0, ]
va_permits <- va_permits[va_permits$Highwall_Length != 0, ]
# tn_permits <- tn_permits[tn_permits$Highwall_Length != 0, ]

# Calculate bond deficits using Full_Bond
for (df_name in permit_df_names) {
  df <- get(df_name)
  df$Min_Deficit <- df$Highwall_Cost_Min - df$Full_Bond
  df$Mid_Deficit <- df$Highwall_Cost_Mid - df$Full_Bond
  df$Max_Deficit <- df$Highwall_Cost_Max - df$Full_Bond
  assign(df_name, df)
}

# Create all_permits dataframe by merging shared attributes
# from state permit dataframes
all_permits <- bind_rows(
  transform(ky_permits, State = "Kentucky"),
  transform(wv_permits, State = "West Virginia"),
  transform(va_permits, State = "Virginia")
  # transform(tn_permits, State = "Tennessee")
) %>%
  select(
    State, Permit_ID, Permittee, Mine_Name, Highwall_IDs, Highwall_Length,
    Highwall_Cost_Min, Highwall_Cost_Mid, Highwall_Cost_Max, Avail_Bond,
    Full_Bond, Min_Deficit, Mid_Deficit, Max_Deficit, Mine_Status,
    Bond_Status, Acres, Post_SMCRA
  )

# Join permit information from all_permits to segments
segments <- segments %>%
  left_join(select(all_permits, Permit_ID, Mine_Name, Avail_Bond,
                   Full_Bond, Mine_Status, Bond_Status, Post_SMCRA),
            by = "Permit_ID")

# Create highwalls dataframe by grouping segments
highwalls <- segments %>%
  group_by(Highwall_ID) %>%
  summarize(
    State = first(State),
    Num_Segments = n_distinct(Segment_ID),
    Rec_Status = first(Rec_Status),
    Rec_Status_Yr = first(Rec_Status_Yr),
    Earliest_Vis_Yr = first(Earliest_Vis_Yr),
    First_Mined_Yr = first(First_Mined_Yr),
    Last_Mined_Yr = first(Last_Mined_Yr),
    Max_Age = first(Max_Age),
    Min_Age = first(Min_Age),
    Mid_Age = first(Mid_Age),
    Age_Uncertainty = first(Age_Uncertainty),
    Raw_Length = sum(Raw_Length),
    Length = sum(Length),
    Max_Top_Elevation = max(Top_Elevation),
    Min_Base_Elevation = min(Base_Elevation),
    Avg_Height = mean(Height),
    Min_Cost = sum(Min_Cost),
    Mid_Cost = sum(Mid_Cost),
    Max_Cost = sum(Max_Cost),
    Lidar_Yr = first(Lidar_Yr),
    Lidar_Project = first(Lidar_Project),
    All_Permit_IDs = first(All_Permit_IDs),
    Max_Slope = first(Max_Slope),
    Mean_Slope = first(Mean_Slope),
    Med_Slope = first(Med_Slope),
    Permit_ID = first(Permit_ID),
    Permittee = first(Permittee),
    Mine_Name = first(Mine_Name),
    Avail_Bond = first(Avail_Bond),
    Full_Bond = first(Full_Bond),
    Mine_Status = first(Mine_Status),
    Bond_Status = first(Bond_Status),
    Post_SMCRA = first(Post_SMCRA)
  )

#------------------------------------------------------------------------------
# SAVE CLEANED DATA
#------------------------------------------------------------------------------

write.csv(ky_permits, file.path(cleaned_dir, "ky_permits.csv"), row.names = FALSE)
write.csv(wv_permits, file.path(cleaned_dir, "wv_permits.csv"), row.names = FALSE)
write.csv(va_permits, file.path(cleaned_dir, "va_permits.csv"), row.names = FALSE)
write.csv(all_permits, file.path(cleaned_dir, "all_permits.csv"), row.names = FALSE)
write.csv(segments, file.path(cleaned_dir, "segments.csv"), row.names = FALSE)
write.csv(highwalls, file.path(cleaned_dir, "highwalls.csv"), row.names = FALSE)