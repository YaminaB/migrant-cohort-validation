##########################################################################

# This is a script to determine the cumulative number of migrants annually 
# - Select anyone who: 
#         1) was alive on the 1st January of each calendar year AND
#         2) was registered with a practice on the 1st January of each calendar year AND
#         2) had a migration-related code at any time point during or before the specific annual interval (i.e. before or on 31st December of the respective year) AND 
#         3) does not have a disclosive sex AND 
#         4) was not over 100 years of age
# By:
# - Age 
# - Sex
# - Ethnicity (using SNOMED:2022 codelist) 
# - Practice region - to do 
# - IMD quintile 

# Author: Yamina Boukari
# Bennett Institute for Applied Data Science, University of Oxford, 2025

#############################################################################

from ehrql import create_dataset, codelist_from_csv, show, INTERVAL, case, create_measures, years, when
from ehrql.tables.tpp import addresses, patients, practice_registrations, clinical_events
from utilities import load_all_codelists 

measures = create_measures()

measures.configure_dummy_data(population_size=1000)
measures.configure_disclosure_control(enabled=False) # needs to be enabled when running on real data!

# Load codelists 

(all_migrant_codes,
    cob_migrant_codes,
    asylum_refugee_migrant_codes,
    interpreter_migrant_codes,
    ethnicity_codelist
) = load_all_codelists().values()

# Define denominator based on inclusion criteria  --------------------------------------

# was alive on the 1st January of each calendar year AND

was_alive_on_1Jan = patients.is_alive_on(INTERVAL.start_date)

# was registered with a practice on the 1st January of each calendar year AND

was_registered_on1Jan = (
    practice_registrations.for_patient_on(INTERVAL.start_date)
    .exists_for_patient()
)

# does not have a disclosive sex  

has_recorded_sex = patients.sex.is_in(["male", "female"])

# was not over 100 years of age

age = patients.age_on(INTERVAL.start_date)
not_over_100_years = age <= 100

age_band = case(
    when(age < 16).then("0-15"),
    when((age >= 16) & (age < 25)).then("16-24"),
    when((age >= 25) & (age < 35)).then("25-34"),
    when((age >= 35) & (age < 50)).then("35-49"),
    when((age >= 50) & (age < 65)).then("50-64"),
    when((age >= 65) & (age < 75)).then("65-74"),
    when((age >= 75) & (age < 85)).then("75-84"),
    when(age >= 85).then("85 plus"),
    otherwise="missing",
)

# Define numerators ----------------------------------

# Mapping of numerator names to their codelists

migrant_codelists = {
    "any_migrant": all_migrant_codes,
    "cob_migrant": cob_migrant_codes,
    "asylum_refugee_migrant": asylum_refugee_migrant_codes,
    "interpreter_migrant": interpreter_migrant_codes,
}

# Automatically generate the numerators 

numerators = {
    name: (
        clinical_events
        .where(clinical_events.snomedct_code.is_in(codelist))
        .where(clinical_events.date.is_on_or_before(INTERVAL.end_date))
        .exists_for_patient()
    )
    for name, codelist in migrant_codelists.items()
}

# Define measures -------------------------------------

## Define subgroup variables (if needed)

## Ethnicity

ethnicity = (
    clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codelist))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .snomedct_code.to_category(ethnicity_codelist)
    .when_null_then("unknown")
)

## IMD

address = addresses.for_patient_on(INTERVAL.start_date)
imd_quintile = address.imd_quintile

## Region

practice_id = (practice_registrations.for_patient_on(INTERVAL.start_date)
               .practice_pseudo_id)
region = (practice_registrations.for_patient_on(INTERVAL.start_date)
          .practice_nuts1_region_name
          .when_null_then("unknown"))

# Create subgroups dictionary

subgroups = {
    "": {},  # No grouping, just the overall measure
    "age": {"age_band": age_band},
    "sex": {"sex": patients.sex},
    "ethnicity": {"ethnicity": ethnicity},
    "imd": {"imd_quintile": imd_quintile},
    "region": {"region": region}
}

## set defaults

measures.define_defaults(
    denominator=was_alive_on_1Jan & was_registered_on1Jan & has_recorded_sex & not_over_100_years,
    intervals=years(16).starting_on("2009-01-01")
)

for key, numerator in numerators.items():
    for suffix, group in subgroups.items():
        measure_name = f"{key}" if suffix == "" else f"{key}_{suffix}"
        measures.define_measure(
            name=measure_name,
            numerator=numerator,
            group_by=group
        )



