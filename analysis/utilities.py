
# Dictionary for analysis (ehrQL expressions)
ehrql_subgroups = {
    "": {},
    "age": {"age_band": age_band},
    "sex": {"sex": patients.sex},
    "ethnicity": {"ethnicity": ethnicity},
    "imd": {"imd_quintile": imd_quintile},
    "region": {"region": region},
}

# Dictionary for plotting (column names as strings)
plot_subgroups = {
    "": [],
    "age": ["age_band"],
    "sex": ["sex"],
    "ethnicity": ["ethnicity"],
    "imd": ["imd_quintile"],
    "region": ["region"]
}