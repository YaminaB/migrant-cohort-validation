# This is a script to create the following migrant cohort with basic demographics:
# - Select anyone with 
#         1) a migration-related code at any time point on or before the Census date AND 
#         2) who was registered on the Census date AND
#         3) who does not have a disclosive sex AND
#         4) had not died before the start of the study period AND 
#         5) was not over 100 years old at the Census  date 

from ehrql import create_dataset, codelist_from_csv, show, case, when
from ehrql.tables.tpp import addresses, patients, practice_registrations, clinical_events, ons_deaths
from utilities import load_all_codelists 

# load codelists 
(all_migrant_codes,
    cob_migrant_codes,
    asylum_refugee_migrant_codes,
    interpreter_migrant_codes,
    ethnicity_codelist
) = load_all_codelists().values()

# set date
census_2021_date = "2021-03-21"

# define population
has_any_migrant_code = (
    clinical_events.where(clinical_events.snomedct_code.is_in(all_migrant_codes)
                          ).where(clinical_events.date.is_on_or_before(census_2021_date)
                                  ).exists_for_patient())

was_registered_on_census_date = (
    practice_registrations.exists_for_patient_on(census_2021_date)
)           

has_non_disclosive_sex = (
    (patients.sex == "male") | (patients.sex == "female")
)

was_alive_on_census_date = (
    (patients.is_alive_on(census_2021_date))
)

was_not_over_100_on_census_date = (
    patients.age_on(census_2021_date) <= 100
)

dataset = create_dataset()
dataset.define_population(has_any_migrant_code & 
                          was_registered_on_census_date & 
                          has_non_disclosive_sex & 
                          was_alive_on_census_date & 
                          was_not_over_100_on_census_date)

show(dataset)

# add variables 

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

# Add year of birth variable and categorise into bands 

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

# age 

age_on_census_date = patients.age_on(census_2021_date)
dataset.age_on_census_date  = age_on_census_date

dataset.age_band = case(
        when(age_on_census_date < 16).then("0-15"),
        when((age_on_census_date >= 16) & (age_on_census_date < 25)).then("16-24"),
        when((age_on_census_date >= 25) & (age_on_census_date < 35)).then("25-34"),
        when((age_on_census_date >= 35) & (age_on_census_date < 50)).then("35-49"),
        when((age_on_census_date >= 50) & (age_on_census_date < 65)).then("50-64"),
        when((age_on_census_date >= 65) & (age_on_census_date < 75)).then("65-74"),
        when((age_on_census_date >= 75) & (age_on_census_date < 85)).then("75-84"),
        when(age_on_census_date >= 85).then("85 plus"),
        otherwise="missing",
)

# Add MSOA 

address = addresses.for_patient_on(census_2021_date) 

dataset.msoa_code = address.msoa_code

# Add IMD based on patient's address 

dataset.imd_decile = address.imd_decile
dataset.imd_quintile = address.imd_quintile

# Add practice region (at study start)

dataset.region = practice_registrations.for_patient_on(census_2021_date).practice_nuts1_region_name

# Add date of death (if died)

dataset.TPP_death_date = patients.date_of_death
dataset.ons_death_date = ons_deaths.date

show(dataset)

dataset.configure_dummy_data(population_size=1000)

