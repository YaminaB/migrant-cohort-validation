## Script to generate a migration event-level dataset for migrants
## that has a row per individual per migration-related code 
## Author: Yamina Boukari
####

from ehrql import Dataset, days, years, when

from ehrql.tables.tpp import (
  clinical_events
)

from analysis.create_cohorts.codelists import all_migrant_codes

from analysis.create_cohorts.dataset_definition_full_study_cohort import dataset

# all migration-related codes 
migration_related_codes = (
  clinical_events
  .where(clinical_events.snomedct_code.is_in(all_migrant_codes))
  .sort_by(clinical_events.date)
)

dataset.add_event_table(
  "migration_related_codes",
  date=migration_related_codes.date,
  snomedct_code=migration_related_codes.snomedct_code
)