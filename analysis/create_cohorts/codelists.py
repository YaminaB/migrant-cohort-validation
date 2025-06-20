## Script to load migration-related codelists
## that can be imported to all other relevant scripts
## Author: Yamina Boukari
####

from ehrql import codelist_from_csv

all_migrant_codes = codelist_from_csv("codelists/user-YaminaB-migration-status.csv", column="code")

cob_migrant_codes = codelist_from_csv("codelists/user-YaminaB-born-outside-the-uk.csv", column="code")

asylum_refugee_migrant_codes = codelist_from_csv("codelists/user-YaminaB-asylum-seeker-or-refugee.csv", column="code")

interpreter_migrant_codes = codelist_from_csv("codelists/user-YaminaB-interpreter-required.csv", column="code")

ethnicity_codelist =  codelist_from_csv(
            "codelists/opensafely-ethnicity-snomed-0removed.csv",
            column="code",
            category_column="Label_6",
        )