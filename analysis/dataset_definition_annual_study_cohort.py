##########################################################################

# This is a script to create the following annual migrant cohorts with demographics:
# - Select anyone who: 
#         1) was alive on the 1st January of each calendar year AND
#         2) was registered with a practice on the 1st January of each calendar year AND
#         2) had a migration-related code at any time point before or on the 1st January of each calendar year AND
#         3) does not have a disclosive sex AND 
#         4) was not over 100 years of age
# - Add a variable to indicate the category of migration-related code 
# - Add a sex variable
# - Add ethnicity variable (using SNOMED:2022 codelist)
# - Add age on the 1st January of each calendar year 
# - Add practice region variable (or equivalent)
# - Add IMD variable 

# Author: Yamina Boukari
# Bennett Institute for Applied Data Science, University of Oxford, 2025

#############################################################################

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
