# This is a script to create the following migrant cohort with basic demographics:
# - Select anyone with 
#         1) a migration-related code at any time point on or before the 2021 Census date (21st March 2021) AND 
#         2) who was registered on the Census 2021 date (21st March 2021) AND
#         3) who does not have a disclosive sex AND
#         4) had not died before the start of the study period AND 
#         5) was not over 100 years old at the Census 2021 date (21st March 2021)

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


