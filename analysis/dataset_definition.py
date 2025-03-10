from ehrql import create_dataset, codelist_from_csv, show
from ehrql.tables.tpp import patients, practice_registrations, clinical_events

migrant_codes = codelist_from_csv(
    "codelists/user-YaminaB-migration-status.csv", column="code")

ethnicity_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="code",
    category_column="Grouping_6",
)

# overall cohort: any migration-related code at any timepoint in the database 
# determine their first migrant code, when it was recorded, and when this was in relation to first practice registration

dataset = create_dataset()

has_migrant_code = clinical_events.where(clinical_events.snomedct_code.is_in(migrant_codes)).exists_for_patient()

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
