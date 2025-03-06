from ehrql import create_dataset, codelist_from_csv, show
from ehrql.tables.tpp import patients, practice_registrations, clinical_events

migrant_codes = codelist_from_csv(
    "codelists/user-YaminaB-migration-status.csv", column="code")

dataset = create_dataset()

#index_date = "2020-03-31"

#has_registration = practice_registrations.for_patient_on(
#    index_date
#).exists_for_patient()

has_migrant_code = clinical_events.where(clinical_events.snomedct_code.is_in(migrant_codes)).exists_for_patient()

show(has_migrant_code)

dataset.define_population(has_migrant_code)

dataset.sex = patients.sex
