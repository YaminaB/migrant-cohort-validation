library(gtsummary)
library(dplyr)

# Sample data
full_study_cohort <- read.csv(gzfile("output/full_study_cohort.csv.gz"))

# select needed variables
colnames(full_study_cohort)

full_study_cohort <- full_study_cohort %>%
  select(-c(patient_id, latest_ethnicity_code, date_of_first_migration_code, year_of_birth, TPP_death_date,
            ons_death_date, date_of_first_practice_registration, msoa_code))

str(full_study_cohort$latest_ethnicity_group)

full_study_cohort$latest_ethnicity_group[trimws(full_study_cohort$latest_ethnicity_group) == ""] <- NA
full_study_cohort$region[trimws(full_study_cohort$region) == ""] <- NA

# Generate demographics table
demographics <- full_study_cohort %>%
  tbl_summary(
    statistic = list(
      all_categorical() ~ "{n} ({p}%)",
      all_continuous() ~ "{median} ({sd})",
      all_dichotomous() ~ "{n} ({p}%)"), 
    missing = "ifany"
  ) %>%
  bold_labels()

# Print table
demographics 
