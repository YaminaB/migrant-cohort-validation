
import pandas as pd
import numpy as np
from ehrql import show

# create an skeleton df
dummy_data = pd.DataFrame({'patient_id': range(1, 1001)})
dummy_data[['date_of_first_migration_code', 'number_of_migration_codes',
            'sex', 'has_cob_migrant_code', 'has_asylum_or_refugee_migrant_code',
            'has_interpreter_migrant_code', 'date_of_first_practice_registration',
            'time_to_first_migration_code', 'latest_ethnicity_code', 'latest_ethnicity_group',
            'year_of_birth', 'mso_code', 'imd_decile', 'imd_quintile', 'TPP_death_date', 'ons_death_date']] = np.nan

print(dummy_data)

# generate ethnicities variable based on Pathak et al. CPRD GOLD migrant cohort characteristics 

ethnicities = ["White British", "White Non-British", "Mixed", "Asian/Asian British", "Black/African/Caribbean/Black British", "Other", "Unknown"]
ethnicity_probabilities = [0.0152, 0.343, 0.0273, 0.267, 0.0919, 0.0779, 0.178] # don't add up to 1 so need to normalise them
ethnicity_probabilities = np.array(ethnicity_probabilities) / np.sum(ethnicity_probabilities)
dummy_data['latest_ethnicity_group'] = np.random.choice(ethnicities, size = len(dummy_data), p = ethnicity_probabilities)

# generate sex based on Pathak et al. 

sex = ["Male", "Female"]
sex_probabilities = [0.463, 0.537]
dummy_data['sex'] = np.random.choice(sex, size = len(dummy_data), p =sex_probabilities)

show(dummy_data)

# generate column indicating migrant status

