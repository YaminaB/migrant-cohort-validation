# This is a script to create the following migrant cohort with basic demographics:
# - Select anyone with a migration-related code at any time point during the study period AND who was registered at anytime (2009-2024)
# - Add a variable to indicate the date when they got their first migration code 
# - Add a variable to indicate number of migration codes in their record
# - Add a variable to indicate the category of migration-related code 
# - Add date of first practice registration variable
# - Add time from first practice registration to first migration code
# - Add ethnicity variable (using SNOMED:2022 codelist)
# - Add year of birth variable
# - Add practice region variable (or equivalent)
# - Add IMD variable 
# - Add sex variable
# - Add a date of death (if there is one)

from ehrql import create_dataset, codelist_from_csv, show
from ehrql.tables.tpp import patients, practice_registrations, clinical_events

# Load codelists 

all_migrant_codes = codelist_from_csv(
    "codelists/user-YaminaB-migration-status.csv", column="code"
)

cob_migrant_codes = codelist_from_csv(
    "codelists/user-YaminaB-born-outside-the-uk.csv", column = "code"
)

asylum_refugee_migrant_codes = codelist_from_csv(
    "codelists/user-YaminaB-asylum-seeker-or-refugee.csv", column = "code"
)

interpreter_migrant_codes = codelist_from_csv(
    "codelists/user-YaminaB-interpreter-required.csv", column = "code"
)

ethnicity_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="code",
    category_column="Grouping_6",
)

# Dates

study_start_date = "2009-01-01"
study_end_date = "2024-12-31"

# Select all individuals who 1) had a migrant code during the entire study period AND were registered at some point during the period
# Add a variable indicating the date of the first code 
# Add a variable indicating how many migration-related codes they have

has_any_migrant_code = (
    clinical_events.where(clinical_events.snomedct_code.is_in(all_migrant_codes))
    .exists_for_patient())

is_registered_during_study = (
    practice_registrations
    .where((practice_registrations.end_date.is_null()) | ((practice_registrations.end_date.is_on_or_before(study_end_date)) & (practice_registrations.end_date.is_after(study_start_date))))
    .exists_for_patient()
)           

dataset = create_dataset()
dataset.define_population(has_any_migrant_code & is_registered_during_study)

dataset.date_of_first_migration_code = (
    clinical_events.where(clinical_events.snomedct_code.is_in(all_migrant_codes))
    .sort_by(clinical_events.date)
    .first_for_patient().date
)
dataset.number_of_migration_codes = (
    clinical_events.where(clinical_events.snomedct_code.is_in(all_migrant_codes))
    .count_for_patient()
)

# Add variables to indicate the type of migration code

dataset.has_cob_migrant_code = clinical_events.where(clinical_events.snomedct_code.is_in(cob_migrant_codes)).exists_for_patient()
dataset.has_asylum_or_refugee_migrant_code = clinical_events.where(clinical_events.snomedct_code.is_in(asylum_refugee_migrant_codes)).exists_for_patient()
dataset.has_interpreter_migrant_code = clinical_events.where(clinical_events.snomedct_code.is_in(interpreter_migrant_codes)).exists_for_patient()

# Add first practice registration date

dataset.first_practice_registration_date = (
    practice_registrations.sort_by(practice_registrations.start_date)
    .first_for_patient().start_date
)

show(dataset)

show(
    clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codelist))
    .where(clinical_events.date.is_on_or_before("2023-01-01"))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .snomedct_code
)

dataset.define_population(has_migrant_code)

dataset.sex = patients.sex
dataset.first_migrant_code = clinical_events.where(clinical_events.snomedct_code.is_in(migrant_codes)).sort_by(clinical_events.date).first_for_patient().snomedct_code
dataset.date_of_first_migrant_code = clinical_events.where(clinical_events.snomedct_code.is_in(migrant_codes)).sort_by(clinical_events.date).first_for_patient().date
dataset.year_of_birth = patients.date_of_birth.year
dataset.date_of_first_practice_registration = practice_registrations.sort_by(practice_registrations.start_date).first_for_patient().start_date


dataset.latest_ethnicity_code = (
    clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codelist))
    .where(clinical_events.date.is_on_or_before("2023-01-01"))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .snomedct_code
)
dataset.latest_ethnicity_group = dataset.latest_ethnicity_code.to_category(
    ethnicity_codelist
)

show(dataset)

show(clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codelist))
     .snomedct_code)
