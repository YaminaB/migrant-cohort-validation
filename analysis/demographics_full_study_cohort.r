library(gtsummary)
library(dplyr)

# Sample data
full_study_cohort <- read.csv(gzfile("output/full_study_cohort.csv.gz"))

# select needed variables
colnames(full_study_cohort)

cob_cohort <- full_study_cohort %>%
  filter(has_cob_migrant_code == "TRUE") %>%
  mutate(cohort_type = "Country of birth")

interpreter_cohort <- full_study_cohort %>%
  filter(has_interpreter_migrant_code == "FALSE") %>%
  mutate(cohort_type = "Interpreter")

asylum_refugee_cohort <- full_study_cohort %>%
  filter(has_asylum_or_refugee_migrant_code == "FALSE") %>%
  mutate(cohort_type = "Asylum seeker or refugee")

full_study_cohort <- full_study_cohort %>%
  mutate(cohort_type = "All migrants")

full_study_cohort_with_subgroups <- bind_rows(full_study_cohort, 
                                              cob_cohort, 
                                              interpreter_cohort,
                                              asylum_refugee_cohort)

full_study_cohort_with_subgroups$latest_ethnicity_group[trimws(full_study_cohort_with_subgroups$latest_ethnicity_group) == ""] <- NA
full_study_cohort_with_subgroups$region[trimws(full_study_cohort_with_subgroups$region) == ""] <- NA

full_study_cohort_with_subgroups$cohort_type <- factor(full_study_cohort_with_subgroups$cohort_type, 
                                                       levels = c("All migrants", "Country of birth",
                                                                  "Interpreter", "Asylum seeker or refugee"))

full_study_cohort_with_subgroups <- full_study_cohort_with_subgroups %>%
  select(-c(patient_id, latest_ethnicity_code, date_of_first_migration_code, year_of_birth, TPP_death_date,
            ons_death_date, date_of_first_practice_registration, msoa_code, imd_decile, 
            has_cob_migrant_code, has_asylum_or_refugee_migrant_code, has_interpreter_migrant_code))

# Generate demographics table
demographics <- full_study_cohort_with_subgroups %>%
  tbl_summary(by = cohort_type,
    statistic = list(
      all_categorical() ~ "{n} ({p}%)",
      all_continuous() ~ "{median} ({p25}-{p75})",
      all_dichotomous() ~ "{n} ({p}%)"), 
    missing = "ifany"
  ) %>% 
  add_overall() %>%
  bold_labels()

# Print table
demographics 
