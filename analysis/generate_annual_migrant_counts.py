##########################################################################

# This is a script to determine the cumulative number of migrants annually 
# - Select anyone who: 
#         1) was alive on the 1st January of each calendar year AND
#         2) was registered with a practice on the 1st January of each calendar year AND
#         2) had a migration-related code at any time point during or before the specific annual interval (i.e. before or on 31st December of the respective year) AND 
#         3) does not have a disclosive sex AND 
#         4) was not over 100 years of age
# By:
# - Sex
# - Ethnicity (using SNOMED:2022 codelist) - to do
# - Age (use age bands)
# - Practice region - to do 
# - IMD

# Author: Yamina Boukari
# Bennett Institute for Applied Data Science, University of Oxford, 2025

#############################################################################

from ehrql import create_dataset, codelist_from_csv, show, INTERVAL, case, create_measures, years, when
from ehrql.tables.tpp import addresses, patients, practice_registrations, clinical_events, ons_deaths

measures = create_measures()

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

# 1) was alive on the 1st January of each calendar year AND

was_alive_on_1Jan = patients.is_alive_on(INTERVAL.start_date)

# 2) was registered with a practice on the 1st January of each calendar year AND

was_registered_on1Jan = (
    practice_registrations
    .where(practice_registrations.start_date <= INTERVAL.start_date)
    .except_where(practice_registrations.end_date < INTERVAL.start_date)
    .exists_for_patient()
)

# 3) had a migration-related code at any time point before or on the 1st January of each calendar year AND

has_any_migrant_code = (
    clinical_events.where(clinical_events.snomedct_code.is_in(all_migrant_codes)))

has_any_migrant_code_during_or_before_interval  = has_any_migrant_code.where(clinical_events.date.is_on_or_before(INTERVAL.end_date))

# 4) does not have a disclosive sex AND 

has_recorded_sex = patients.sex.is_in(["male", "female"])

# 5) was not over 100 years of age

age = patients.age_on(INTERVAL.start_date)
not_over_100_years = age <= 100

age_band = case(
    when((age >= 0) & (age < 20)).then("0-19"),
    when((age >= 20) & (age < 40)).then("20-39"),
    when((age >= 40) & (age < 60)).then("40-59"),
    when((age >= 60) & (age < 80)).then("60-79"),
    when(age >= 80).then("80+"),
)

# define measures -

## set defaults

measures.define_defaults(
    numerator = has_any_migrant_code_during_or_before_interval.exists_for_patient(),
    denominator = was_alive_on_1Jan & was_registered_on1Jan & has_recorded_sex & not_over_100_years & has_recorded_sex,
    intervals= years(16).starting_on("2009-01-01")
)

## all migrants

measures.define_measure(
    name = "migrant", 
    group_by = {
        
    }
)

## broken down by sex

measures.define_measure(
    name = "migrant_sex", 
    group_by = {
        "sex": patients.sex 
    }
)

## broken down by age

measures.define_measure(
    name = "migrant_age", 
    group_by = {
        "age_band": age_band 
    }
)

## broken down by imd

imd_rounded = addresses.for_patient_on(INTERVAL.start_date).imd_rounded
max_imd = 32844
imd_quintile = case(
    when(imd_rounded < int(max_imd * 1 / 5)).then(1),
    when(imd_rounded < int(max_imd * 2 / 5)).then(2),
    when(imd_rounded < int(max_imd * 3 / 5)).then(3),
    when(imd_rounded < int(max_imd * 4 / 5)).then(4),
    when(imd_rounded <= max_imd).then(5),
)

measures.define_measure(
    name = "migrant_imd", 
    group_by = {
        "imd": imd_quintile 
    }
)





