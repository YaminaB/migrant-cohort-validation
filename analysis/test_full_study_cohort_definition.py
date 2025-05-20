from datetime import date
from dataset_definition_full_study_cohort import dataset

test_data = {
    # Expected in population 
    1:{
        "patients": {
            "date_of_birth": date(1999, 1, 1),
            "sex": "male",
            "date_of_death": None},
        "practice_registrations": [
            {
            "end_date": date(2023, 1, 1),
            "start_date": date(2003, 1, 1)
            }
        ],
        "clinical_events": [
            {
                # First migration code
                "date": date(2010, 1, 1),
                "snomedct_code": "1047291000000109"
            },
            {
                # Latest ethnicity code
                "date": date(2015, 1,1 ),
                "snomedct_code":  "10292001"
            }
        ],
        "addresses": [
            {
                "start_date": date(2020, 1, 1),
                "end_date": date(2023, 1, 1),
                "msoa_code": "E02000864"
            }
        ], 
        "ons_deaths": {
            "date": None
        },
        "expected_in_population": True,
        "expected_columns": {
            "date_of_first_migration_code": date(2010, 1, 1),
            "number_of_migration_codes": 1,
            "sex": "male",
            "has_cob_migrant_code": False,
            "has_asylum_or_refugee_migrant_code": False,
            "has_interpreter_migrant_code": False,
            "date_of_first_practice_registration": date(2003, 1, 1),
            "time_to_first_migration_code": 2557,
            "latest_ethnicity_code": "10292001",
            "latest_ethnicity_group": "Chinese or Other Ethnic Groups",
            "year_of_birth": 1999,
            "msoa_code": "E02000864",
            "TPP_death_date": None,
            "ons_death_date": None
        }  
    },
    # Not expected in population (disclosive sex)
    2:{
        "patients": {
            "date_of_birth": date(1999, 1, 1),
            "sex": "intersex",
            "date_of_death": None},
        "practice_registrations": [
            {
            "end_date": date(2023, 1, 1),
            "start_date": date(2003, 1, 1)
            }
        ],
        "clinical_events": [
            {
                # First migration code
                "date": date(2010, 1, 1),
                "snomedct_code": "1047291000000109"
            },
            {
                # Latest ethnicity code
                "date": date(2015, 1,1 ),
                "snomedct_code":  "10292001"
            }
        ],
        "addresses": [
            {
                "start_date": date(2020, 1, 1),
                "end_date": date(2023, 1, 1),
                "msoa_code": "E02000864"
            }
        ], 
        "ons_deaths": {
            "date": None
        },
        "expected_in_population": False,
        "expected_columns": {
            "date_of_first_migration_code": date(2010, 1, 1),
            "number_of_migration_codes": 1,
            "sex": "intersex",
            "has_cob_migrant_code": False,
            "has_asylum_or_refugee_migrant_code": False,
            "has_interpreter_migrant_code": False,
            "date_of_first_practice_registration": date(2003, 1, 1),
            "time_to_first_migration_code": 2557,
            "latest_ethnicity_code": "10292001",
            "latest_ethnicity_group": "Chinese or Other Ethnic Groups",
            "year_of_birth": 1999,
            "msoa_code": "E02000864",
            "TPP_death_date": None,
            "ons_death_date": None
            }
    }
}