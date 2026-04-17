library(dplyr)
library(ggplot2)

#------------------------------------------------------------------------------
# LOAD CLEANED DATA
#------------------------------------------------------------------------------

# Define directory paths
cleaned_dir <- "cleaned"
figures_dir <- "figures"

# Load dataframes
segments <- read.csv(file.path(cleaned_dir, "segments.csv"))
all_permits <- read.csv(file.path(cleaned_dir, "all_permits.csv"))
highwalls <- read.csv(file.path(cleaned_dir, "highwalls.csv"))


#------------------------------------------------------------------------------
# FIGURE 5: HIGHWALL COSTS BY STATE AND RECLAMATION STATUS
#------------------------------------------------------------------------------

# Order the states to control stack order
segments$State <- factor(segments$State,
  levels = c("Virginia", "West Virginia", "Kentucky"))

cost_by_rec_status <- ggplot(segments, aes(x = Mid_Cost/1000000, y = State, fill = Rec_Status)) +
  geom_bar(stat = "sum", position = "stack") +
  scale_fill_manual(values = c("Unreclaimed" = "#5B4B49", "Revegetated" = "#B9D18A")) +
  scale_x_continuous(
    labels = scales::comma_format(),
    breaks = c(30, 60, 90, 120),
    limits = function(l) c(0, max(120, l[2])),
    expand = expansion(mult = c(0, 0.04))
  ) +
  labs(
    x = "Estimated Highwall Cost (Millions $)",
    y = NULL,
    fill = "Highwall Status"
  ) +
  theme_minimal() +
  theme(
    axis.text.x.bottom = element_text(size = 12),
    axis.title.x.bottom = element_text(
      face = "bold",
      size = 14,
      color = "black",
      margin = margin(t = 14, r = 0, b = 0, l = 0, unit = "pt")
    ),

    axis.line.y = element_line(size=0.4, color="black"),
    axis.ticks.y.left = element_blank(),
    axis.text.y.left = element_text(
      size = 12,
      face = "bold",
      color = "black",
      hjust = 1,
      margin = margin(t = 0, r = 10, b = 0, l = 0, unit = "pt")
    ),
    axis.title.y = element_blank(),
    
    panel.grid.major.y=element_blank(),
    panel.grid.minor.x=element_blank(),
    panel.grid.major.x=element_line(color="black", size=0.1058),

    legend.text = element_text(size = 12),
    legend.title = element_text(size = 14, face = "bold", hjust = 0.5),
    legend.title.align = 0.5,
    legend.position = "inside",
    legend.position.inside = c(0.95, 0.97),
    legend.justification = c(1, 1),
    legend.key.size = unit(0.4, "cm"),
    legend.key.width = unit(0.5, "cm"),
    legend.spacing.x = unit(0.2, "cm"),
    legend.box.spacing = unit(0.2, "cm")
  ) +
  guides(fill = guide_legend(reverse = TRUE, ncol = 1))

# ggsave(file.path(figures_dir, "cost_by_rec_status.png"), cost_by_rec_status, width = 12, height = 6, dpi = 300)

cost_by_rec_status_table <- highwalls %>%
  group_by(State) %>%
  summarize(unrec_cost = sum(Mid_Cost[Rec_Status == "Unreclaimed"], na.rm = TRUE),
            rev_cost = sum(Mid_Cost[Rec_Status == "Revegetated"], na.rm = TRUE),
            unrec_pct = unrec_cost / (unrec_cost + rev_cost) * 100,
            rev_pct = rev_cost / (unrec_cost + rev_cost) * 100) %>%
  bind_rows(
    .,
    tibble(
      State = "Total",
      unrec_cost = sum(highwalls$Mid_Cost[highwalls$Rec_Status == "Unreclaimed"], na.rm = TRUE),
      rev_cost = sum(highwalls$Mid_Cost[highwalls$Rec_Status == "Revegetated"], na.rm = TRUE),
      unrec_pct = unrec_cost / (unrec_cost + rev_cost) * 100,
      rev_pct = rev_cost / (unrec_cost + rev_cost) * 100
    )
  )
# print(cost_by_rec_status_table)


#------------------------------------------------------------------------------
# FIGURE 6: HIGHWALL COSTS BY STATE AND BOND STATUS
#------------------------------------------------------------------------------

# Order the factor levels to control stack order
all_permits$Bond_Status <- factor(all_permits$Bond_Status,
  levels = c("Not Bonded", "Forfeited", "Released", "Bonded"))

# Order the states to control stack order
all_permits$State <- factor(all_permits$State,
  levels = c("Virginia", "West Virginia", "Kentucky"))

cost_by_bond_status <- ggplot(all_permits, aes(x = Highwall_Cost_Mid/1000000, y = State, fill = Bond_Status)) +
  geom_bar(stat = "sum", position = "stack") +
  scale_fill_manual(values = c("Bonded" = "#2C7BB6", "Released" = "#ABD9E9", "Forfeited" = "#FDAE61", "Not Bonded" = "#D7191C")) +
  scale_x_continuous(
    labels = scales::comma_format(),
    breaks = c(30, 60, 90, 120),
    limits = function(l) c(0, max(120, l[2])),
    expand = expansion(mult = c(0, 0.04))
  ) +
  labs(
    x = "Estimated Highwall Cost (Millions $)",
    y = NULL,
    fill = "Bond Status"
  ) +
  theme_minimal() +
  theme(
    axis.text.x.bottom = element_text(size = 12),
    axis.title.x.bottom = element_text(
      face = "bold",
      size = 14,
      color = "black",
      margin = margin(t = 14, r = 0, b = 0, l = 0, unit = "pt")
    ),

    axis.line.y = element_line(size=0.4, color="black"),
    axis.ticks.y.left = element_blank(),
    axis.text.y.left = element_text(
      size = 12,
      face = "bold",
      color = "black",
      hjust = 1,
      margin = margin(t = 0, r = 10, b = 0, l = 0, unit = "pt")
    ),
    axis.title.y = element_blank(),
    
    panel.grid.major.y=element_blank(),
    panel.grid.minor.x=element_blank(),
    panel.grid.major.x=element_line(color="black", size=0.1058),

    legend.text = element_text(size = 12),
    legend.title = element_text(size = 14, face = "bold", hjust = 0.5),
    legend.title.align = 0.5,
    legend.position = "inside",
    legend.position.inside = c(0.95, 0.97),
    legend.justification = c(1, 1),
    legend.key.size = unit(0.4, "cm"),
    legend.key.width = unit(0.5, "cm"),
    legend.spacing.x = unit(0.2, "cm"),
    legend.box.spacing = unit(0.2, "cm")
  ) +
  guides(fill = guide_legend(reverse = TRUE, ncol = 1))

# ggsave(file.path(figures_dir, "cost_by_bond_status.png"), cost_by_bond_status, width = 12, height = 6, dpi = 300)

# In each state, most costs are for bonded permits.
# Kentucky and Virginia have high proportions of released highwall costs.

cost_by_bond_status_table <- all_permits %>%
  group_by(State) %>%
  summarize(notbonded_pct = sum(Highwall_Cost_Mid[Bond_Status == "Not Bonded"], na.rm = TRUE) / sum(Highwall_Cost_Mid, na.rm = TRUE) * 100,
            forfeited_pct = sum(Highwall_Cost_Mid[Bond_Status == "Forfeited"], na.rm = TRUE) / sum(Highwall_Cost_Mid, na.rm = TRUE) * 100,
            released_pct = sum(Highwall_Cost_Mid[Bond_Status == "Released"], na.rm = TRUE) / sum(Highwall_Cost_Mid, na.rm = TRUE) * 100,
            bonded_pct = sum(Highwall_Cost_Mid[Bond_Status == "Bonded"], na.rm = TRUE) / sum(Highwall_Cost_Mid, na.rm = TRUE) * 100) %>%
  bind_rows(
    .,
    tibble(State = "Total", notbonded_pct = sum(all_permits$Highwall_Cost_Mid[all_permits$Bond_Status == "Not Bonded"], na.rm = TRUE) / sum(all_permits$Highwall_Cost_Mid, na.rm = TRUE) * 100,
           forfeited_pct = sum(all_permits$Highwall_Cost_Mid[all_permits$Bond_Status == "Forfeited"], na.rm = TRUE) / sum(all_permits$Highwall_Cost_Mid, na.rm = TRUE) * 100,
           released_pct = sum(all_permits$Highwall_Cost_Mid[all_permits$Bond_Status == "Released"], na.rm = TRUE) / sum(all_permits$Highwall_Cost_Mid, na.rm = TRUE) * 100,
           bonded_pct = sum(all_permits$Highwall_Cost_Mid[all_permits$Bond_Status == "Bonded"], na.rm = TRUE) / sum(all_permits$Highwall_Cost_Mid, na.rm = TRUE) * 100)
  )

# print(cost_by_bond_status_table)


#------------------------------------------------------------------------------
# FIGURE 7: DEFICITS BY STATE AND BOND STATUS
#------------------------------------------------------------------------------

deficit_by_bond_status <- ggplot(all_permits %>% filter(Mid_Deficit > 0), aes(x = Mid_Deficit/1000000, y = State, fill = Bond_Status)) +
  geom_bar(stat = "sum", position = "stack") +
  scale_fill_manual(values = c("Bonded" = "#2C7BB6", "Released" = "#ABD9E9", "Forfeited" = "#FDAE61", "Not Bonded" = "#D7191C")) +
  scale_x_continuous(
    labels = scales::comma_format(),
    breaks = c(10, 20, 30, 40),
    limits = function(l) c(0, max(40, l[2])),
    expand = expansion(mult = c(0, 0.04))
  ) +
  labs(
    x = "Estimated Permit-Specific Highwall Cost Deficit (Millions $)",
    y = NULL,
    fill = "Bond Status"
  ) +
  theme_minimal() +
  theme(
    axis.text.x.bottom = element_text(size = 12),
    axis.title.x.bottom = element_text(
      face = "bold",
      size = 14,
      color = "black",
      margin = margin(t = 14, r = 0, b = 0, l = 0, unit = "pt")
    ),

    axis.line.y = element_line(size=0.4, color="black"),
    axis.ticks.y.left = element_blank(),
    axis.text.y.left = element_text(
      size = 12,
      face = "bold",
      color = "black",
      hjust = 1,
      margin = margin(t = 0, r = 10, b = 0, l = 0, unit = "pt")
    ),
    axis.title.y = element_blank(),
    
    panel.grid.major.y=element_blank(),
    panel.grid.minor.x=element_blank(),
    panel.grid.major.x=element_line(color="black", size=0.1058),

    legend.text = element_text(size = 12),
    legend.title = element_text(size = 14, face = "bold", hjust = 0.5),
    legend.title.align = 0.5,
    legend.position = "inside",
    legend.position.inside = c(0.95, 0.97),
    legend.justification = c(1, 1),
    legend.key.size = unit(0.4, "cm"),
    legend.key.width = unit(0.5, "cm"),
    legend.spacing.x = unit(0.2, "cm"),
    legend.box.spacing = unit(0.2, "cm")
  ) +
  guides(fill = guide_legend(reverse = TRUE, ncol = 1))

# ggsave(file.path(figures_dir, "deficit_by_bond_status.png"), deficit_by_bond_status, width = 12, height = 6, dpi = 300)


#------------------------------------------------------------------------------
# OTHER FIGURES (NOT INCLUDED IN MANUSCRIPT)
#------------------------------------------------------------------------------

# How does highwall age relate to reclamation status?
age_by_rec_status <- ggplot(highwalls, aes(x = Rec_Status, y = Mid_Age)) +
  geom_boxplot() +
  labs(
    title = "Highwall Age by Reclamation Status",
    x = "Reclamation Status",
    y = "Estimated Age (years)"
  ) +
  theme_classic() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1, size = 22),
    axis.text.y = element_text(size = 22),
    axis.title.x = element_text(size = 24),
    axis.title.y = element_text(size = 24),
    plot.title = element_text(size = 40, hjust = 0.5)
  )
# print(age_by_rec_status)

# Revegetated highwalls are older than unreclaimed highwalls.


# How does highwall age relate to height?
age_by_height <- ggplot(highwalls, aes(x = Mid_Age, y = Avg_Height)) +
  geom_point(alpha = 0.5) +
  geom_smooth(method = "lm", color = "red") +
  labs(
    title = "Relationship Between Highwall Age and Height",
    x = "Estimated Age (years)",
    y = "Height (m)"
  ) +
  theme_classic() +
  theme(
    axis.text.x = element_text(size = 22),
    axis.text.y = element_text(size = 22),
    axis.title.x = element_text(size = 24),
    axis.title.y = element_text(size = 24),
    plot.title = element_text(size = 28, hjust = 0.5)
  )
# print(age_by_height)

# No clear relationship between age and height, whether we use
# segment height or average highwall height