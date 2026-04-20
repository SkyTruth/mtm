library(dplyr)

#------------------------------------------------------------------------------
# LOAD CLEANED DATA
#------------------------------------------------------------------------------

# Define directory paths
cleaned_dir <- "Highwall_Detection/data_analysis/cleaned"

# Load dataframes
all_permits <- read.csv(file.path(cleaned_dir, "all_permits.csv"))
highwalls <- read.csv(file.path(cleaned_dir, "highwalls.csv"))


#------------------------------------------------------------------------------
# What are the top 10 permittees in each state by unreclaimed highwall costs?
#------------------------------------------------------------------------------

# We will only consider bonded and forfeited permits, to avoid highlighting
# older permits where the company has likely disappeared.

top_permittees <- all_permits %>%
  filter(State == "Virginia",
         Bond_Status == "Bonded" | Bond_Status == "Forfeited") %>%
  group_by(Permittee) %>%
  summarize(total_cost = sum(Highwall_Cost_Mid, na.rm = TRUE),
            total_deficit = sum(Mid_Deficit, na.rm = TRUE)) %>%
  arrange(desc(total_cost)) %>%
  head(10)

# print(top_permittees)


#------------------------------------------------------------------------------
# # Why are there still so many highwalls in Released permits?
# # Even after removing pre-law highwalls?
#------------------------------------------------------------------------------

# Hypothesis 1: We failed to remove all pre-law highwalls.
# H1 Test 1: Are highwalls in Released permits older than highwalls in permits
# of other statuses?

age_by_status <- ggplot(highwalls, aes(x = Bond_Status, y = Max_Age)) +
  geom_boxplot() +
  labs(
    title = "Highwall Age by Bond Status",
    x = "Bond Status",
    y = "Age (Years)"
  ) +
  theme_classic() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1, size = 22),
    axis.text.y = element_text(size = 22),
    axis.title.x = element_text(size = 24),
    axis.title.y = element_text(size = 24),
    plot.title = element_text(size = 28, hjust = 0.5)
  )
# print(age_by_status)

# Released and Unbonded highwalls are older than Bonded and Forfeited highwalls.


# H1 Test 2: Are Released highwalls more likely to be revegetated
# than unreleased highwalls?

rec_status_by_bond_status <- ggplot(highwalls, aes(x = Bond_Status, fill = Rec_Status)) +
  geom_bar(position = "stack") +
  scale_fill_manual(values = c("Unreclaimed" = "blue", "Revegetated" = "#4DAF4A")) +
  scale_y_continuous(labels = scales::comma_format()) +
  labs(
    title = "Reclamation Status by Bond Status",
    x = "Bond Status",
    y = "Number of Highwalls",
    fill = "Reclamation Status"
  ) +
  theme_classic() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1, size = 22),
    axis.text.y = element_text(size = 22),
    axis.title.x = element_text(size = 24),
    axis.title.y = element_text(size = 24),
    plot.title = element_text(size = 28, hjust = 0.5),
    legend.text = element_text(size = 20),
    legend.title = element_text(size = 22),
    legend.position = "bottom"
  )
# print(rec_status_by_bond_status)

# Released highwalls are mostly revegetated, while bonded highwalls
# are mostly unreclaimed.


# Hypothesis 2: These highwalls got assigned to the wrong permit.
# The should have been assigned to an unreleased permit but were
# mistakenly assigned to a released permit.

# H2 Test 1: Do Released highwalls often intersect multiple permits,
# indicating that they could have been assignd to a different permit?

# Calculate number of permits per highwall
highwalls$Num_Permits <- sapply(strsplit(highwalls$All_Permit_IDs, ","), length)

# Show the percentage of Released highwalls that only intersect one permit
one_permit <- highwalls %>%
  filter(Bond_Status == "Released", Num_Permits == 1) %>%
  nrow()
total_released <- highwalls %>%
  filter(Bond_Status == "Released") %>%
  nrow()
percentage_one_permit <- one_permit / total_released * 100
print(paste(percentage_one_permit, "%"))

# 62% of Released highwalls only intersect one permit, meaning they coudn't have
# been assigned to the wrong permit.
# Also, the permit match methdology only assigns a highwall to a Released permit
# if it does not intersect any bonded/forfeited permits, so there is no way they
# could have been incorrectly assigned to a Released permit.
# One caveat here is if they are part of an underground mine,
# prep plant, or refuse impoundment, but got assigned to a Released
# surface permit instead.


# Hypothesis 3: These highwalls were incorrectly detected and are not highwalls.
# H3 Test 1: Manually inspect Released highwalls in Earth Engine, and get Matt
# to confirm that they are actually highwalls.
# Matt confirmed that everything he saw was a highwall.