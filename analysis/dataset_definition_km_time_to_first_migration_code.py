# This is a script to create a cohort with basic demographics in order to carry out a survival analysis looking at time from first practice registration to first migration code:
# - Select anyone with 
#         2) who was registered at any time during the study period (2009-2024) AND
#         3) who does not have a disclosive sex AND
#         4) had not died before the start of the study period AND 
#         5) was not over 100 years old at the start of the study period

from ehrql import create_dataset, codelist_from_csv, show, case, when
from ehrql.tables.tpp import addresses, patients, practice_registrations, clinical_events, ons_deaths

all_migrant_codes = codelist_from_csv(
    "codelists/user-YaminaB-migration-status.csv", column="code"
)

# Dates

study_start_date = "2009-01-01"
study_end_date = "2024-12-31"

# Dataset definitions

is_registered_during_study = (
    practice_registrations
    .where((practice_registrations.end_date.is_null()) | ((practice_registrations.end_date.is_on_or_before(study_end_date)) & (practice_registrations.end_date.is_after(study_start_date))))
    .exists_for_patient()
)           

has_non_disclosive_sex = (
    (patients.sex == "male") | (patients.sex == "female")
)

is_alive_at_study_start = (
    ((patients.date_of_death >= study_start_date) | (patients.date_of_death.is_null())) &
    ((ons_deaths.date >= study_start_date) | (ons_deaths.date.is_null()))
)

was_not_over_100_at_study_start = (
    patients.age_on(study_start_date) <= 100
)

dataset = create_dataset()
dataset.define_population(is_registered_during_study & 
                          has_non_disclosive_sex & 
                          is_alive_at_study_start & 
                          was_not_over_100_at_study_start)

# Add required variables

## Date of first GP registration 

dataset.date_of_first_practice_registration = (
    practice_registrations.sort_by(practice_registrations.start_date)
    .first_for_patient().start_date
)

## Migration status

dataset.has_a_migration_code = (
    clinical_events.where(clinical_events.snomedct_code.is_in(all_migrant_codes))
    .exists_for_patient())

## Date of first migration code

dataset.date_of_first_migration_code = (
    clinical_events.where(clinical_events.snomedct_code.is_in(all_migrant_codes))
    .sort_by(clinical_events.date)
    .first_for_patient().date)

## Number of migration codes (maybe don't need)

dataset.number_of_migration_codes = (
    clinical_events.where(clinical_events.snomedct_code.is_in(all_migrant_codes))
    .count_for_patient()
)

# Sex

dataset.sex = patients.sex

# Year of birth

year_of_birth = (patients.date_of_birth).year
dataset.year_of_birth = year_of_birth

dataset.year_of_birth_band = case(
    when((year_of_birth >= 1900) & (year_of_birth <= 1925)).then("1900-1925"),
    when((year_of_birth > 1925) & (year_of_birth <= 1945)).then("1926-1945"),
    when((year_of_birth > 1945) & (year_of_birth <= 1965)).then("1946-1965"),
    when((year_of_birth > 1965) & (year_of_birth <= 1985)).then("1966-1985"),
    when((year_of_birth > 1985) & (year_of_birth <= 2005)).then("1986-2005"),
    when((year_of_birth > 2005) & (year_of_birth <= 2025)).then("2006-2025") 
)


dataset.configure_dummy_data(population_size=1000)

