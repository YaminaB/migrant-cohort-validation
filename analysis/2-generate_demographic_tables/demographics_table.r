library(gtsummary)
library(dplyr)
library(here)
library(janitor)
library(fs)
library(readr)
library(tools)
library(arrow)

# Parse command-line argument
args <- commandArgs(trailingOnly=TRUE)

cohort_file <- args[[1]]
output_file <- args[[2]]

# load data
cohort <- read_feather(cohort_file)

cat("File successfully loaded. Rows:", nrow(cohort), "\n")

# create sub-cohorts and bind to full cohort

cob_cohort <- cohort %>%
  filter(has_cob_migrant_code == "TRUE") %>%
  mutate(cohort_type = "Country of birth")

interpreter_cohort <- cohort %>%
  filter(has_interpreter_migrant_code == "FALSE") %>%
  mutate(cohort_type = "Interpreter")

asylum_refugee_cohort <- cohort %>%
  filter(has_asylum_or_refugee_migrant_code == "FALSE") %>%
  mutate(cohort_type = "Asylum seeker or refugee")

cohort <- cohort %>%
  mutate(cohort_type = "All migrants")

study_cohort_with_subgroups <- bind_rows(cohort, 
                                              cob_cohort, 
                                              interpreter_cohort,
                                              asylum_refugee_cohort)

study_cohort_with_subgroups$latest_ethnicity_group[trimws(study_cohort_with_subgroups$latest_ethnicity_group) == ""] <- NA
study_cohort_with_subgroups$region[trimws(study_cohort_with_subgroups$region) == ""] <- NA

study_cohort_with_subgroups$cohort_type <- factor(study_cohort_with_subgroups$cohort_type, 
                                                       levels = c("All migrants", "Country of birth",
                                                                  "Interpreter", "Asylum seeker or refugee"))

study_cohort_with_subgroups <- study_cohort_with_subgroups %>%
  select(-c(patient_id, latest_ethnicity_code, date_of_first_migration_code, year_of_birth, TPP_death_date,
            ons_death_date, date_of_first_practice_registration, msoa_code, imd_decile, 
            has_cob_migrant_code, has_asylum_or_refugee_migrant_code, has_interpreter_migrant_code))

# generate demographics table

demographics <- study_cohort_with_subgroups %>%
  tbl_summary(by = cohort_type,
    statistic = list(
      all_categorical() ~ "{n} ({p}%)",
      all_continuous() ~ "{median} ({p25}-{p75})",
      all_dichotomous() ~ "{n} ({p}%)"), 
    missing = "ifany"
  ) %>% 
  add_overall() %>%
  bold_labels()
  
demographics_tibble <- as_tibble(demographics, include = "tibble")

dir_create(here("output", "tables"))

write_csv(demographics_tibble, path = output_file)


