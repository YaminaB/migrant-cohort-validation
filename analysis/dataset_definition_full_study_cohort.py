# This is a script to create the following migrant cohort with basic demographics:
# - Select anyone with 
#         1) a migration-related code at any time point during the study period AND 
#         2) who was registered at anytime (2009-2024) AND
#         3) who does not have a disclosive sex 
# - Add a variable to indicate the date when they got their first migration code 
# - Add a variable to indicate number of migration codes in their record
# - Add a variable to indicate the category of migration-related code 
# - Add a sex variable
# - Add date of first practice registration variable
# - Add time from first practice registration to first migration code
# - Add ethnicity variable (using SNOMED:2022 codelist)
# - Add year of birth variable
# - Add practice region variable (or equivalent)
# - Add IMD variable 
# - Add a date of death (if there is one)

from ehrql import create_dataset, codelist_from_csv, show
from ehrql.tables.tpp import addresses, patients, practice_registrations, clinical_events, ons_deaths

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

# Select all individuals who:
#          1) had a migrant code during the entire study period AND 
#          2) were registered at some point during the period AND 
#          3) has a non-disclosive sex
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

has_non_disclosive_sex = (
    (patients.sex == "male") | (patients.sex == "female")
)

dataset = create_dataset()
dataset.define_population(has_any_migrant_code & is_registered_during_study & has_non_disclosive_sex)

date_of_first_migration_code = (
    clinical_events.where(clinical_events.snomedct_code.is_in(all_migrant_codes))
    .sort_by(clinical_events.date)
    .first_for_patient().date)

dataset.date_of_first_migration_code = date_of_first_migration_code

dataset.number_of_migration_codes = (
    clinical_events.where(clinical_events.snomedct_code.is_in(all_migrant_codes))
    .count_for_patient()
)

dataset.sex = patients.sex

# Add variables to indicate the type of migration code

dataset.has_cob_migrant_code = clinical_events.where(clinical_events.snomedct_code.is_in(cob_migrant_codes)).exists_for_patient()
dataset.has_asylum_or_refugee_migrant_code = clinical_events.where(clinical_events.snomedct_code.is_in(asylum_refugee_migrant_codes)).exists_for_patient()
dataset.has_interpreter_migrant_code = clinical_events.where(clinical_events.snomedct_code.is_in(interpreter_migrant_codes)).exists_for_patient()

# Add first practice registration date

date_of_first_practice_registration = (
    practice_registrations.sort_by(practice_registrations.start_date)
    .first_for_patient().start_date
)

dataset.date_of_first_practice_registration = date_of_first_practice_registration

# Calculate time from first registration to first migration code 

time_to_first_migration_code  = (date_of_first_migration_code - date_of_first_practice_registration).days

dataset.time_to_first_migration_code = time_to_first_migration_code

# Add ethnicity variable

dataset.latest_ethnicity_code = (
    clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codelist))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .snomedct_code
)
dataset.latest_ethnicity_group = dataset.latest_ethnicity_code.to_category(
    ethnicity_codelist
)

# Add year of birth variable

dataset.year_of_birth = (patients.date_of_birth).year

# Add MSOA 

address = addresses.for_patient_on("2021-03-21") # 2021 Census day

dataset.msoa_code = address.msoa_code

# Add IMD based on patient's address 

dataset.imd_decile = address.imd_decile
dataset.imd_quintile = address.imd_quintile

# Add date of death (if died)

dataset.TPP_death_date = patients.date_of_death
dataset.ons_death_date = ons_deaths.date

show(dataset)

dataset.configure_dummy_data(population_size=1000)



