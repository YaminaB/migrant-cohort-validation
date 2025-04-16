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

measures = create_measures()

measures.configure_dummy_data(population_size=1000)
measures.configure_disclosure_control(enabled=False) # needs to be enabled when running on real data!

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
    category_column="Label_6",
)

# Define denominator based on inclusion criteria  --------------------------------------

# was alive on the 1st January of each calendar year AND

was_alive_on_1Jan = patients.is_alive_on(INTERVAL.start_date)

# was registered with a practice on the 1st January of each calendar year AND

was_registered_on1Jan = (
    practice_registrations
    .where(practice_registrations.start_date <= INTERVAL.start_date)
    .except_where(practice_registrations.end_date < INTERVAL.start_date)
    .exists_for_patient()
)

# does not have a disclosive sex AND 

has_recorded_sex = patients.sex.is_in(["male", "female"])

# was not over 100 years of age

age = patients.age_on(INTERVAL.start_date)
not_over_100_years = age <= 100

age_band = case(
    when((age >= 0) & (age < 20)).then("0-19"),
    when((age >= 20) & (age < 40)).then("20-39"),
    when((age >= 40) & (age < 60)).then("40-59"),
    when((age >= 60) & (age < 80)).then("60-79"),
    when(age >= 80).then("80+")
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
)

## IMD

imd_rounded = addresses.for_patient_on(INTERVAL.start_date).imd_rounded
max_imd = 32844
imd_quintile = case(
    when(imd_rounded < int(max_imd * 1 / 5)).then(1),
    when(imd_rounded < int(max_imd * 2 / 5)).then(2),
    when(imd_rounded < int(max_imd * 3 / 5)).then(3),
    when(imd_rounded < int(max_imd * 4 / 5)).then(4),
    when(imd_rounded <= max_imd).then(5),
)

## Region

practice_id = (practice_registrations.for_patient_on(INTERVAL.start_date)
               .practice_pseudo_id)
region = (practice_registrations.for_patient_on(INTERVAL.start_date)
          .practice_nuts1_region_name)

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


